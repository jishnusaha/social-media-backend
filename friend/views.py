# friends/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import FriendRequest, Friendship
from account.models import EndUser
from .serializers import (
    FriendRequestSerializer,
    FriendshipSerializer,
    EndUserMinimalSerializer,
)


class FriendRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.enduser
        return FriendRequest.objects.filter(Q(sender=user) | Q(receiver=user)).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user.enduser)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        friend_request = self.get_object()

        # Check if the current user is the receiver
        if friend_request.receiver != request.user.enduser:
            return Response(
                {"detail": "You can only accept requests sent to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        Friendship.objects.get_or_create(
            user1=friend_request.sender, user2=friend_request.receiver
        )

        friend_request.delete()

        return Response(
            {
                "detail": "Friend request accepted successfully.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def received(self, request):
        user = request.user.enduser
        queryset = FriendRequest.objects.filter(receiver=user).order_by("-created_at")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        user = request.user.enduser
        queryset = FriendRequest.objects.filter(sender=user).order_by("-created_at")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FriendshipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.enduser
        return Friendship.objects.filter(Q(user1=user) | Q(user2=user))

    @action(detail=False, methods=["delete"])
    def unfriend(self, request):
        friend_id = request.data.get("friend_id")
        if not friend_id:
            return Response(
                {"detail": "friend_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        friend = get_object_or_404(EndUser, id=friend_id)
        user = request.user.enduser

        # Find and delete the friendship
        friendship = Friendship.objects.filter(
            (Q(user1=user) & Q(user2=friend)) | (Q(user1=friend) & Q(user2=user))
        ).first()

        if not friendship:
            return Response(
                {"detail": "You are not friends with this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        friendship.delete()
        return Response(
            {"detail": "Unfriended successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        user = request.user.enduser

        # Get current friends
        friends = Friendship.get_friends(user)
        friend_ids = [friend.id for friend in friends]

        # Get users who are not friends
        potential_friends = EndUser.objects.exclude(id__in=friend_ids + [user.id])[
            :10
        ]  # Limit to 10 suggestions

        serializer = EndUserMinimalSerializer(potential_friends, many=True)
        return Response(serializer.data)
