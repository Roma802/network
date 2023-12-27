from django import template
from django.db.models import Q
from django.shortcuts import get_object_or_404

from chat.models import Message, Chat

register = template.Library()


@register.simple_tag
def get_not_request_user(chat, request_user):
    if chat.user1 == request_user:
        return chat.user2
    elif chat.user2 == request_user:
        return chat.user1
    else:
        return None


@register.simple_tag
def get_count_of_unread_messages(chat, another_user):
    return Message.objects.filter(Q(room=chat) & Q(author=another_user) & Q(is_seen=False)).count()