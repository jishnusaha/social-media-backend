# messages/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Max
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from account.models import EndUser
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationDetailSerializer
        return ConversationSerializer

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()

        # Mark messages as read when retrieving a conversation
        unread_messages = conversation.messages.exclude(sender=request.user).exclude(
            read_by=request.user
        )
        for message in unread_messages:
            message.mark_as_read(request.user)

        # Get message limit from query params
        message_limit = int(request.query_params.get("message_limit", 20))

        serializer = self.get_serializer(
            conversation, context={"request": request, "message_limit": message_limit}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def start_conversation(self, request):
        user_ids = request.data.get("participants", [])
        is_group = request.data.get("is_group", False)
        name = request.data.get("name")

        # Ensure request user is included in participants
        if request.user.id not in user_ids:
            user_ids.append(request.user.id)

        # Check if it's a direct message (between 2 people)
        if len(user_ids) == 2 and not is_group:
            user1 = request.user
            user2_id = [uid for uid in user_ids if uid != user1.id][0]
            user2 = get_object_or_404(EndUser, id=user2_id)

            # Get or create direct conversation
            conversation = Conversation.get_or_create_direct_conversation(user1, user2)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)

        # For group conversations
        if is_group:
            if not name:
                return Response(
                    {"detail": "Group conversations require a name."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create new group conversation
            conversation = Conversation.objects.create(is_group=True, name=name)

            # Add participants
            participants = EndUser.objects.filter(id__in=user_ids)
            conversation.participants.set(participants)

            serializer = self.get_serializer(conversation)
            return Response(serializer.data)

        return Response(
            {"detail": "Invalid conversation parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Only allow adding participants to group conversations
        if not conversation.is_group:
            return Response(
                {"detail": "Participants can only be added to group conversations."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(EndUser, id=user_id)
        conversation.participants.add(user)

        return Response(
            {"detail": f"{user.username} added to the conversation."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Only allow removing participants from group conversations
        if not conversation.is_group:
            return Response(
                {
                    "detail": "Participants can only be removed from group conversations."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(EndUser, id=user_id)

        # Don't allow removing the last participant
        if conversation.participants.count() <= 1:
            return Response(
                {"detail": "Cannot remove the last participant from a conversation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation.participants.remove(user)

        return Response(
            {"detail": f"{user.username} removed from the conversation."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        conversation = self.get_object()

        # Pagination parameters
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        # Get messages with pagination
        start = (page - 1) * page_size
        end = page * page_size
        messages = conversation.messages.order_by("-created_at")[start:end]

        serializer = MessageSerializer(
            messages, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        user = request.user
        conversations = self.get_queryset()

        # Calculate total unread messages across all conversations
        total_unread = 0
        for conversation in conversations:
            unread_count = (
                conversation.messages.exclude(sender=user).exclude(read_by=user).count()
            )
            total_unread += unread_count

        return Response({"unread_count": total_unread})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(conversation__participants=user).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        conversation = serializer.validated_data["conversation"]

        # Check if user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            raise serializers.ValidationError(
                {"detail": "You are not a participant in this conversation."}
            )

        serializer.save(sender=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        message.mark_as_read(request.user)
        return Response(
            {"detail": "Message marked as read."}, status=status.HTTP_200_OK
        )
