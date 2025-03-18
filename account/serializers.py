from rest_framework import serializers
from .models import AdminUser, EndUser


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
