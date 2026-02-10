from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model
from django.utils import timezone

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from rooms.models import Room, RoomParticipant
from rooms.serializers import RoomSerializer

from .models import Message
from .serializers import MessageSerializer

User = get_user_model()


class MessageListPagination(LimitOffsetPagination):
    default_limit = 30
    max_limit = 50


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipient_id = self.request.data.get("recipient_id")
        content = self.request.data.get("content")

        sender = self.request.user
        recipient = User.objects.get(id=recipient_id)

        channel_layer = get_channel_layer()

        # 🔍 Buscar room 1 a 1 existente (usando RoomParticipant)
        room = (
            Room.objects.filter(
                participants__user=sender,
                participants__is_active=True,
            )
            .filter(
                participants__user=recipient,
                participants__is_active=True,
            )
            .distinct()
            .first()
        )

        room_was_created = False

        # 🆕 Crear room si no existe
        if not room:
            room = Room.objects.create()

            RoomParticipant.objects.bulk_create(
                [
                    RoomParticipant(room=room, user=sender),
                    RoomParticipant(room=room, user=recipient),
                ]
            )

            room_was_created = True

        # 💬 Crear mensaje
        message = serializer.save(sender=sender, room=room, content=content)

        # 🔔 Notificar creación de room (solo la primera vez)
        if room_was_created:
            for user in (sender, recipient):
                room_serializer = RoomSerializer(room, context={"user": user})

                async_to_sync(channel_layer.group_send)(
                    f"rooms_user_{user.id}",
                    {
                        "type": "room_created",
                        "room": room_serializer.data,
                    },
                )

        # 📩 Notificar mensaje nuevo a ambos usuarios (sidebar + conversación)
        message_data = MessageSerializer(message).data

        async_to_sync(channel_layer.group_send)(
            f"rooms_user_{recipient.id}",
            {
                "type": "new_message",
                "room_id": room.id,
                "message": message_data,
            },
        )

        async_to_sync(channel_layer.group_send)(
            f"rooms_user_{sender.id}",
            {
                "type": "new_message",
                "room_id": room.id,
                "message": message_data,
            },
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessageListPagination

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        queryset = Message.objects.filter(
            room_id=room_id,
            room__participants__user=self.request.user,
            room__participants__is_active=True,
        )

        before_id = self.request.query_params.get("before_id")

        if before_id:
            queryset = queryset.filter(id__lt=before_id)

        return queryset.order_by("-created_at")


class MessageEditView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        message = self.get_object()

        # Solo el autor puede editar
        if message.sender != request.user:
            return Response(
                {"detail": "No tienes permiso"},
                status=status.HTTP_403_FORBIDDEN,
            )

        new_content = request.data.get("content")
        if not new_content:
            return Response(
                {"detail": "Content es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message.content = new_content
        message.edited_at = timezone.now()
        message.save()

        return Response(self.get_serializer(message).data)
