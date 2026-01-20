from django.db import models
from django.conf import settings


class Room(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="RoomParticipant",
        related_name="rooms",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id}"


class RoomParticipant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="room_participations",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    is_active = models.BooleanField(default=True)
