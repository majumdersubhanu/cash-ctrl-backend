import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("INFO", "Information"),
        ("WARNING", "Warning"),
        ("ALERT", "Critical Alert"),
        ("SUCCESS", "Success"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )

    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default="INFO")
    title = models.CharField(max_length=255)
    message = models.TextField()

    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.user.email}"
