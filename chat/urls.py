from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from chat import views

urlpatterns = [
    path("chat/<int:pk>", views.chat, name="chat"),
    path("create_room/<str:uuid>", views.create_room, name="create_room"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)