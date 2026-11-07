# poultrys/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from .models import Item, SubImage
from .forms import ItemForm
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from cart.models import CartItem
from cart.views import _get_cart
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import json
from .models import Consultant, ConsultationService, ConsultationBooking
from .forms import ConsultationBookingForm
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import EggSeller, EggOrder
from .forms import EggSellerForm, EggOrderForm, EggSellerFilterForm
from django.contrib.auth.decorators import login_required
from .models import ChickenSeller
from .forms import ChickenSellerForm
from django.shortcuts import render, redirect
from .forms import TrainingEnrollmentForm
from django.contrib import messages
from .models import TrainingEnrollment
from django.utils.decorators import method_decorator
from decimal import Decimal, InvalidOperation
from companies.models import Farm
from users.roles import UserRole, role_required

@require_POST
@login_required
def like_item(request, pk):
    try:
        item = get_object_or_404(Item, pk=pk)
        new_count = item.toggle_like(request.user)
        has_liked = item.liked_by.filter(pk=request.user.pk).exists()
        return JsonResponse({
            'status': 'success',
            'like_count': new_count,
            'has_liked': has_liked,
            'item_id': pk
        })
    except Item.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
@require_POST
def share_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.share_count += 1
    item.save()
    return JsonResponse({'shares': item.share_count})

@login_required
@require_POST
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    cart = _get_cart(request)
    item_ct = ContentType.objects.get_for_model(Item)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        content_type=item_ct,
        object_id=item.id
    )

    if created:
        message = "Item added to cart."
    else:
        message = "Item is already in the cart."

    return JsonResponse({'status': 'success', 'message': message})

def index(request):

    featured_products = Item.objects.all().order_by('-created_at')[:3] 
    context = {
        'featured_products': featured_products
    }
    return render(request, 'poultrys/index.html', context)

class ItemListView(ListView):
    model = Item
    template_name = 'poultrys/item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    ordering = ['-created_at']

    def get_queryset(self):
        return Item.objects.filter(is_featured=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = context['items']

        cart = _get_cart(self.request)
        item_ct = ContentType.objects.get_for_model(Item)
        cart_item_ids = CartItem.objects.filter(
            cart=cart,
            content_type=item_ct,
            object_id__in=items.values_list('id', flat=True)
        ).values_list('object_id', flat=True)

        liked_item_ids = []
        if self.request.user.is_authenticated:
            liked_item_ids = self.request.user.liked_items.values_list('id', flat=True)

        for item in items:
            item.is_carted = item.id in cart_item_ids
            item.has_liked = item.id in liked_item_ids

        return context

class ItemDetailView(DetailView):
    model = Item
    template_name = 'poultrys/item_detail.html'
    context_object_name = 'item'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object
        context['app_label'] = item._meta.app_label
        context['model_name'] = item._meta.model_name
        context['related_items'] = Item.objects.filter(category=item.category).exclude(id=item.id)[:4]
        cart = _get_cart(self.request)
        item_ct = ContentType.objects.get_for_model(Item)
        user = self.request.user
        context['has_liked'] = (
            user.is_authenticated
            and item.liked_by.filter(pk=user.pk).exists()
        )

        return context
    
class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'poultrys/item_create.html'
    success_message = "Item was created successfully!"
    login_url = 'login'

    @method_decorator(role_required(UserRole.FARMER, UserRole.SUPPLIER))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.created_by = self.request.user
        
        item = form.save()
        
        for img in self.request.FILES.getlist('sub_images'):
            SubImage.objects.create(item=item, image=img)
        messages.success(self.request, self.success_message)
        return redirect('poultrys:item_detail', pk=item.pk)

@login_required
def item_edit(request, pk):
    items = Item.objects.all() if request.user.is_staff else Item.objects.filter(created_by=request.user)
    item = get_object_or_404(items, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('poultrys:item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item, user=request.user)
    return render(request, 'poultrys/item_create.html', {'form': form})

@login_required
@require_POST
def item_delete(request, pk):
    items = Item.objects.all() if request.user.is_staff else Item.objects.filter(created_by=request.user)
    item = get_object_or_404(items, pk=pk)
    item.delete()
    return redirect('poultrys:item_list')

def chicken_sellers(request):
    return render(request, 'poultrys/chicken_sellers.html')


def veterinary_consultancy(request):
    consultants = Consultant.objects.filter(is_available=True).prefetch_related('services')
    form = ConsultationBookingForm()

    context = {
        'consultants': consultants,
        'form': form,
    }
    return render(request, 'poultrys/veterinary_consultancy.html', context)

@require_POST
def book_consultation(request):
    data = _json_request_data(request)
    if data is None:
        return JsonResponse(
            {'success': False, 'message': _('Invalid request data.')},
            status=400,
        )

    try:
        consultant = Consultant.objects.get(
            id=data.get('consultant_id'),
            is_available=True,
        )
    except Consultant.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': _('Consultant not found.')},
            status=404,
        )

    try:
        service = ConsultationService.objects.get(
            id=data.get('service_id'),
            consultant=consultant,
        )
    except ConsultationService.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': _('Service not found.')},
            status=404,
        )

    form = ConsultationBookingForm({
        'consultant': consultant.id,
        'service': service.id,
        'user_name': data.get('user_name'),
        'user_email': data.get('user_email'),
        'user_phone': data.get('user_phone'),
        'preferred_date': data.get('preferred_date'),
        'preferred_time': data.get('preferred_time'),
        'message': data.get('message'),
    })
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'errors': form.errors},
            status=400,
        )

    booking = form.save(commit=False)
    if request.user.is_authenticated:
        booking.customer = request.user
    booking.save()
    return JsonResponse({
        'success': True,
        'message': _('Your consultation request has been submitted successfully! We will contact you shortly.'),
    })

# eggs for sell
def egg_sellers(request):
    sellers = EggSeller.objects.filter(is_active=True).select_related('user__profile')
    form = EggSellerFilterForm(request.GET or None)
    
    if form.is_valid():
        egg_type = form.cleaned_data.get('egg_type')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        certified_only = form.cleaned_data.get('certified_only')
        
        if egg_type:
            sellers = sellers.filter(egg_type=egg_type)
        if city:
            sellers = sellers.filter(city__icontains=city)
        if min_price:
            sellers = sellers.filter(price_per_dozen__gte=min_price)
        if max_price:
            sellers = sellers.filter(price_per_dozen__lte=max_price)
        if certified_only:
            sellers = sellers.filter(~Q(certification='none'))
    
    sellers = sellers.order_by('-is_verified', '-rating')
    
    context = {
        'sellers': sellers,
        'filter_form': form,
    }
    return render(request, 'poultrys/egg_sellers.html', context)

@require_POST
def place_egg_order(request):
    data = _json_request_data(request)
    if data is None:
        return JsonResponse(
            {'success': False, 'message': _('Invalid request data.')},
            status=400,
        )

    try:
        seller = EggSeller.objects.get(id=data.get('seller_id'), is_active=True)
    except EggSeller.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': _('Seller not found.')},
            status=404,
        )

    form = EggOrderForm({
        'customer_name': data.get('customer_name'),
        'customer_email': data.get('customer_email'),
        'customer_phone': data.get('customer_phone'),
        'customer_address': data.get('customer_address'),
        'quantity': data.get('quantity'),
        'preferred_delivery_date': data.get('preferred_delivery_date'),
        'special_instructions': data.get('special_instructions'),
    })
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'errors': form.errors},
            status=400,
        )

    order = form.save(commit=False)
    order.seller = seller
    if request.user.is_authenticated:
        order.customer = request.user
    order.total_price = form.cleaned_data['quantity'] * seller.price_per_dozen
    order.save()
    return JsonResponse({
        'success': True,
        'message': _('Your order has been placed successfully! The seller will contact you soon.'),
        'order_id': order.id,
    })


def _json_request_data(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


@role_required(UserRole.FARMER, UserRole.SUPPLIER)
def add_egg_seller(request):
    
    if hasattr(request.user, 'egg_seller'):
        messages.error(request, _('You already have an egg seller profile!'))
        return redirect('poultrys:egg_sellers')
    
    if request.method == 'POST':
        form = EggSellerForm(request.POST, user=request.user)
        if form.is_valid():
            egg_seller = form.save(commit=False)
            egg_seller.user = request.user
            farm = Farm.objects.get_or_create(
                owner=request.user,
                name=egg_seller.farm_name,
                defaults={
                    "city": egg_seller.city,
                    "region": egg_seller.state,
                    "country": egg_seller.country,
                    "address": egg_seller.address,
                    "phone": egg_seller.phone,
                    "email": egg_seller.email,
                },
            )[0]
            egg_seller.farm = farm
            egg_seller.save()
            messages.success(request, _('Egg seller added successfully!'))
            return redirect('poultrys:egg_sellers')
    else:
        form = EggSellerForm(user=request.user)
    
    return render(request, 'poultrys/add_egg_seller.html', {'form': form})

@role_required(UserRole.FARMER, UserRole.SUPPLIER)
def edit_egg_seller(request, pk):
    seller = get_object_or_404(
        EggSeller.objects.filter(user=request.user) if not request.user.is_staff else EggSeller.objects.all(),
        pk=pk,
    )
    if request.method == 'POST':
        form = EggSellerForm(request.POST, instance=seller, user=seller.user)
        if form.is_valid():
            egg_seller = form.save(commit=False)
            # For safety, ensure the user remains the same (though it shouldn't change)
            egg_seller.user = seller.user  # Keep the original user
            egg_seller.save()
            messages.success(request, _('Egg seller updated successfully!'))
            return redirect('poultrys:egg_sellers')
    else:
        form = EggSellerForm(instance=seller, user=seller.user)
    
    return render(request, 'poultrys/edit_egg_seller.html', {'form': form, 'seller': seller})

@login_required
def egg_seller_orders(request):
    seller = get_object_or_404(EggSeller, user=request.user)
    orders = EggOrder.objects.filter(seller=seller).order_by('-order_date')

    # Optional: sanitize problematic decimal fields
    valid_orders = []
    for order in orders:
        try:
            # Force conversion to Decimal to catch errors
            if order.total_price is not None:
                Decimal(order.total_price)
            if order.quantity is not None:
                Decimal(order.quantity)
            valid_orders.append(order)
        except InvalidOperation:
            print(f"Problematic order: {order.id}")
            continue

    return render(request, 'poultrys/egg_seller_orders.html', {'orders': valid_orders})



def chicken_sellers_list(request):
    sellers = ChickenSeller.objects.filter(is_active=True)
    
    location_filter = request.GET.get('location', '')
    search_query = request.GET.get('search', '')
    
    if location_filter:
        sellers = sellers.filter(location__icontains=location_filter)
    
    if search_query:
        sellers = sellers.filter(
            Q(farm_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(breeds__icontains=search_query)
        )
    
    locations = ChickenSeller.objects.filter(is_active=True).values_list('location', flat=True).distinct()
    
    context = {
        'sellers': sellers,
        'locations': locations,
        'selected_location': location_filter,
        'search_query': search_query,
    }
    
    return render(request, 'poultrys/chicken_sellers.html', context)

def chicken_seller_detail(request, seller_id):
    seller = get_object_or_404(ChickenSeller, id=seller_id, is_active=True)
    return render(request, 'poultrys/chicken_seller_detail.html', {'seller': seller})

@role_required(UserRole.FARMER)
def register_seller(request):
    current_seller = request.user.chicken_seller if hasattr(request.user, 'chicken_seller') else None
    if current_seller and current_seller.is_active:
        messages.info(request, 'You already have an active seller profile.')
        return redirect('poultrys:chicken_sellers_list')
    
    if request.method == 'POST':
        form = ChickenSellerForm(request.POST, instance=current_seller)
        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            farm, _ = Farm.objects.get_or_create(
                owner=request.user,
                name=seller.farm_name,
                defaults={
                    "city": seller.location,
                    "phone": seller.contact_number,
                    "email": seller.email,
                },
            )
            seller.farm = farm
            seller.save()
            messages.success(request, 'Chicken seller created successfully!')
            return redirect('poultrys:chicken_sellers_list')
    else:
        form = ChickenSellerForm(instance=current_seller)
      
    return render(request, 'poultrys/register_seller.html', {'form': form})

@role_required(UserRole.FARMER, UserRole.SUPPLIER)
def edit_seller(request, seller_id):
    sellers = ChickenSeller.objects.filter(is_active=True)
    if not request.user.is_staff:
        sellers = sellers.filter(user=request.user)
    seller = get_object_or_404(sellers, id=seller_id)
    
    if request.method == 'POST':
        form = ChickenSellerForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('poultrys:chicken_sellers_list')
    else:
        form = ChickenSellerForm(instance=seller)
    
    return render(request, 'poultrys/edit_seller.html', {
        'form': form,
        'seller': seller
    })

@role_required(UserRole.FARMER, UserRole.SUPPLIER)
def delete_seller(request, seller_id):
    sellers = ChickenSeller.objects.filter(is_active=True)
    if not request.user.is_staff:
        sellers = sellers.filter(user=request.user)
    seller = get_object_or_404(sellers, id=seller_id)
    
    if request.method == 'POST':
        seller.is_active = False
        seller.save()
        messages.success(request, 'Seller profile deleted successfully!')
        return redirect('poultrys:chicken_sellers_list')
    
    return render(request, 'poultrys/delete_seller.html', {'seller': seller})

@role_required(UserRole.FARMER, UserRole.SUPPLIER)
@require_POST
def delete_seller_ajax(request, seller_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse(
            {'success': False, 'error': 'Invalid request.'},
            status=400,
        )
    sellers = ChickenSeller.objects.filter(is_active=True)
    if not request.user.is_staff:
        sellers = sellers.filter(user=request.user)
    seller = get_object_or_404(sellers, id=seller_id)
    seller.is_active = False
    seller.save(update_fields=('is_active',))
    return JsonResponse({'success': True})


@role_required(UserRole.FARMER, UserRole.SUPPLIER)
@require_POST
def delete_egg_seller_ajax(request, pk):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse(
            {'success': False, 'error': 'Invalid request.'},
            status=400,
        )
    sellers = EggSeller.objects.all()
    if not request.user.is_staff:
        sellers = sellers.filter(user=request.user)
    seller = get_object_or_404(sellers, pk=pk)
    seller_name = seller.farm_name
    seller.delete()
    return JsonResponse({
        'success': True,
        'message': f'{seller_name} has been deleted successfully!',
    })

def poultry_trainings(request):
    if request.method == 'POST':
        form = TrainingEnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Enrollment successful! We will contact you soon.")
            return redirect('poultrys:poultry_trainings')
    else:
        form = TrainingEnrollmentForm()
    return render(request, 'poultrys/poultry_trainings.html', {'form': form})

@login_required
def poultry_trainees(request):
    trainees = TrainingEnrollment.objects.all().order_by('-created_at')
    return render(request, 'poultrys/poultry_trainees.html', {'trainees': trainees})
