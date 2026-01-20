from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model
from django.utils import timezone
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


class MessageEditView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        message = self.get_object()

        # Solo el autor puede editar
        if message.sender != request.user:
            return Response(
                {"detail": "No tienes permiso"}, status=status.HTTP_403_FORBIDDEN
            )

        new_content = request.data.get("content")
        if not new_content:
            return Response(
                {"detail": "Content es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        message.content = new_content
        message.edited_at = timezone.now()
        message.save()

        return Response(self.get_serializer(message).data)
