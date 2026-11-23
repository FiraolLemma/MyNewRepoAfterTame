from django.urls import path
from . import views

app_name = "dairys"

urlpatterns = [
    path("", views.index, name="index"),
    path("marketplace/", views.MarketplaceView.as_view(), name="marketplace"),
    path("products/", views.MarketplaceView.as_view(), {"default_main_category": "milk"}, name="Products"),
    path("items/", views.MarketplaceView.as_view(), {"default_main_category": "items"}, name="Items"),
    path("cattle-livestock/", views.MarketplaceView.as_view(), {"default_main_category": "livestock"}, name="CattleLiveStock"),
    path("consultancy/", views.ServiceListView.as_view(), {"default_kind": "consulting"}, name="Consultancy"),
    path("training-offers/", views.ServiceListView.as_view(), {"default_kind": "training"}, name="TrainingOffers"),
    path("items/create/", views.ProductCreateView.as_view(), name="product_create"),
    path("items/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("items/<slug:slug>/edit/", views.product_edit, name="product_edit"),
    path("items/<slug:slug>/delete/", views.product_delete, name="product_delete"),
    path("services/", views.ServiceListView.as_view(), name="services"),
    path("services/create/", views.ServiceCreateView.as_view(), name="service_create"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="dairy_service_detail"),
    path("services/<slug:slug>/book/", views.consultation_book, name="consultation_book"),
    path("training/", views.training, name="training"),
    path("training/", views.training, name="Training"),
]
