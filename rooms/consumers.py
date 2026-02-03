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

        # Grupo único por usuario (para su chat-list)
        self.group_name = f"rooms_user_{self.user.id}"

        # Unirse al grupo
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        # Enviar lista inicial de rooms
        rooms = await self.get_user_rooms()
        await self.send(text_data=json.dumps({"type": "rooms_list", "rooms": rooms}))

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # 🔥 Evento: mensaje nuevo en cualquier room
    async def new_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_message",
                    "room_id": event["room_id"],
                    "message": event["message"],
                }
            )
        )

    # 🔁 Evento: room actualizada (opcional)
    async def room_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "room_update",
                    "room": event["room"],
                }
            )
        )

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
