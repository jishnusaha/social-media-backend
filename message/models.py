# messages/models.py
from django.db import models
from core.models import BaseModel
from account.models import EndUser
from django.db.models import Q


class Conversation(BaseModel):
    participants = models.ManyToManyField(EndUser, related_name="conversations")
    is_group = models.BooleanField(default=False)
    name = models.CharField(
        max_length=255, blank=True, null=True
    )  # For group conversations

    def __str__(self):
        if self.is_group and self.name:
            return f"Group: {self.name}"

        participant_names = ", ".join(
            [user.username for user in self.participants.all()[:3]]
        )
        if self.participants.count() > 3:
            participant_names += f" and {self.participants.count() - 3} more"

        return f"Conversation: {participant_names}"

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()

    @classmethod
    def get_or_create_direct_conversation(cls, user1, user2):
        # Look for existing direct conversation between these users
        conversations = (
            cls.objects.filter(is_group=False)
            .filter(participants=user1)
            .filter(participants=user2)
        )

        # Check if there's an existing conversation with exactly 2 participants
        for conv in conversations:
            if conv.participants.count() == 2:
                return conv

        # Create new conversation if none exists
        conversation = cls.objects.create(is_group=False)
        conversation.participants.add(user1, user2)
        return conversation


class Message(BaseModel):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        EndUser, related_name="sent_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(EndUser, related_name="read_messages", blank=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation}"

    class Meta:
        ordering = ["created_at"]

    def mark_as_read(self, user):
        if user != self.sender and user in self.conversation.participants.all():
            self.read_by.add(user)
            # If all participants have read the message, mark it as read
            if (
                self.read_by.count() == self.conversation.participants.count() - 1
            ):  # Exclude sender
                self.is_read = True
                self.save()

