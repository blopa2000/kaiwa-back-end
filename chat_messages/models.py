from django.db import models
from django.conf import settings
from rooms.models import Room


class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender_id}: {self.content[:20]}"
