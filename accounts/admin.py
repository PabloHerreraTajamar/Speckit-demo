"""
Django admin registration for accounts app.

This module registers the User and AuthenticationLog models with the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User, AuthenticationLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )


@admin.register(AuthenticationLog)
class AuthenticationLogAdmin(admin.ModelAdmin):
    """Admin interface for AuthenticationLog model."""

    list_display = ("user", "event_type", "ip_address", "timestamp", "success")
    list_filter = ("event_type", "success", "timestamp")
    search_fields = ("user__email", "user__username", "ip_address")
    readonly_fields = (
        "user",
        "event_type",
        "ip_address",
        "user_agent",
        "timestamp",
        "success",
        "metadata",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        """Prevent manual creation of authentication logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make authentication logs read-only."""
        return False
