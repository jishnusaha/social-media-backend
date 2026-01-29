# posts/models.py
from django.db import models
from core.models import BaseModel
from account.models import EndUser


class Post(BaseModel):
    author = models.ForeignKey(EndUser, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.username}'s post: {self.content[:50]}..."

    class Meta:
        ordering = ["-created_at"]


class Comment(BaseModel):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(
        EndUser, related_name="comments", on_delete=models.CASCADE
    )
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"

    class Meta:
        ordering = ["created_at"]


class Reaction(BaseModel):
    class ReactionType(models.TextChoices):
        LIKE = "LIKE", "Like"
        LOVE = "LOVE", "Love"
        LAUGH = "LAUGH", "Laugh"
        WOW = "WOW", "Wow"
        SAD = "SAD", "Sad"
        ANGRY = "ANGRY", "Angry"

    user = models.ForeignKey(
        EndUser, related_name="reactions", on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, related_name="reactions", on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        Comment,
        related_name="reactions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reaction_type = models.CharField(
        max_length=10, choices=ReactionType.choices, default=ReactionType.LIKE
    )

    class Meta:
        unique_together = [("user", "post"), ("user", "comment")]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(post__isnull=False)
                | models.Q(comment__isnull=False),
                name="reaction_has_post_or_comment",
            ),
            models.CheckConstraint(
                condition=~(
                    models.Q(post__isnull=False) & models.Q(comment__isnull=False)
                ),
                name="reaction_not_both_post_and_comment",
            ),
        ]

    def __str__(self):
        if self.post:
            return f"{self.user.username} {self.reaction_type} on {self.post}"
        return f"{self.user.username} {self.reaction_type} on comment {self.comment.id}"
