from django.urls import path
from . import views

app_name = "dairys"

urlpatterns = [
    path("", views.index, name="index"),
    path("training/", views.training, name="training"),
    path("training/create/", views.training_create, name="training_create"),
    path("training/mine/", views.training_dashboard, name="training_dashboard"),
    path("training/<slug:slug>/enroll/", views.training_enroll, name="training_enroll"),
    path("training/<slug:slug>/", views.training_detail, name="training_detail"),
    path("items/", views.items, name="items"),
    path("items/create/", views.item_create, name="item_create"),
    path("items/<int:item_id>/", views.item_detail, name="item_detail"),
    path("products/", views.products, name="products"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cattle-livestock/", views.cattle_livestock, name="cattle_livestock"),
    path(
        "cattle-livestock/create/",
        views.cattle_livestock_create,
        name="cattle_livestock_create",
    ),
    path(
        "cattle-livestock/<int:cattle_livestock_id>/",
        views.cattle_livestock_detail,
        name="cattle_livestock_detail",
    ),
    path(
        "veterinary-consulting/",
        views.veterinary_consultancy,
        name="veterinary_consultancy",
    ),
    path(
        "veterinary-consulting/register/",
        views.consultacy_create,
        name="consultacy_create",
    ),
    path(
        "veterinary-consulting/book/<int:service_id>/",
        views.consultation_create,
        name="consultation_create",
    ),
]
