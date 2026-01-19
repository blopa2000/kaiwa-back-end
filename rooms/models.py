from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Room(models.Model):
    users = models.ManyToManyField(
        User, through="RoomParticipant", related_name="rooms"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id}"


class RoomParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # si el usuario eliminó la room
