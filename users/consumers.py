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

        # MARCAR ONLINE AL CONECTAR
        await self.set_user_online()

        # enviar snapshot inicial
        statuses = await self.get_all_statuses()
        await self.send(
            text_data=json.dumps({"type": "presence_snapshot", "users": statuses})
        )

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

    async def set_user_typing(self):
        await self._update_status("typing")
        await self.channel_layer.group_send(
            "presence_group",
            {"type": "presence_update", "user_id": self.user.id, "status": "typing"},
        )

    async def presence_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "ping":
            await self.set_user_online()
        elif data.get("type") == "typing":
            await self.set_user_typing()

        # Nuevo: pedir estado de usuario específico
        if data.get("type") == "get_status":
            user_id = data.get("user_id")
            if not user_id:
                return

            status = await self.get_user_status(user_id)
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "status_response",
                        "user_id": user_id,
                        "status": status,
                    }
                )
            )

    @database_sync_to_async
    def _update_status(self, status):
        if not self.user or not self.user.is_authenticated:
            return
        UserStatus.objects.update_or_create(user=self.user, defaults={"status": status})

    @database_sync_to_async
    def get_all_statuses(self):
        users = User.objects.exclude(id=self.user.id)

        statuses = []
        for user in users:
            status, _ = UserStatus.objects.get_or_create(
                user=user,
                defaults={"status": "offline"},
            )
            statuses.append({"user_id": user.id, "status": status.status})

        return statuses

    @database_sync_to_async
    def get_user_status(self, user_id):
        try:
            user_status = UserStatus.objects.get(user_id=user_id)
            return user_status.status
        except UserStatus.DoesNotExist:
            return "offline"
