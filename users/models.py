from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to="users/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return str(self.username)


class UserStatus(models.Model):
    STATUS_CHOICES = (
        ("online", "Online"),
        ("offline", "Offline"),
        ("typing", "Typing"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="status")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="offline")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.status}"
