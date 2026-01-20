from rest_framework import generics, permissions
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model
from rooms.models import Room, RoomParticipant
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()


class MessageListPagination(LimitOffsetPagination):
    default_limit = 10  # por defecto trae 10 mensajes
    max_limit = 50  # máximo que se puede pedir


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipient_id = self.request.data.get("recipient_id")
        content = self.request.data.get("content")

        recipient = User.objects.get(id=recipient_id)
        sender = self.request.user

        # Verificar si ya existe room 1 a 1
        room = Room.objects.filter(users=sender).filter(users=recipient).first()
        if not room:
            room = Room.objects.create()
            RoomParticipant.objects.create(user=sender, room=room)
            RoomParticipant.objects.create(user=recipient, room=room)

        # Crear mensaje en esa room
        serializer.save(sender=sender, room=room, content=content)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessageListPagination

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return Message.objects.filter(
            room_id=room_id,
            room__participants__user=self.request.user,
            room__participants__is_active=True,
        ).order_by("-created_at")
