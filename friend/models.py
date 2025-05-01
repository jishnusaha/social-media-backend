# friends/models.py
from django.db import models
from core.models import BaseModel
from account.models import EndUser
from django.db.models import Q


class FriendRequest(BaseModel):

    sender = models.ForeignKey(
        EndUser, related_name="sent_friend_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        EndUser, related_name="received_friend_requests", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("sender", "receiver")

    def __str__(self):
        return f"{self.sender.email} → {self.receiver.email}"


class Friendship(BaseModel):
    user1 = models.ForeignKey(
        EndUser, related_name="friendships1", on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        EndUser, related_name="friendships2", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"

    @classmethod
    def are_friends(cls, user1, user2):
        return cls.objects.filter(
            (Q(user1=user1) & Q(user2=user2)) | (Q(user1=user2) & Q(user2=user1))
        ).exists()

    @classmethod
    def get_friends(cls, user):
        # Get all friendships involving the user
        friendships = cls.objects.filter(Q(user1=user) | Q(user2=user))

        # Extract the friend from each friendship
        friends = []
        for friendship in friendships:
            if friendship.user1 == user:
                friends.append(friendship.user2)
            else:
                friends.append(friendship.user1)

        return friends
