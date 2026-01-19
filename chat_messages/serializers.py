from rest_framework import serializers
from .models import Message
from users.serializers import UserListSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserListSerializer(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True)  # solo para input

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "created_at", "recipient_id"]
        read_only_fields = ["id", "sender", "created_at"]

    def create(self, validated_data):
        # Quitamos recipient_id porque no pertenece al modelo
        validated_data.pop("recipient_id", None)
        return super().create(validated_data)
