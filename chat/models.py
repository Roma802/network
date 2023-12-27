import uuid as uuid
from django.db import models

# Create your models here.
from django.db.models import Q
from django.urls import reverse

from network.models import User


class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='user1', on_delete=models.SET_NULL, null=True)
    user2 = models.ForeignKey(User, related_name='user2', on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=32, default='', null=True, blank=True)

    def get_last_message(self):
        messages = Message.objects.filter(room=self)
        if messages:
            return messages.order_by('-created_at')[0]
        else:
            return 'now you can chat!'


class Message(models.Model):
    text = models.TextField(max_length=512)
    author = models.ForeignKey(User, related_name='author_message', on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Chat, related_name='room_messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author}: {self.text[:10]}...'


