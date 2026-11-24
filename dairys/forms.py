from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from companies.forms import OrganizationSelectionMixin

from .models import DairyConsultation, DairyProduct, DairyService, TrainingEnrollment


class DairyLivestockForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyProduct
        fields = (
            "name",
            "livestock_type",
            "breed",
            "description",
            "price",
            "age_months",
            "lactation_status",
            "daily_milk_yield",
            "quantity_available",
            "unit",
            "location",
            "main_image",
            "company",
            "farm",
        )
        labels = {
            "name": _("Listing title"),
            "livestock_type": _("Animal type"),
            "age_months": _("Age (months)"),
            "daily_milk_yield": _("Average daily milk yield (liters)"),
            "quantity_available": _("Number available"),
            "unit": _("Availability unit"),
            "main_image": _("Livestock photo"),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "age_months": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "daily_milk_yield": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "quantity_available": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "main_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields["livestock_type"].required = True
        self.fields["description"].help_text = _(
            "Include health, temperament, and other details buyers should know."
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "livestock-create__control",
            )

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class DairyProductForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyProduct
        fields = (
            "name",
            "description",
            "price",
            "subcategory",
            "milk_source",
            "milk_unit",
            "unit",
            "quantity_available",
            "location",
            "collection_date",
            "main_image",
            "company",
            "farm",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "quantity_available": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "collection_date": forms.DateInput(attrs={"type": "date"}),
            "main_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "form-select" if isinstance(field.widget, forms.Select) else "form-control",
            )

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class DairyItemForm(OrganizationSelectionMixin, forms.ModelForm):
    class Meta:
        model = DairyProduct
        fields = (
            "name",
            "item_group",
            "subcategory",
            "description",
            "price",
            "unit",
            "quantity_available",
            "location",
            "main_image",
            "company",
            "farm",
        )
        labels = {
            "name": _("Listing title"),
            "item_group": _("Item category"),
            "subcategory": _("Item type or model"),
            "price": _("Price (ETB)"),
            "quantity_available": _("Quantity available"),
            "main_image": _("Item photo"),
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": _("Describe the item's condition, specifications, and included accessories."),
                }
            ),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "quantity_available": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "main_image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields["item_group"].required = True
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "dairy-item-create__control")

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class DairyServiceForm(forms.ModelForm):
    class Meta:
        model = DairyService
        fields = (
            "name",
            "service_type",
            "description",
            "schedule",
            "location",
            "service_area",
            "availability",
            "price",
        )
        labels = {
            "name": _("Professional display name"),
            "service_type": _("Area of expertise"),
            "description": _("About your consulting service"),
            "schedule": _("Consultation method or schedule"),
            "location": _("Clinic or base location"),
            "service_area": _("Areas you serve"),
            "availability": _("Availability"),
            "price": _("Consultation fee (ETB)"),
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": "2000",
                    "placeholder": _("Describe your experience and how you can help dairy farmers."),
                }
            ),
            "schedule": forms.TextInput(
                attrs={"placeholder": _("e.g. Farm visits and video calls")}
            ),
            "location": forms.TextInput(
                attrs={"placeholder": _("Town, clinic, or base")}
            ),
            "service_area": forms.TextInput(
                attrs={"placeholder": _("e.g. Addis Ababa and nearby areas")}
            ),
            "availability": forms.TextInput(
                attrs={"placeholder": _("e.g. Weekdays, 9:00–17:00")}
            ),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_type"].choices = [
            (value, label)
            for value, label in DairyService.SERVICE_TYPE_CHOICES
            if value in DairyService.CONSULTING_SERVICE_TYPE_VALUES
        ]
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "consultancy-form__control",
            )

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class DairyTrainingForm(forms.ModelForm):
    class Meta:
        model = DairyService
        fields = (
            "name",
            "service_type",
            "description",
            "training_format",
            "training_date",
            "duration_hours",
            "schedule",
            "location",
            "service_area",
            "availability",
            "price",
        )
        labels = {
            "name": _("Course title"),
            "service_type": _("Training topic"),
            "description": _("Course description"),
            "training_format": _("Training format"),
            "training_date": _("Training date"),
            "duration_hours": _("Duration (hours)"),
            "schedule": _("Schedule or session times"),
            "location": _("Training location"),
            "service_area": _("Areas served"),
            "availability": _("Available places or enrollment details"),
            "price": _("Course fee (ETB)"),
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5, "maxlength": "2000"}
            ),
            "training_date": forms.DateInput(attrs={"type": "date"}),
            "duration_hours": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_type"].choices = [
            (value, label)
            for value, label in DairyService.SERVICE_TYPE_CHOICES
            if value in DairyService.TRAINING_SERVICE_TYPE_VALUES
        ]
        self.fields["training_format"].required = True
        self.fields["training_date"].required = True
        self.fields["duration_hours"].required = True
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "training-form__control")

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_training_date(self):
        training_date = self.cleaned_data["training_date"]
        if training_date < timezone.localdate():
            raise forms.ValidationError(_("Choose today or a future date."))
        return training_date


class DairyTrainingEnrollmentForm(forms.ModelForm):
    class Meta:
        model = TrainingEnrollment
        fields = ("name", "email", "phone")
        labels = {
            "name": _("Your name"),
            "email": _("Email address"),
            "phone": _("Phone number"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TelInput(attrs={"autocomplete": "tel"}),
        }

    def __init__(self, *args, training, trainee, **kwargs):
        self.training = training
        self.trainee = trainee
        initial = kwargs.get("initial") or {}
        initial.setdefault("name", trainee.username)
        initial.setdefault("email", trainee.email or "")
        initial.setdefault("phone", trainee.phone_number)
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "training-form__control")

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def clean(self):
        cleaned_data = super().clean()
        if TrainingEnrollment.objects.filter(
            training=self.training,
            trainee=self.trainee,
        ).exists():
            raise forms.ValidationError(
                _("You are already registered for this training.")
            )
        return cleaned_data


class DairyConsultationForm(forms.ModelForm):
    class Meta:
        model = DairyConsultation
        fields = ("name", "email", "phone", "preferred_date", "message")
        labels = {
            "name": _("Your name"),
            "email": _("Email address"),
            "phone": _("Phone number"),
            "preferred_date": _("Preferred date"),
            "message": _("Tell the consultant what you need"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TelInput(attrs={"autocomplete": "tel"}),
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": "2000",
                    "placeholder": _("Share a few details about your herd or question."),
                }
            ),
        }

    def __init__(self, *args, customer=None, **kwargs):
        self.customer = customer
        initial = kwargs.get("initial") or {}
        kwargs["initial"] = initial
        if customer and customer.is_authenticated:
            initial.setdefault("name", customer.username)
            initial.setdefault("email", customer.email or "")
            initial.setdefault("phone", customer.phone_number)
        super().__init__(*args, **kwargs)
        self.fields["preferred_date"].widget.attrs["min"] = timezone.localdate().isoformat()
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "consultancy-form__control",
            )

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]
        if preferred_date < timezone.localdate():
            raise forms.ValidationError(_("Choose today or a future date."))
        return preferred_date