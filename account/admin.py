from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AdminUser, EndUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "user_type", "is_verified", "joined_at")
    list_filter = ("user_type", "is_verified", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("-joined_at",)


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "is_active_admin")
    list_filter = ("role", "is_active_admin")
    search_fields = ("username", "email")
    ordering = ("-joined_at",)


@admin.register(EndUser)
class EndUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "status", "location")
    list_filter = ("status",)
    search_fields = ("username", "email", "location")
    ordering = ("-joined_at",)
