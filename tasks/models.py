"""
Task model for task management.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from .managers import TaskManager
from .validators import validate_description_length, validate_title_length


class Task(models.Model):
    """
    Task model representing a user's personal task.

    Attributes:
        title: Task title (required, max 200 chars)
        description: Task description (optional, max 2000 chars)
        due_date: Due date (optional)
        priority: Priority level (alta/media/baja)
        status: Current status (pendiente/completada)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp (auto-set)
        owner: Task owner (Foreign Key to User)
    """

    PRIORITY_CHOICES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]

    STATUS_CHOICES = [
        ("pendiente", "Pendiente"),
        ("completada", "Completada"),
    ]

    # Required fields
    title = models.CharField(
        max_length=200,
        validators=[validate_title_length],
        help_text="Task title (max 200 chars)",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Task owner (immutable)",
    )

    # Optional fields
    description = models.TextField(
        max_length=2000,
        blank=True,
        validators=[validate_description_length],
        help_text="Task description (max 2000 chars)",
    )
    due_date = models.DateField(
        null=True, blank=True, help_text="Task due date (optional)"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="media", db_index=True
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pendiente", db_index=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when task was completed"
    )

    # Custom manager
    objects = TaskManager()

    class Meta:
        db_table = "tasks_task"
        ordering = ["-created_at"]  # Newest first
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "priority"]),
            models.Index(fields=["owner", "due_date"]),
        ]

    def save(self, *args, **kwargs):
        """
        Auto-update completed_at timestamp.

        Sets completed_at when status changes to 'completada'.
        Clears completed_at when status changes to 'pendiente'.
        """
        if self.status == "completada" and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status == "pendiente":
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of task."""
        return f"{self.title} ({self.get_status_display()})"
