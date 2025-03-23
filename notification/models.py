# notifications/models.py
from django.db import models
from core.models import BaseModel
from account.models import EndUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(BaseModel):
    class NotificationType(models.TextChoices):
        FRIEND_REQUEST = "FRIEND_REQUEST", "Friend Request"
        FRIEND_ACCEPT = "FRIEND_ACCEPT", "Friend Request Accepted"
        POST_LIKE = "POST_LIKE", "Post Like"
        POST_COMMENT = "POST_COMMENT", "Post Comment"
        COMMENT_REPLY = "COMMENT_REPLY", "Comment Reply"
        COMMENT_LIKE = "COMMENT_LIKE", "Comment Like"
        MESSAGE = "MESSAGE", "New Message"
        MENTION = "MENTION", "Mention"
        SYSTEM = "SYSTEM", "System Notification"

    recipient = models.ForeignKey(
        EndUser, related_name="notifications", on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        EndUser,
        related_name="triggered_notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    # For linking to the related object (post, comment, friend request, etc.)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Additional data that might be needed for rendering the notification
    extra_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.title}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]
