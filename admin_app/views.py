from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render

from companies.models import Farm
from conversation.models import Conversation
from dairys.models import DairyProduct, DairyService
from poultrys.models import (
    ChickenSeller,
    Consultant,
    EggOrder,
    EggSeller,
    Item,
    TrainingEnrollment,
)

from .forms import DashboardSearchForm


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view


@admin_required
def dashboard(request):
    search_form = DashboardSearchForm(request.GET or None)
    query = ""
    if search_form.is_valid():
        query = search_form.cleaned_data["q"]

    dairy_products = DairyProduct.objects.select_related(
        "category", "created_by", "farm"
    )
    poultry_items = Item.objects.select_related("created_by", "farm")
    egg_orders = EggOrder.objects.select_related("seller", "seller__farm")
    if query:
        dairy_products = dairy_products.filter(
            Q(name__icontains=query)
            | Q(farm__name__icontains=query)
            | Q(created_by__username__icontains=query)
        )
        poultry_items = poultry_items.filter(
            Q(name__icontains=query)
            | Q(farm__name__icontains=query)
            | Q(created_by__username__icontains=query)
        )
        egg_orders = egg_orders.filter(
            Q(customer_name__icontains=query)
            | Q(seller__farm_name__icontains=query)
        )

    user_model = get_user_model()
    dairy_farms = Farm.objects.filter(
        Q(dairy_products__isnull=False) | Q(dairy_services__isnull=False)
    ).distinct()
    context = {
        "users_count": user_model.objects.count(),
        "dairy_managers_count": user_model.objects.filter(
            Q(dairy_products__isnull=False)
            | Q(dairy_services__isnull=False)
            | Q(farms__dairy_products__isnull=False)
            | Q(farms__dairy_services__isnull=False)
        ).distinct().count(),
        "dairy_farms_count": dairy_farms.count(),
        "dairy_products_count": DairyProduct.objects.count(),
        "dairy_services_count": DairyService.objects.count(),
        "poultry_managers_count": user_model.objects.filter(
            Q(items__isnull=False)
            | Q(egg_seller__isnull=False)
            | Q(chicken_seller__isnull=False)
            | Q(farms__poultry_items__isnull=False)
            | Q(farms__egg_seller_profiles__isnull=False)
            | Q(farms__chicken_seller_profiles__isnull=False)
        ).distinct().count(),
        "poultry_farms_count": Farm.objects.filter(
            Q(poultry_items__isnull=False)
            | Q(egg_seller_profiles__isnull=False)
            | Q(chicken_seller_profiles__isnull=False)
        ).distinct().count(),
        "poultry_items_count": Item.objects.count(),
        "egg_sellers_count": EggSeller.objects.count(),
        "chicken_sellers_count": ChickenSeller.objects.count(),
        "egg_orders_count": EggOrder.objects.count(),
        "dairy_products": dairy_products.order_by("-created_at")[:6],
        "poultry_items": poultry_items.order_by("-created_at")[:6],
        "egg_orders": egg_orders.order_by("-order_date")[:6],
        "search_form": search_form,
    }
    return render(request, "admin_app/dashboard.html", context)


@admin_required
def manage_dairys(request):
    context = {
        "dairy_products": DairyProduct.objects.select_related(
            "category", "created_by", "farm"
        ),
        "dairy_services": DairyService.objects.select_related("provider", "farm"),
    }
    return render(request, "admin_app/manage_dairys.html", context)


@admin_required
def manage_poultry(request):
    context = {
        "items": Item.objects.select_related("created_by", "farm"),
        "egg_sellers": EggSeller.objects.select_related("user", "farm"),
        "chicken_sellers": ChickenSeller.objects.select_related("user", "farm"),
        "consultants": Consultant.objects.all(),
        "trainings": TrainingEnrollment.objects.all(),
    }
    return render(request, "admin_app/manage_poultry.html", context)


@admin_required
def manage_sales(request):
    orders = EggOrder.objects.select_related("seller", "customer").order_by(
        "-order_date"
    )
    return render(request, "admin_app/manage_sales.html", {"orders": orders})


@admin_required
def manage_users(request):
    users = get_user_model().objects.all()
    return render(request, "admin_app/manage_users.html", {"users": users})


@admin_required
def manage_conversations(request):
    conversations = Conversation.objects.prefetch_related("members").all()
    return render(
        request,
        "admin_app/manage_conversations.html",
        {"conversations": conversations},
    )
