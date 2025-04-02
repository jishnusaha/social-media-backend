import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from core.validators import validate_not_empty


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", CustomUser.UserType.ADMIN)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):

    class UserType(models.TextChoices):
        ADMIN = "ADMIN", _("ADMIN")
        END_USER = "END_USER", _("END_USER")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_type = models.CharField(max_length=20, choices=UserType.choices)
    email = models.EmailField(
        max_length=100, unique=True, validators=[validate_not_empty]
    )
    # TODO: implement file storage later
    # profile_picture = models.ImageField(
    #     upload_to="profile_pics/", blank=True, null=True
    # )
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class AdminUser(CustomUser):
    # ADMIN USER MAY BE TO OPERATE SOMETHING
    role = models.CharField(
        max_length=50,
        choices=[("SUPER_ADMIN", "Super Admin"), ("MODERATOR", "Moderator")],
    )
    assigned_sections = models.JSONField(
        default=list
    )  # Sections or topics an admin manages
    is_active_admin = models.BooleanField(default=True)  # Track if the admin is active

    class Meta:
        db_table = "admin_user"

    def save(self, *args, **kwargs):
        self.user_type = CustomUser.UserType.ADMIN  # Ensure user_type is ADMIN
        super().save(*args, **kwargs)


class EndUser(CustomUser):
    # WHO WILL ACTUALLY USE THE SOCIAL MEDIA
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive"), ("BANNED", "Banned")],
        default="ACTIVE",
    )

    class Meta:
        db_table = "end_user"

    def save(self, *args, **kwargs):
        self.user_type = CustomUser.UserType.END_USER  # Ensure user_type is END_USER
        super().save(*args, **kwargs)
