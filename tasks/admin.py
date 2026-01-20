"""
Django admin configuration for tasks app.
"""

from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""

    list_display = ["title", "owner", "priority", "status", "due_date", "created_at"]
    list_filter = ["status", "priority", "created_at"]
    search_fields = ["title", "description", "owner__email"]
    readonly_fields = ["created_at", "updated_at", "completed_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Task Information", {"fields": ("title", "description", "owner")}),
        ("Task Details", {"fields": ("priority", "status", "due_date")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
    )
