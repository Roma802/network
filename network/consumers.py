from asgiref.sync import sync_to_async, async_to_sync
from channels.consumer import AsyncConsumer
import json

from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from django.db.models import Q

from network.models import Notification


class YourConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('ok')
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        text_data = text_data.get('text')
        if text_data:
            user = json.loads(text_data)['user']
            notification_count = \
                await database_sync_to_async(Notification.objects.filter(Q(is_seen=False) & Q(user=user)).count)()
            await self.send({
                "type": "websocket.send",
                "text": f"{notification_count}"
            })

    async def websocket_disconnect(self, event):
        raise StopConsumer()