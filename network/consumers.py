from asgiref.sync import sync_to_async, async_to_sync
from channels.consumer import AsyncConsumer
import json

from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

from network.models import Notification


class YourConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('ok')
        await self.send({"type": "websocket.accept"})

    @database_sync_to_async
    def get_unseen_notification_count(self, user):
        return Notification.objects.filter(is_seen=False, user=user).count()

    async def websocket_receive(self, text_data):
        text_data = text_data.get('text')  # {"message":"Hello from Js client"}
        if text_data:
            user = json.loads(text_data)['user']  # loads - из json в python
            # notification_count = database_sync_to_async(Notification.objects.filter(is_seen=False).count())
            notification_count = await self.get_unseen_notification_count(user)
            await self.send({
                "type": "websocket.send",
                "text": f"{notification_count}"
            })
        # await self.send({
        #     "type": 'websocket.send',
        #     "text": f"Received message from Js client: {text_data['text']}"
        # })
        # await self.send({
        #     "type": "websocket.send",
        #     "text": "Hello from Django socket"
        # })

    async def websocket_disconnect(self, event):
        # async_to_sync(self.channel_layer.group_discard)(
        #     self.room_group_name,
        #     self.channel_name
        # )
        raise StopConsumer()