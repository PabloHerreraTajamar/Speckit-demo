"""
Custom managers and querysets for Task model.
"""

from django.db import models


class TaskQuerySet(models.QuerySet):
    """Custom queryset for Task model with filter/sort methods."""

    def for_user(self, user):
        """
        Return tasks owned by specific user.

        Args:
            user: User instance

        Returns:
            QuerySet filtered by owner
        """
        return self.filter(owner=user)

    def pending(self):
        """Return pending tasks."""
        return self.filter(status="pendiente")

    def completed(self):
        """Return completed tasks."""
        return self.filter(status="completada")

    def high_priority(self):
        """Return high priority tasks."""
        return self.filter(priority="alta")

    def by_due_date(self):
        """Sort by due date (nulls last)."""
        return self.order_by(models.F("due_date").asc(nulls_last=True))

    def by_priority(self):
        """Sort by priority (alta, media, baja)."""
        priority_order = models.Case(
            models.When(priority="alta", then=1),
            models.When(priority="media", then=2),
            models.When(priority="baja", then=3),
        )
        return self.order_by(priority_order)


class TaskManager(models.Manager):
    """Custom manager for Task model."""

    def get_queryset(self):
        """Return custom queryset."""
        return TaskQuerySet(self.model, using=self._db)

    def for_user(self, user):
        """Return tasks for specific user."""
        return self.get_queryset().for_user(user)
