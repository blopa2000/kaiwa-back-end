from rest_framework import serializers
from .models import Room
from chat_messages.serializers import MessageSerializer
from users.serializers import UserListSerializer


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "other_user", "last_message", "created_at"]

    def get_other_user(self, obj):
        request = self.context.get("request")
        user = None

        if request and hasattr(request, "user"):
            user = request.user
        else:
            user = self.context.get("user")

        if not user or not user.is_authenticated:
            return None
        # Obtener el otro usuario de la room
        participants = obj.participants.select_related("user")

        other_participant = next(
            (p for p in participants if p.user_id != user.id), None
        )
        return (
            UserListSerializer(other_participant.user).data
            if other_participant
            else None
        )

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last_msg).data if last_msg else None
