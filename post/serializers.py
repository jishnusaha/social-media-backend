# posts/serializers.py
from rest_framework import serializers
from .models import Post, Comment, Reaction
from account.models import EndUser


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUser
        fields = ["id", "username", "first_name", "last_name"]


class ReactionSerializer(serializers.ModelSerializer):
    user_details = AuthorSerializer(source="user", read_only=True)

    class Meta:
        model = Reaction
        fields = ["id", "user", "reaction_type", "created_at", "user_details"]
        read_only_fields = ["user"]


class CommentSerializer(serializers.ModelSerializer):
    author_details = AuthorSerializer(source="author", read_only=True)
    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "content",
            "created_at",
            "parent",
            "author_details",
            "reactions_count",
            "user_reaction",
            "replies",
        ]
        read_only_fields = ["author"]

    def get_reactions_count(self, obj):
        return {
            reaction_type: obj.reactions.filter(reaction_type=reaction_type).count()
            for reaction_type, _ in Reaction.ReactionType.choices
        }

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None

    def get_replies(self, obj):
        # Only get direct replies, not nested ones
        replies = obj.replies.filter(is_deleted=False)
        return CommentShallowSerializer(replies, many=True, context=self.context).data


class CommentShallowSerializer(serializers.ModelSerializer):
    """A simpler version of CommentSerializer to avoid infinite recursion"""

    author_details = AuthorSerializer(source="author", read_only=True)
    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "content",
            "created_at",
            "author_details",
            "reactions_count",
            "user_reaction",
        ]

    def get_reactions_count(self, obj):
        return {
            reaction_type: obj.reactions.filter(reaction_type=reaction_type).count()
            for reaction_type, _ in Reaction.ReactionType.choices
        }

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None


class PostSerializer(serializers.ModelSerializer):
    author_details = AuthorSerializer(source="author", read_only=True)
    comments_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "is_public",
            "created_at",
            "author_details",
            "comments_count",
            "reactions_count",
            "user_reaction",
        ]
        read_only_fields = ["author"]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_reactions_count(self, obj):
        return {
            reaction_type: obj.reactions.filter(reaction_type=reaction_type).count()
            for reaction_type, _ in Reaction.ReactionType.choices
        }

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None


class PostDetailSerializer(PostSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ["comments"]

    def get_comments(self, obj):
        # Only get top-level comments (no parent)
        comments = obj.comments.filter(parent=None, is_deleted=False)
        return CommentSerializer(comments, many=True, context=self.context).data
