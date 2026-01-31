from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from .models import Room
from .serializers import RoomSerializer


class RoomsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        await self.accept()

        rooms = await self.get_user_rooms()

        await self.send(text_data=json.dumps({"type": "rooms_list", "rooms": rooms}))

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def get_user_rooms(self):
        queryset = (
            Room.objects.filter(
                participants__user=self.user, participants__is_active=True
            )
            .distinct()
            .prefetch_related("participants__user")
        )

        serializer = RoomSerializer(queryset, many=True, context={"user": self.user})
        return serializer.data
