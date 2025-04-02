from rest_framework.permissions import BasePermission
from account.models import CustomUser  # Adjust the import path if needed


class IsEndUser(BasePermission):
    """
    Custom permission to allow only END_USER to create posts.
    """

    def has_permission(self, request, view):

        # Allow only END_USER to create/update posts
        return (
            request.user.is_authenticated
            and request.user.user_type == CustomUser.UserType.END_USER
        )


class IsAdminUser(BasePermission):
    """
    Custom permission to allow only END_USER to create posts.
    """

    def has_permission(self, request, view):

        # Allow only END_USER to create/update posts
        return (
            request.user.is_authenticated
            and request.user.user_type == CustomUser.UserType.ADMIN
        )
