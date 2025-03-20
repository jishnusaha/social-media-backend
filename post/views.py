# posts/views.py
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Post, Comment, Reaction
from .serializers import (
    PostSerializer,
    PostDetailSerializer,
    CommentSerializer,
    ReactionSerializer,
)
from friends.models import Friendship


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        # Base queryset - excludes archived posts
        queryset = Post.objects.filter(is_archived=False)

        # Filter to only show posts the user should see
        user = self.request.user

        # For non-public posts, only show posts from friends
        friends = Friendship.get_friends(user)
        friend_ids = [friend.id for friend in friends]

        # Show all public posts and private posts from friends
        queryset = queryset.filter(
            Q(is_public=True)
            | (Q(is_public=False) & Q(author_id__in=friend_ids))
            | Q(author=user)  # Always show the user's own posts
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        post = self.get_object()
        reaction_type = request.data.get("reaction_type")

        if not reaction_type or reaction_type not in dict(
            Reaction.ReactionType.choices
        ):
            return Response(
                {
                    "detail": f"Invalid reaction type. Choose from {dict(Reaction.ReactionType.choices).keys()}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user already reacted to this post
        existing_reaction = Reaction.objects.filter(
            user=request.user, post=post
        ).first()

        if existing_reaction:
            # Update existing reaction
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
            message = "Reaction updated."
        else:
            # Create new reaction
            Reaction.objects.create(
                user=request.user, post=post, reaction_type=reaction_type
            )
            message = "Reaction added."

        return Response({"detail": message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"])
    def unreact(self, request, pk=None):
        post = self.get_object()

        # Find and delete the reaction
        reaction = Reaction.objects.filter(user=request.user, post=post).first()

        if not reaction:
            return Response(
                {"detail": "No reaction found."}, status=status.HTTP_404_NOT_FOUND
            )

        reaction.delete()
        return Response({"detail": "Reaction removed."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def reactions(self, request, pk=None):
        post = self.get_object()
        reactions = post.reactions.all()

        # Optional filtering by reaction type
        reaction_type = request.query_params.get("type")
        if reaction_type:
            reactions = reactions.filter(reaction_type=reaction_type)

        serializer = ReactionSerializer(reactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def user_posts(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response(
                {"detail": "Username parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(author__username=username)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def trending(self, request):
        # Get posts with most reactions and comments in the last 7 days
        from django.utils import timezone
        from datetime import timedelta

        last_week = timezone.now() - timedelta(days=7)

        # Calculate trending score based on reactions and comments
        queryset = self.get_queryset().filter(created_at__gte=last_week)

        queryset = queryset.annotate(
            reaction_count=Count("reactions"), comment_count=Count("comments")
        ).order_by("-reaction_count", "-comment_count")[:10]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        # Soft delete by setting flag instead of actual deletion
        comment.is_deleted = True
        comment.content = "[This comment has been deleted]"
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        comment = self.get_object()
        reaction_type = request.data.get("reaction_type")

        if not reaction_type or reaction_type not in dict(
            Reaction.ReactionType.choices
        ):
            return Response(
                {
                    "detail": f"Invalid reaction type. Choose from {dict(Reaction.ReactionType.choices).keys()}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user already reacted to this comment
        existing_reaction = Reaction.objects.filter(
            user=request.user, comment=comment
        ).first()

        if existing_reaction:
            # Update existing reaction
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
            message = "Reaction updated."
        else:
            # Create new reaction
            Reaction.objects.create(
                user=request.user, comment=comment, reaction_type=reaction_type
            )
            message = "Reaction added."

        return Response({"detail": message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"])
    def unreact(self, request, pk=None):
        comment = self.get_object()

        # Find and delete the reaction
        reaction = Reaction.objects.filter(user=request.user, comment=comment).first()

        if not reaction:
            return Response(
                {"detail": "No reaction found."}, status=status.HTTP_404_NOT_FOUND
            )

        reaction.delete()
        return Response({"detail": "Reaction removed."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def reactions(self, request, pk=None):
        comment = self.get_object()
        reactions = comment.reactions.all()

        # Optional filtering by reaction type
        reaction_type = request.query_params.get("type")
        if reaction_type:
            reactions = reactions.filter(reaction_type=reaction_type)

        serializer = ReactionSerializer(reactions, many=True)
        return Response(serializer.data)
