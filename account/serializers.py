from rest_framework import serializers
from .models import AdminUser, EndUser


class EndUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(read_only=True)  # will be auto generated
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = EndUser
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = EndUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = (
            "id",
            "username",
            "email",
            "role",
            "assigned_sections",
            "is_active_admin",
        )


class EndUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndUser
        fields = (
            "id",
            "username",
            "email",
            "bio",
            "location",
            "website",
            "status",
        )
