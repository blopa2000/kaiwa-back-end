# users/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import UserStatus

User = get_user_model()


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Agregar al grupo global de presencia
        await self.channel_layer.group_add("presence_group", self.channel_name)
        await self.accept()
        await self.set_user_online()

    async def disconnect(self, close_code):
        await self.set_user_offline()
        # Sacar del grupo
        await self.channel_layer.group_discard("presence_group", self.channel_name)

    async def set_user_online(self):
        await self._update_status("online")
        await self.channel_layer.group_send(
            "presence_group",
            {"type": "presence_update", "user_id": self.user.id, "status": "online"},
        )

    async def set_user_offline(self):
        await self._update_status("offline")
        await self.channel_layer.group_send(
            "presence_group",
            {"type": "presence_update", "user_id": self.user.id, "status": "offline"},
        )

    async def presence_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _update_status(self, status):
        if not self.user or not self.user.is_authenticated:
            return
        UserStatus.objects.update_or_create(user=self.user, defaults={"status": status})
