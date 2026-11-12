from django.urls import path

from . import views

app_name = "dairys"

urlpatterns = [
    path("", views.dairy_home, name="index"),
    path("market/", views.DairyMarketView.as_view(), name="marketplace"),
    path("create/", views.dairy_product_create, name="product_create"),
    path("services/create/", views.dairy_service_create, name="dairy_service_create"),
    path(
        "products/<int:product_id>/like/",
        views.like_dairy_product,
        name="like_product",
    ),
    path(
        "products/<int:product_id>/share/",
        views.share_dairy_product,
        name="share_product",
    ),
    path(
        "products/<slug:slug>/update/",
        views.dairy_product_update,
        name="product_update",
    ),
    path(
        "products/<slug:slug>/delete/",
        views.dairy_product_delete,
        name="product_delete",
    ),
    path("products/<slug:slug>/", views.dairy_product_detail, name="product_detail"),
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
    # Keep route names used by older links and integrations.
    path("market/", views.DairyMarketView.as_view(), name="dairy_list"),
    path("create/", views.dairy_product_create, name="dairy_create"),
    path(
        "products/<int:product_id>/like/",
        views.like_dairy_product,
        name="like_dairy",
    ),
    path(
        "products/<int:product_id>/share/",
        views.share_dairy_product,
        name="share_dairy",
    ),
    path(
        "products/<slug:slug>/update/",
        views.dairy_product_update,
        name="dairy_update",
    ),
    path(
        "products/<slug:slug>/delete/",
        views.dairy_product_delete,
        name="dairy_delete",
    ),
    path(
        "products/<slug:slug>/",
        views.dairy_product_detail,
        name="dairy_detail",
    ),
]
