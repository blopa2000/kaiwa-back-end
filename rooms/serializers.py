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
        request_user = self.context["request"].user
        other = obj.users.exclude(id=request_user.id).first()
        return UserListSerializer(other).data if other else None

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last_msg).data if last_msg else None
