from django.shortcuts import render
from dairys.models import DairyProduct, DairyService
from poultrys.models import Item, EggSeller, ChickenSeller, Consultant, TrainingEnrollment
from users.models import Profile
from conversation.models import Conversation
from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    decorated = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated


@admin_required
def dashboard(request):
    context = {
        "dairy_products_count": DairyProduct.objects.count(),
        "dairy_services_count": DairyService.objects.count(),
        "poultry_items_count": Item.objects.count(),
        "egg_sellers_count": EggSeller.objects.count(),
        "chicken_sellers_count": ChickenSeller.objects.count(),
        "consultants_count": Consultant.objects.count(),
        "trainings_count": TrainingEnrollment.objects.count(),
        "users_count": Profile.objects.count(),
        "conversations_count": Conversation.objects.count(),
    }
    return render(request, "admin_app/dashboard.html", context)
@admin_required
def manage_clothings(request):
    context = {
        "dairy_products": DairyProduct.objects.select_related("category", "created_by").all(),
        "dairy_services": DairyService.objects.select_related("provider").all(),
    }
    return render(request, "admin_app/manage_clothings.html", context)


@admin_required
def manage_poultry(request):
    context = {
        "items": Item.objects.all(),
        "egg_sellers": EggSeller.objects.all(),
        "chicken_sellers": ChickenSeller.objects.all(),
        "consultants": Consultant.objects.all(),
        "trainings": TrainingEnrollment.objects.all(),
    }
    return render(request, "admin_app/manage_poultry.html", context)


@admin_required
def manage_users(request):
    return render(request, "admin_app/manage_users.html", {"users": Profile.objects.all()})


@admin_required
def manage_conversations(request):
    return render(request, "admin_app/manage_conversations.html", {"conversations": Conversation.objects.all()})
