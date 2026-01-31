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
        # Intentar obtener user de REST
        user = None
        request = self.context.get("request")
        if request:
            user = getattr(request, "user", None)

        # Si no hay user, intentar obtener de context (WS)
        if not user:
            user = self.context.get("user")

        # Si todavía no hay user, devolvemos None
        if not user or not user.is_authenticated:
            return None

        # Obtener el otro usuario de la room
        other_participant = (
            obj.participants.exclude(user=user).select_related("user").first()
        )
        return (
            UserListSerializer(other_participant.user).data
            if other_participant
            else None
        )

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last_msg).data if last_msg else None
