"""
ASGI config for project4 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from django.core.asgi import get_asgi_application
from django.urls import path, re_path

import chat.routing
import network.routing
from chat.consumers import ChatConsumer
from network.consumers import YourConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project4.settings')

application = get_asgi_application()


application = ProtocolTypeRouter({
    'http': application,
    'websocket': AuthMiddlewareStack(
        URLRouter([
    *chat.routing.websocket_urlpatterns,
    *network.routing.websocket_urlpatterns,
    # path('ws/<str:chat_name>/', ChatConsumer.as_asgi()),
    # path('ws', YourConsumer.as_asgi()),
    ])
    )
})