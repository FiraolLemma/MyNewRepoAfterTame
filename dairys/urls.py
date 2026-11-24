from django.urls import path
from . import views

app_name = "dairys"

urlpatterns = [
    path("", views.index, name="index"),
    path("items/", views.items, name="items"),
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
