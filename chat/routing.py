from django.template.defaulttags import url
from django.urls import path, re_path

from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/<str:chat_name>/', ChatConsumer.as_asgi()),
    re_path(r'^ws/(?P<chat_name>[^/]+)/$', ChatConsumer.as_asgi()),
]