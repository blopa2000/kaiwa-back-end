from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
from rooms.models import RoomParticipant, Room
from .models import Message
from users.models import UserStatus
from channels.db import database_sync_to_async
from django.utils import timezone

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        is_participant = await self.user_in_room(self.user, self.room_id)
        if not is_participant:
            await self.close(code=4003)
            return

        # 🔥 USUARIO ONLINE
        await self.set_user_online(self.user)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # 📩 Enviar últimos 10 mensajes
        messages = await self.get_last_messages(self.room_id)
        for msg in reversed(messages):
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "message",
                        "id": msg.id,
                        "content": msg.content,
                        "sender_id": msg.sender_id,
                        "created_at": msg.created_at.isoformat(),
                        "read_at": msg.read_at.isoformat() if msg.read_at else None,
                        "edited_at": (
                            msg.edited_at.isoformat()
                            if hasattr(msg, "edited_at") and msg.edited_at
                            else None
                        ),
                    }
                )
            )

        # 🔔 Avisar al room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_join",
                "user_id": self.user.id,
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

        if self.user and self.user.is_authenticated:
            # 🔥 USUARIO OFFLINE
            await self.set_user_offline(self.user)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_leave",
                    "user_id": self.user.id,
                },
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "typing":
            await self.handle_typing(data)
        elif event_type == "message":
            await self.handle_message(data)
        elif event_type == "read":
            await self.handle_read(data)
        elif event_type == "edit":
            await self.handle_edit(data)

    # ================== EVENTS ==================

    async def handle_message(self, data):
        content = data.get("content")
        if not content:
            return

        message = await self.create_message(self.user, self.room_id, content)

        message_data = {
            "id": message.id,
            "content": message.content,
            "sender_id": self.user.id,
            "created_at": message.created_at.isoformat(),
        }

        # Enviar a la conversación activa
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                **message_data,
            },
        )

        # Notificar a la chat-list (rooms)
        participants = await self.get_room_participants(self.room_id)

        for user_id in participants:
            await self.channel_layer.group_send(
                f"rooms_user_{user_id}",
                {
                    "type": "new_message",
                    "room_id": int(self.room_id),
                    "message": message_data,
                },
            )

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_event",
                "user_id": self.user.id,
                "value": data.get("value", False),
            },
        )

    async def handle_read(self, data):
        """
        data: { "message_ids": [1,2,3] }
        """
        message_ids = data.get("message_ids", [])
        if not message_ids:
            return

        updated = await self.mark_as_read(message_ids)

        if updated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "messages_read",
                    "message_ids": message_ids,
                    "user_id": self.user.id,
                },
            )

    async def handle_edit(self, data):
        """
        data: { "message_id": 1, "content": "nuevo contenido" }
        """
        message_id = data.get("message_id")
        new_content = data.get("content")
        if not message_id or new_content is None:
            return

        message = await self.edit_message(message_id, new_content)
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_edited",
                    "id": message.id,
                    "content": message.content,
                    "edited_at": (
                        message.edited_at.isoformat() if message.edited_at else None
                    ),
                },
            )

    # ================== SENDERS ==================

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "id": event["id"],
                    "content": event["content"],
                    "sender_id": event["sender_id"],
                    "created_at": event["created_at"],
                }
            )
        )

    async def typing_event(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "user_id": event["user_id"],
                    "value": event["value"],
                }
            )
        )

    async def user_join(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "join",
                    "user_id": event["user_id"],
                }
            )
        )

    async def user_leave(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "leave",
                    "user_id": event["user_id"],
                }
            )
        )

    async def messages_read(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "read",
                    "message_ids": event["message_ids"],
                    "user_id": event["user_id"],
                }
            )
        )

    async def message_edited(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "edit",
                    "id": event["id"],
                    "content": event["content"],
                    "edited_at": event["edited_at"],
                }
            )
        )

    # ================== DB ==================

    @database_sync_to_async
    def user_in_room(self, user, room_id):
        return RoomParticipant.objects.filter(
            room_id=room_id, user=user, is_active=True
        ).exists()

    @database_sync_to_async
    def create_message(self, user, room_id, content):
        room = Room.objects.get(id=room_id)
        return Message.objects.create(sender=user, room=room, content=content)

    @database_sync_to_async
    def get_last_messages(self, room_id, limit=10):
        return list(
            Message.objects.filter(room_id=room_id).order_by("-created_at")[:limit]
        )

    @database_sync_to_async
    def mark_as_read(self, message_ids):
        return Message.objects.filter(id__in=message_ids, read_at__isnull=True).update(
            read_at=timezone.now()
        )

    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        message = Message.objects.get(id=message_id)
        if message.sender_id != self.user.id:
            return None  # No puede editar si no es autor
        message.content = new_content
        message.edited_at = timezone.now()
        message.save()
        return message

    @database_sync_to_async
    def set_user_online(self, user):
        UserStatus.objects.update_or_create(user=user, defaults={"status": "online"})

    @database_sync_to_async
    def set_user_offline(self, user):
        UserStatus.objects.update_or_create(user=user, defaults={"status": "offline"})

    @database_sync_to_async
    def set_user_typing(self, user):
        UserStatus.objects.update_or_create(user=user, defaults={"status": "typing"})

    @database_sync_to_async
    def get_room_participants(self, room_id):
        return list(
            RoomParticipant.objects.filter(room_id=room_id, is_active=True).values_list(
                "user_id", flat=True
            )
        )
