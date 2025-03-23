# notifications/serializers.py
from rest_framework import serializers
from .models import Notification
from account.models import EndUser


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUser
        fields = ["id", "username", "first_name", "last_name"]


class NotificationSerializer(serializers.ModelSerializer):
    actor_details = ActorSerializer(source="actor", read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "created_at",
            "actor_details",
            "time_ago",
            "extra_data",
        ]
        read_only_fields = ["notification_type", "title", "message", "actor_details"]

    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif diff < timedelta(days=7):
            days = diff.days
            return f'{days} day{"s" if days != 1 else ""} ago'
        else:
            return obj.created_at.strftime("%b %d, %Y")
