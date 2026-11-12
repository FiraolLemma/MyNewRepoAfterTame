from django.urls import path
from . import views

app_name = "admin_app"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dairys/", views.manage_dairys, name="manage_dairys"),
    path("poultrys/", views.manage_poultry, name="manage_poultry"),
    path("sales/", views.manage_sales, name="manage_sales"),
    path("users/", views.manage_users, name="manage_users"),
    path("conversations/", views.manage_conversations, name="manage_conversations"),
]
