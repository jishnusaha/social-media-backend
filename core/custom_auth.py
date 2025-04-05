from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            if not user:
                msg = "Unable to log in with provided credentials."
                raise ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "email" and "password".'
            raise ValidationError(msg, code="authorization")

        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
        }

        return data


class EmailBackend(ModelBackend):
    """
    Authenticate using email only.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # If someone tries to login with username parameter, treat it as email
        # This is necessary because Django's auth views use 'username' parameter
        email = kwargs.get("email") or username

        if email is None:
            return None

        try:
            # Only lookup users by email
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user
            User().set_password(password)
            return None

    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None
