# conversation/urls.py
from django.urls import path
from . import views

app_name = 'conversation'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:pk>/', views.detail, name='detail'),
    path('new/<str:app_label>/<str:model_name>/<int:object_id>/', views.new_conversation, name='new'),
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
    path('api/mark-all-read/', views.mark_all_read, name='mark_all_read'),
]