from django.urls import path

from . import views

app_name = "clothings"

urlpatterns = [
    path("", views.DairyMarketView.as_view(), name="clothing_list"),
    path("create/", views.dairy_product_create, name="clothing_create"),
    path("services/create/", views.dairy_service_create, name="dairy_service_create"),
    path(
        "products/<int:product_id>/like/",
        views.like_dairy_product,
        name="like_clothing",
    ),
    path(
        "products/<int:product_id>/share/",
        views.share_dairy_product,
        name="share_clothing",
    ),
    path(
        "products/<slug:slug>/update/",
        views.dairy_product_update,
        name="clothing_update",
    ),
    path(
        "products/<slug:slug>/delete/",
        views.dairy_product_delete,
        name="clothing_delete",
    ),
    path("products/<slug:slug>/", views.dairy_product_detail, name="clothing_detail"),
    path(
        "services/<slug:slug>/update/",
        views.dairy_service_update,
        name="dairy_service_update",
    ),
    path(
        "services/<slug:slug>/delete/",
        views.dairy_service_delete,
        name="dairy_service_delete",
    ),
    path(
        "services/<slug:slug>/",
        views.dairy_service_detail,
        name="dairy_service_detail",
    ),
]
