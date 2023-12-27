from django.urls import path

from network.consumers import YourConsumer

websocket_urlpatterns = [
    path('ws', YourConsumer.as_asgi()),
]