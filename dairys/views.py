from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView

from users.roles import UserRole, role_required
from django.utils.decorators import method_decorator

from .forms import (
    DairyConsultationForm,
    DairyProductForm,
    DairyServiceForm,
    TrainingEnrollmentForm,
)
from .models import (
    DairyCategory,
    DairyConsultation,
    DairyProduct,
    DairyService,
    ensure_product_categories,
)
from .forms import PRODUCT_MAIN_CATEGORIES, SERVICE_TYPES_BY_KIND


def index(request):
    ensure_product_categories()
    return render(request, "dairys/index.html", {
        "featured_products": DairyProduct.objects.filter(is_featured=True)[:6],
        "featured_services": DairyService.objects.filter(is_featured=True, is_available=True)[:4],
    })


class MarketplaceView(ListView):
    model = DairyProduct
    template_name = "dairys/item_list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        ensure_product_categories()
        queryset = DairyProduct.objects.select_related("category").all()
        main_category = self.request.GET.get("main_category") or self.kwargs.get("default_main_category", "")
        category = self.request.GET.get("category")
        subcategory = self.request.GET.get("subcategory")
        item_group = self.request.GET.get("item_group")
        search = self.request.GET.get("q")
        if main_category in PRODUCT_MAIN_CATEGORIES:
            queryset = queryset.filter(main_category=main_category)
        if category:
            queryset = queryset.filter(category__slug=category)
        if subcategory:
            queryset = queryset.filter(subcategory__iexact=subcategory)
        if item_group:
            queryset = queryset.filter(item_group=item_group)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(subcategory__icontains=search)
                | Q(breed__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_category = self.request.GET.get("main_category") or self.kwargs.get("default_main_category", "")
        categories = DairyCategory.objects.filter(main_category__in=PRODUCT_MAIN_CATEGORIES)
        if main_category in PRODUCT_MAIN_CATEGORIES:
            categories = categories.filter(main_category=main_category)
        context["categories"] = categories.order_by("name")
        context["main_categories"] = DairyCategory.MainCategory.choices[:3]
        context["item_groups"] = DairyProduct.ItemGroup.choices
        context["main_category"] = main_category
        context["category"] = self.request.GET.get("category", "")
        context["subcategory"] = self.request.GET.get("subcategory", "")
        context["item_group"] = self.request.GET.get("item_group", "")
        context["query"] = self.request.GET.get("q", "")
        return context


class ProductDetailView(DetailView):
    model = DairyProduct
    template_name = "dairys/item_detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["app_label"] = self.object._meta.app_label
        context["model_name"] = self.object._meta.model_name
        context["related_items"] = DairyProduct.objects.filter(category=self.object.category).exclude(pk=self.object.pk)[:4]
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = DairyProduct
    form_class = DairyProductForm
    template_name = "dairys/item_create.html"
    login_url = "login"

    @method_decorator(role_required(UserRole.FARMER, UserRole.SUPPLIER))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Dairy listing published successfully.")
        return response


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = DairyService
    form_class = DairyServiceForm
    template_name = "dairys/service_create.html"
    login_url = "login"

    @method_decorator(role_required(UserRole.SUPPLIER, UserRole.VETERINARIAN, UserRole.SERVICE_PROVIDER))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.provider = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Dairy service published successfully.")
        return response


@login_required
def product_edit(request, slug):
    if request.user.is_staff:
        item = get_object_or_404(DairyProduct, slug=slug)
    else:
        item = get_object_or_404(DairyProduct, slug=slug, created_by=request.user)
    if request.method == "POST":
        form = DairyProductForm(request.POST, request.FILES, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dairy listing updated.")
            return redirect("dairys:product_detail", slug=item.slug)
    else:
        form = DairyProductForm(instance=item, user=request.user)
    return render(request, "dairys/item_create.html", {"form": form})


@login_required
def product_delete(request, slug):
    if request.user.is_staff:
        item = get_object_or_404(DairyProduct, slug=slug)
    else:
        item = get_object_or_404(DairyProduct, slug=slug, created_by=request.user)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Dairy listing deleted.")
        return redirect("dairys:marketplace")
    return render(request, "dairys/product_confirm_delete.html", {"item": item})


class ServiceListView(ListView):
    model = DairyService
    template_name = "dairys/services.html"
    context_object_name = "services"

    def get_queryset(self):
        queryset = DairyService.objects.filter(is_available=True)
        kind = self.request.GET.get("kind") or self.kwargs.get("default_kind", "")
        service_type = self.request.GET.get("service_type")
        if kind:
            queryset = queryset.filter(service_kind=kind)
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kind = self.request.GET.get("kind") or self.kwargs.get("default_kind", "")
        context["kind"] = kind
        context["service_type"] = self.request.GET.get("service_type", "")
        context["service_kinds"] = DairyService.ServiceKind.choices
        type_values = SERVICE_TYPES_BY_KIND.get(kind)
        context["service_types"] = (
            [(value, DairyService.ServiceType(value).label) for value in type_values]
            if type_values
            else DairyService.ServiceType.choices
        )
        return context


class ServiceDetailView(DetailView):
    model = DairyService
    template_name = "dairys/service_detail.html"
    context_object_name = "service"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["consultation_form"] = DairyConsultationForm()
        return context


def training(request):
    if request.method == "POST":
        form = TrainingEnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Enrollment received. We will contact you soon.")
            return redirect("dairys:training")
    else:
        form = TrainingEnrollmentForm()
    return render(request, "dairys/training.html", {
        "form": form,
        "topics": [
            (kind, DairyService.ServiceType(kind).label)
            for kind in SERVICE_TYPES_BY_KIND[DairyService.ServiceKind.TRAINING]
        ],
        "offers": DairyService.objects.filter(service_kind=DairyService.ServiceKind.TRAINING, is_available=True),
    })


@login_required
def consultation_book(request, slug):
    service = get_object_or_404(DairyService, slug=slug, is_available=True)
    if request.method == "POST":
        form = DairyConsultationForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.customer = request.user
            booking.save()
            messages.success(request, "Your consultation request has been sent.")
            return redirect("dairys:dairy_service_detail", slug=slug)
    else:
        form = DairyConsultationForm()
    return render(request, "dairys/consultation_book.html", {"service": service, "form": form})
