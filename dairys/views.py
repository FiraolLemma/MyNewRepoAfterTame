from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .forms import DairyProductForm, DairyServiceForm
from .models import DairyCategory, DairyProduct, DairyService
from users.roles import UserRole, role_required


class DairyMarketView(ListView):
    model = DairyProduct
    template_name = "dairys/dairy_market.html"
    context_object_name = "dairy_products"
    paginate_by = 24

    def get_queryset(self):
        products = DairyProduct.objects.select_related(
            "category", "created_by"
        ).filter(quantity_available__gt=0)
        query = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        if query:
            products = products.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(location__icontains=query)
                | Q(category__name__icontains=query)
            )
        if category:
            products = products.filter(category__slug=category)
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        services = DairyService.objects.select_related("provider").filter(
            is_available=True
        )
        if query:
            services = services.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(location__icontains=query)
                | Q(service_type__icontains=query)
            )
        context.update(
            {
                "dairy_services": services,
                "categories": DairyCategory.objects.all(),
                "query": query,
                "selected_category": self.request.GET.get("category", ""),
            }
        )
        return context


def _unique_slug(model, name, current=None):
    base_slug = slugify(name) or "farm-listing"
    slug = base_slug
    suffix = 2
    queryset = model.objects.all()
    if current is not None:
        queryset = queryset.exclude(pk=current.pk)
    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


def _owned_queryset(model, user):
    queryset = model.objects.all()
    return queryset if (
        (user.is_staff or user.is_superuser) and not user.is_virtual_user
    ) else queryset.filter(
        **{"created_by" if model is DairyProduct else "provider": user}
    )


def dairy_product_detail(request, slug):
    product = get_object_or_404(
        DairyProduct.objects.select_related("category", "created_by"),
        slug=slug,
    )
    return render(request, "dairys/dairyproduct_detail.html", {"product": product})


def dairy_service_detail(request, slug):
    service = get_object_or_404(
        DairyService.objects.select_related("provider"),
        slug=slug,
    )
    return render(request, "dairys/dairyservice_detail.html", {"service": service})


@role_required(UserRole.FARMER, UserRole.SUPPLIER)
def dairy_product_create(request):
    form = DairyProductForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
    )
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.created_by = request.user
        product.slug = _unique_slug(DairyProduct, product.name)
        product.save()
        messages.success(request, "Your dairy product has been listed.")
        return redirect(product.get_absolute_url())
    return render(
        request,
        "dairys/dairyproduct_form.html",
        {"form": form, "form_title": "List a dairy product"},
    )


@login_required
def dairy_product_update(request, slug):
    product = get_object_or_404(_owned_queryset(DairyProduct, request.user), slug=slug)
    form = DairyProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
        user=request.user,
    )
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.slug = _unique_slug(DairyProduct, product.name, current=product)
        product.save()
        messages.success(request, "Your dairy product has been updated.")
        return redirect(product.get_absolute_url())
    return render(
        request,
        "dairys/dairyproduct_form.html",
        {"form": form, "form_title": "Update dairy product", "product": product},
    )


@login_required
def dairy_product_delete(request, slug):
    product = get_object_or_404(_owned_queryset(DairyProduct, request.user), slug=slug)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Your dairy product has been removed.")
        return redirect("clothings:clothing_list")
    return render(
        request,
        "dairys/dairyproduct_confirm_delete.html",
        {"product": product},
    )


@role_required(
    UserRole.FARMER,
    UserRole.SERVICE_PROVIDER,
    UserRole.VETERINARIAN,
)
def dairy_service_create(request):
    form = DairyServiceForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        service = form.save(commit=False)
        service.provider = request.user
        service.slug = _unique_slug(DairyService, service.name)
        service.save()
        messages.success(request, "Your dairy farm service has been listed.")
        return redirect(service.get_absolute_url())
    return render(
        request,
        "dairys/dairyservice_form.html",
        {"form": form, "form_title": "Offer a dairy farm service"},
    )


@login_required
def dairy_service_update(request, slug):
    service = get_object_or_404(_owned_queryset(DairyService, request.user), slug=slug)
    form = DairyServiceForm(request.POST or None, instance=service, user=request.user)
    if request.method == "POST" and form.is_valid():
        service = form.save(commit=False)
        service.slug = _unique_slug(DairyService, service.name, current=service)
        service.save()
        messages.success(request, "Your dairy farm service has been updated.")
        return redirect(service.get_absolute_url())
    return render(
        request,
        "dairys/dairyservice_form.html",
        {"form": form, "form_title": "Update dairy farm service", "service": service},
    )


@login_required
def dairy_service_delete(request, slug):
    service = get_object_or_404(_owned_queryset(DairyService, request.user), slug=slug)
    if request.method == "POST":
        service.delete()
        messages.success(request, "Your dairy farm service has been removed.")
        return redirect("clothings:clothing_list")
    return render(
        request,
        "dairys/dairyservice_confirm_delete.html",
        {"service": service},
    )


@require_POST
@login_required
def like_dairy_product(request, product_id):
    product = get_object_or_404(DairyProduct, pk=product_id)
    return JsonResponse({"status": "success", "like_count": product.toggle_like(request.user)})


@require_POST
@login_required
def share_dairy_product(_request, product_id):
    product = get_object_or_404(DairyProduct, pk=product_id)
    return JsonResponse({"status": "success", "share_count": product.increment_shares()})
