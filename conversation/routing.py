# conversation/routing.py
from django.urls import re_path  
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/conversation/(?P<conversation_id>[0-9a-f-]+)/$', consumers.ConversationConsumer.as_asgi()),
    
    re_path(r'^ws/user/(?P<user_id>\d+)/notifications/$', consumers.UserNotificationsConsumer.as_asgi()),
]