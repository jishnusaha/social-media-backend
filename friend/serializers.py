from rest_framework import serializers
from .models import FriendRequest, Friendship
from account.models import EndUser


class EndUserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUser
        fields = ["id", "username", "first_name", "last_name"]


class FriendRequestSerializer(serializers.ModelSerializer):
    sender_details = EndUserMinimalSerializer(source="sender", read_only=True)
    receiver_details = EndUserMinimalSerializer(source="receiver", read_only=True)

    class Meta:
        model = FriendRequest
        fields = [
            "id",
            "sender",
            "receiver",
            "created_at",
            "sender_details",
            "receiver_details",
        ]
        read_only_fields = ["sender"]

    def validate(self, data):
        sender = self.context["request"].user.enduser
        receiver = data.get("receiver")

        if sender == receiver:
            raise serializers.ValidationError(
                "You cannot send a friend request to yourself."
            )

        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError("Friend request already sent.")

        if FriendRequest.objects.filter(sender=receiver, receiver=sender).exists():
            raise serializers.ValidationError(
                "This user has already sent you a friend request."
            )

        if Friendship.are_friends(sender, receiver):
            raise serializers.ValidationError("You are already friends with this user.")

        return data


class FriendshipSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ["id", "friend"]

    def get_friend(self, obj):
        request = self.context.get("request")
        user = request.user

        if obj.user1 == user:
            friend = obj.user2
        else:
            friend = obj.user1

        return EndUserMinimalSerializer(friend).data
