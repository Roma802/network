import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from django.shortcuts import get_object_or_404

from chat.models import Message, Chat
from network.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connect')
        self.chat_name = self.scope['url_route']['kwargs']['chat_name']
        self.chat_group_name = f'chat_{self.chat_name}'
        print('join')
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

    @sync_to_async
    def create_message(self, message, username):
        room = get_object_or_404(Chat, code=self.chat_name)
        user = get_object_or_404(User, username=username)
        Message.objects.create(text=message, author=user, room=room)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type_text_data = text_data_json['type']
        message = text_data_json['message']
        username = text_data_json['username']
        # another_user = text_data_json['to_user']
        print(f'username, type, message - {username, type_text_data, message}')
        if type_text_data == 'message':
            await self.create_message(message, username)
            await self.channel_layer.group_send(
                self.chat_group_name, {
                    "type": "chat_message",
                    "message": message,
                    "username": username
                })
            # messages_count = \
            # await database_sync_to_async(Message.objects.filter(Q(is_seen=False) & Q(author=another_user)).count)()
            # await self.send({
            #     "type": "messages_count",
            #     "user": another_user,
            #     "text": f"{messages_count}"
            # })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'username': event['username']
        }))

    async def disconnect(self, event):
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)