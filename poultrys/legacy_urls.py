from django.urls import path

from . import views
from .api.views import ItemDetailAPIView, ItemListAPIView
from .views import (
    ItemCreateView,
    ItemDetailView,
    ItemListView,
    item_delete,
    item_edit,
)

app_name = "poultrys"

urlpatterns = [
    path("", ItemListView.as_view(), name="item_list"),
    path("<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("create/", ItemCreateView.as_view(), name="item_create"),
    path("poultry/", views.index, name="index"),
    path("api/poultrys/", ItemListAPIView.as_view(), name="api_item_list"),
    path("api/poultrys/<int:pk>/", ItemDetailAPIView.as_view(), name="api_item_detail"),
    path("<int:pk>/edit/", item_edit, name="item_edit"),
    path("<int:pk>/delete/", item_delete, name="item_delete"),
    path("<int:pk>/like/", views.like_item, name="item_like"),
    path("<int:pk>/share/", views.share_item, name="item_share"),
    path(
        "egg-sellers/delete-ajax/<int:pk>/",
        views.delete_egg_seller_ajax,
        name="delete_egg_seller_ajax",
    ),
    path("egg-sellers/add/", views.add_egg_seller, name="add_egg_seller"),
    path("egg-sellers/edit/<int:pk>/", views.edit_egg_seller, name="edit_egg_seller"),
    path("egg-sellers/place-order/", views.place_egg_order, name="place_egg_order"),
    path("egg-sellers/", views.egg_sellers, name="egg_sellers"),
    path("my-orders/", views.egg_seller_orders, name="egg_seller_orders"),
    path("chicken-sellers/", views.chicken_sellers_list, name="chicken_sellers_list"),
    path(
        "chicken-seller/<int:seller_id>/",
        views.chicken_seller_detail,
        name="chicken_seller_detail",
    ),
    path("register-seller/", views.register_seller, name="register_seller"),
    path("edit-seller/<int:seller_id>/", views.edit_seller, name="edit_seller"),
    path("delete-seller/<int:seller_id>/", views.delete_seller, name="delete_seller"),
    path(
        "delete-seller-ajax/<int:seller_id>/",
        views.delete_seller_ajax,
        name="delete_seller_ajax",
    ),
    path(
        "veterinary-consultancy/",
        views.veterinary_consultancy,
        name="veterinary_consultancy",
    ),
    path("book-consultation/", views.book_consultation, name="book_consultation"),
    path("trainings/", views.poultry_trainings, name="poultry_trainings"),
    path("trainees/", views.poultry_trainees, name="poultry_trainees"),
]
