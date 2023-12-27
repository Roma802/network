import json

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q, Max
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse

from chat.models import Chat, Message
from network.models import User


@login_required
def chat(request, pk):
    chats_for_user = Chat.objects.filter(Q(user2=request.user) | Q(user1=request.user)).annotate(
        last_message_date=Max('room_messages__created_at')
    ).order_by('-last_message_date')
    if request.user.pk != pk:  # request.user.pk == pk, when request.user open his messages, but not the dialogue with someone
        another_user = get_object_or_404(User, pk=pk)
        chat = get_object_or_404(Chat, Q(user1=another_user, user2=request.user) | Q(user1=request.user, user2=another_user))
        messages = Message.objects.filter(room=chat)
        if request.method == 'PUT':
            Message.objects.filter(Q(room=chat) & Q(author=another_user)).update(is_seen=True)
            return JsonResponse({'status': 'success'})
        return render(request, 'chat/chat.html',
                      {'user': another_user, 'chat': chat, 'messages': messages,
                       'chats_for_user': chats_for_user})

    return render(request, 'chat/chat.html', {'chats_for_user': chats_for_user})


@login_required
def create_room(request, uuid):
    user1_pk = int(request.POST.get('user1', 0))
    user2_pk = int(request.POST.get('user2', 0))
    if user1_pk and user2_pk:
        user1 = get_object_or_404(User, pk=user1_pk)
        user2 = get_object_or_404(User, pk=user2_pk)
        if not Chat.objects.filter(Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)).exists():
            Chat.objects.create(user1=user1, user2=user2, code=uuid)
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Chat room already exists'})
    else:
        return JsonResponse({'status': 'error', 'message': 'There are no '})
