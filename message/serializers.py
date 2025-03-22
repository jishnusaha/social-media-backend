# messages/serializers.py
from rest_framework import serializers
from .models import Conversation, Message
from account.models import EndUser


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUser
        fields = ["id", "username", "first_name", "last_name"]


class MessageSerializer(serializers.ModelSerializer):
    sender_details = ParticipantSerializer(source="sender", read_only=True)
    is_sender = serializers.SerializerMethodField()
    read_by_list = ParticipantSerializer(source="read_by", read_only=True, many=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "content",
            "created_at",
            "is_read",
            "sender_details",
            "is_sender",
            "read_by_list",
        ]
        read_only_fields = ["sender", "is_read"]

    def get_is_sender(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False


class ConversationSerializer(serializers.ModelSerializer):
    participants_details = ParticipantSerializer(
        source="participants", many=True, read_only=True
    )
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "is_group",
            "name",
            "created_at",
            "participants_details",
            "last_message_preview",
            "unread_count",
            "display_name",
        ]
        read_only_fields = ["is_group", "last_message_preview", "unread_count"]

    def get_last_message_preview(self, obj):
        last_message = obj.last_message
        if last_message:
            return {
                "content": last_message.content[:50]
                + ("..." if len(last_message.content) > 50 else ""),
                "sender": last_message.sender.username,
                "created_at": last_message.created_at,
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return (
                obj.messages.exclude(sender=request.user)
                .exclude(read_by=request.user)
                .count()
            )
        return 0

    def get_display_name(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        if obj.is_group:
            return obj.name or "Group Chat"

        # For direct conversations, show the other participant's name
        other_participants = obj.participants.exclude(id=request.user.id)
        if other_participants.exists():
            other_user = other_participants.first()
            return (
                f"{other_user.first_name} {other_user.last_name}"
                if other_user.first_name
                else other_user.username
            )

        return "Chat"


class ConversationDetailSerializer(ConversationSerializer):
    messages = serializers.SerializerMethodField()

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ["messages"]

    def get_messages(self, obj):
        # Get the last 20 messages by default
        limit = self.context.get("message_limit", 20)
        messages = obj.messages.order_by("-created_at")[:limit]
        return MessageSerializer(messages, many=True, context=self.context).data
