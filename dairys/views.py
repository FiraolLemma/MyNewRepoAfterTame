
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_http_methods

from .forms import DairyConsultationForm, DairyProductForm, DairyServiceForm
from .models import DairyProduct, DairyService


def index(request):
    return render(request, "dairys/index.html")


def items(request):
    item_queryset = DairyProduct.objects.filter(main_category="items")
    group_counts = dict(
        item_queryset.order_by()
        .values("item_group")
        .annotate(total=Count("pk"))
        .values_list("item_group", "total")
    )
    categories = [
        {"value": value, "label": label, "count": group_counts.get(value, 0)}
        for value, label in DairyProduct.ITEM_GROUP_CHOICES
    ]
    item_queryset = item_queryset.select_related("category", "company", "created_by", "farm")

    return render(
        request,
        "dairys/item_list.html",
        {
            "items": item_queryset,
            "categories": categories,
            "total_count": item_queryset.count(),
        },
    )


def item_detail(request, item_id):
    item = get_object_or_404(
        DairyProduct.objects.select_related("category", "company", "created_by", "farm"),
        pk=item_id,
        main_category="items",
    )
    return render(request, "dairys/item_detail.html", {"item": item})


def products(request):
    product_queryset = DairyProduct.objects.filter(main_category="milk")
    source_counts = dict(
        product_queryset.order_by()
        .values("milk_source")
        .annotate(total=Count("pk"))
        .values_list("milk_source", "total")
    )
    categories = [
        {
            "value": value,
            "label": f"{label} Milk",
            "count": source_counts.get(value, 0),
        }
        for value, label in DairyProduct.MILK_SOURCE_CHOICES
    ]
    product_queryset = product_queryset.select_related(
        "category", "company", "created_by", "farm"
    )

    return render(
        request,
        "dairys/product_list.html",
        {
            "products": product_queryset,
            "categories": categories,
            "total_count": product_queryset.count(),
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        DairyProduct.objects.select_related("category", "company", "created_by", "farm"),
        slug=slug,
        main_category="milk",
    )
    return render(request, "dairys/product_detail.html", {"product": product})


@login_required
def product_create(request):
    if request.method == "POST":
        form = DairyProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.main_category = "milk"
            product.created_by = request.user

            base_slug = slugify(product.name)[:180].strip("-") or "dairy-product"
            product.slug = base_slug
            suffix = 2
            while DairyProduct.objects.filter(slug=product.slug).exists():
                suffix_text = f"-{suffix}"
                product.slug = f"{base_slug[:180 - len(suffix_text)]}{suffix_text}"
                suffix += 1

            product.save()
            return redirect("dairys:product_detail", slug=product.slug)
    else:
        form = DairyProductForm(user=request.user)

    return render(request, "dairys/product_create.html", {"form": form})


def cattle_livestock(request):
    livestock = DairyProduct.objects.filter(main_category="livestock")
    counts = dict(
        livestock.order_by()
        .values("livestock_type")
        .annotate(total=Count("pk"))
        .values_list("livestock_type", "total")
    )
    products = livestock.select_related("category", "company", "created_by", "farm")
    categories = [
        {"value": "dairy_cow", "label": "Dairy Cows", "count": counts.get("dairy_cow", 0)},
        {"value": "heifer", "label": "Heifers", "count": counts.get("heifer", 0)},
        {"value": "calf", "label": "Calves", "count": counts.get("calf", 0)},
        {"value": "bull", "label": "Bulls", "count": counts.get("bull", 0)},
        {"value": "goat", "label": "Goats", "count": counts.get("goat", 0)},
        {"value": "sheep", "label": "Sheep", "count": counts.get("sheep", 0)},
    ]

    return render(
        request,
        "dairys/cattle_livestock_list.html",
        {
            "products": products,
            "categories": categories,
            "total_count": products.count(),
        },
    )


def cattle_livestock_detail(request, cattle_livestock_id):
    product = get_object_or_404(
        DairyProduct,
        pk=cattle_livestock_id,
        main_category="livestock",
    )
    return render(request, "dairys/cattle_livestock_detail.html", {"product": product})


@require_GET
def veterinary_consultancy(request):
    services = DairyService.objects.filter(
        service_kind="consulting",
        is_available=True,
    ).select_related("provider")
    service_type = request.GET.get("specialty", "").strip()
    search_query = request.GET.get("q", "").strip()[:100]

    valid_service_types = set(DairyService.CONSULTING_SERVICE_TYPE_VALUES)
    if service_type in valid_service_types:
        services = services.filter(service_type=service_type)
    else:
        service_type = ""

    if search_query:
        services = services.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(service_area__icontains=search_query)
            | Q(provider__username__icontains=search_query)
        )

    return render(
        request,
        "dairys/consultacy.html",
        {
            "services": services,
            "service_count": services.count(),
            "service_types": [
                (value, label)
                for value, label in DairyService.SERVICE_TYPE_CHOICES
                if value in DairyService.CONSULTING_SERVICE_TYPE_VALUES
            ],
            "selected_service_type": service_type,
            "search_query": search_query,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def consultacy_create(request):
    if request.method == "POST":
        form = DairyServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.service_kind = "consulting"
            service.training_format = ""

            base_slug = slugify(service.name)[:180].strip("-") or "dairy-consultant"
            service.slug = base_slug
            suffix = 2
            while DairyService.objects.filter(slug=service.slug).exists():
                suffix_text = f"-{suffix}"
                service.slug = f"{base_slug[:180 - len(suffix_text)]}{suffix_text}"
                suffix += 1

            service.save()
            messages.success(request, _("Your consulting profile is now listed."))
            return redirect("dairys:veterinary_consultancy")
    else:
        form = DairyServiceForm()

    return render(request, "dairys/consultacy_create.html", {"form": form})


@require_http_methods(["GET", "POST"])
def consultation_create(request, service_id):
    service = get_object_or_404(
        DairyService.objects.select_related("provider"),
        pk=service_id,
        service_kind="consulting",
        is_available=True,
    )
    if request.user.is_authenticated and service.provider_id == request.user.pk:
        messages.error(request, _("You cannot book your own consulting profile."))
        return redirect("dairys:veterinary_consultancy")

    customer = request.user if request.user.is_authenticated else None
    form_data = request.POST if request.method == "POST" else None
    form = DairyConsultationForm(form_data, customer=customer)

    if request.method == "POST" and form.is_valid():
        consultation = form.save(commit=False)
        consultation.service = service
        consultation.customer = customer
        consultation.save()
        messages.success(
            request,
            _("Your consultation request has been sent to %(name)s.")
            % {"name": service.name},
        )
        return redirect("dairys:veterinary_consultancy")

    return render(
        request,
        "dairys/consultacy_booking.html",
        {
            "form": form,
            "service": service,
        },
    )
