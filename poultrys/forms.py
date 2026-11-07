# poultrys/forms.py
from django import forms
from .models import Item, SubImage
from companies.forms import OrganizationSelectionMixin
from django.utils.translation import gettext_lazy as _
from .models import ConsultationBooking, Consultant, ConsultationService
from .models import EggSeller, EggOrder
from .models import ChickenSeller
from django import forms
from .models import TrainingEnrollment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ItemForm(OrganizationSelectionMixin, forms.ModelForm):
    sub_images = MultipleFileField(required=False, label='Additional Images')

    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'main_image', 'company', 'farm']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields['main_image'].required = True
        self.fields['main_image'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_images'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Upload additional images',
        })

    def save(self, commit=True):
        item = super().save(commit=commit)
        
        if commit and self.files.getlist('sub_images'):
            for img in self.files.getlist('sub_images'):
                SubImage.objects.create(item=item, image=img) 
        
        return item


# consultancy forms

class ConsultationBookingForm(forms.ModelForm):
    consultant = forms.ModelChoiceField(
        queryset=Consultant.objects.filter(is_available=True),
        widget=forms.HiddenInput(),
        required=False
    )
    service = forms.ModelChoiceField(
        queryset=ConsultationService.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = ConsultationBooking
        fields = [
            'consultant', 'service', 'user_name', 'user_email', 'user_phone',
            'preferred_date', 'preferred_time', 'message'
        ]
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Briefly describe your issue or questions...')}),
        }
        labels = {
            'user_name': _('Your Name'),
            'user_email': _('Email'),
            'user_phone': _('Phone'),
            'preferred_date': _('Preferred Date'),
            'preferred_time': _('Preferred Time'),
            'message': _('Message'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        consultant = cleaned_data.get('consultant')
        service = cleaned_data.get('service')
        if consultant and service and service.consultant_id != consultant.pk:
            self.add_error('service', _('The selected service does not belong to this consultant.'))
        return cleaned_data

# eggs for sell forms

class EggSellerForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = EggSeller
        fields = [
            'farm_name', 'description', 'city', 'state', 'country',
            'address', 'egg_type', 'certification', 'quantity_available',
            'price_per_dozen', 'min_order_quantity', 'website',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Describe your farm and eggs...')}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Full address for deliveries...')}),
        }

    def save(self, commit=True):
        seller = super().save(commit=False)
        seller.owner_name = self.user.username
        seller.phone = self.user.phone_number
        seller.email = self.user.email or ''
        if commit:
            seller.save()
            self.save_m2m()
        return seller

class EggOrderForm(forms.ModelForm):
    class Meta:
        model = EggOrder
        fields = ['customer_name', 'customer_email', 'customer_phone', 'customer_address', 
                 'quantity', 'preferred_delivery_date', 'special_instructions']
        widgets = {
            'customer_address': forms.Textarea(attrs={'rows': 3}),
            'special_instructions': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Any special delivery instructions...')}),
            'preferred_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'customer_name': _('Your Name'),
            'customer_email': _('Email Address'),
            'customer_phone': _('Phone Number'),
            'customer_address': _('Delivery Address'),
            'quantity': _('Quantity (dozens)'),
            'preferred_delivery_date': _('Preferred Delivery Date'),
            'special_instructions': _('Special Instructions'),
        }

class EggSellerFilterForm(forms.Form):
    egg_type = forms.ChoiceField(
        choices=[('', _('All Types'))] + list(EggSeller.EggType.choices),
        required=False,
        label=_('Egg Type')
    )
    city = forms.CharField(required=False, label=_('City'))
    min_price = forms.DecimalField(required=False, label=_('Min Price'), max_digits=6, decimal_places=2)
    max_price = forms.DecimalField(required=False, label=_('Max Price'), max_digits=6, decimal_places=2)
    certified_only = forms.BooleanField(required=False, label=_('Certified Only'))

# chicken for sell

class ChickenSellerForm(forms.ModelForm):
    class Meta:
        model = ChickenSeller
        fields = [
            'farm_name', 'location', 'available_quantity', 
            'min_price', 'max_price', 'breeds', 'description',
            'delivery_available', 'vaccinated', 'contact_number',
            'email', 'facebook_url', 'telegram_handle', 
            'whatsapp_number', 'instagram_handle', 'youtube_channel'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'farm_name': _('Farm Name'),
            'location': _('Location'),
            'available_quantity': _('Available Chickens'),
            'min_price': _('Minimum Price'),
            'max_price': _('Maximum Price'),
            'breeds': _('Breeds (comma separated)'),
            'description': _('Description'),
            'delivery_available': _('Delivery Available'),
            'vaccinated': _('Vaccinated'),
            'contact_number': _('Contact Number'),
            'email': _('Email'),
            'facebook_url': _('Facebook URL'),
            'telegram_handle': _('Telegram Handle'),
            'whatsapp_number': _('WhatsApp Number'),
            'instagram_handle': _('Instagram Handle'),
            'youtube_channel': _('YouTube Channel'),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(_("Minimum price cannot be greater than maximum price."))
        
        return cleaned_data


class TrainingEnrollmentForm(forms.ModelForm):
    class Meta:
        model = TrainingEnrollment
        fields = ['name', 'email', 'phone', 'program']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'program': forms.Select(attrs={'class': 'form-control'}),
        }
