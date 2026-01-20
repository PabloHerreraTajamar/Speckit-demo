"""
Tests for Task model.
"""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from tasks.models import Task
from tests.tasks.factories import TaskFactory, UserFactory


@pytest.mark.django_db
class TestTaskModel:
    """Test cases for Task model."""

    def test_task_creation_with_required_fields(self):
        """Test creating task with only required fields."""
        user = UserFactory()
        task = Task.objects.create(title="Test Task", owner=user)

        assert task.title == "Test Task"
        assert task.owner == user
        assert task.priority == "media"  # Default
        assert task.status == "pendiente"  # Default
        assert task.description == ""
        assert task.due_date is None
        assert task.completed_at is None
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_creation_with_all_fields(self):
        """Test creating task with all fields."""
        user = UserFactory()
        task = Task.objects.create(
            title="Complete Project",
            description="Finish the Django project",
            owner=user,
            priority="alta",
            status="pendiente",
            due_date=timezone.now().date(),
        )

        assert task.title == "Complete Project"
        assert task.description == "Finish the Django project"
        assert task.priority == "alta"
        assert task.status == "pendiente"
        assert task.due_date is not None

    def test_task_title_validation_empty(self):
        """Test that empty title raises validation error."""
        user = UserFactory()
        task = Task(title="   ", owner=user)

        with pytest.raises(ValidationError) as exc:
            task.full_clean()

        assert "Title cannot be empty" in str(exc.value)

    def test_task_title_validation_too_long(self):
        """Test that title over 200 chars raises validation error."""
        user = UserFactory()
        task = Task(title="x" * 201, owner=user)

        with pytest.raises(ValidationError) as exc:
            task.full_clean()

        assert "Title cannot exceed 200 characters" in str(exc.value)

    def test_task_description_validation_too_long(self):
        """Test that description over 2000 chars raises validation error."""
        user = UserFactory()
        task = Task(title="Test", description="x" * 2001, owner=user)

        with pytest.raises(ValidationError) as exc:
            task.full_clean()

        assert "Description cannot exceed 2000 characters" in str(exc.value)

    def test_task_owner_foreign_key(self):
        """Test that task is linked to owner via foreign key."""
        user = UserFactory()
        task = TaskFactory(owner=user)

        assert task.owner == user
        assert task in user.tasks.all()

    def test_task_default_values(self):
        """Test default values for priority and status."""
        task = TaskFactory()

        assert task.priority == "media"
        assert task.status == "pendiente"

    def test_task_string_representation(self):
        """Test __str__ method."""
        task = TaskFactory(title="My Task", status="pendiente")

        assert str(task) == "My Task (Pendiente)"

    def test_completed_at_auto_set_on_completion(self):
        """Test that completed_at is auto-set when status changes to completada."""
        task = TaskFactory(status="pendiente")
        assert task.completed_at is None

        task.status = "completada"
        task.save()

        assert task.completed_at is not None
        assert isinstance(task.completed_at, type(timezone.now()))

    def test_completed_at_cleared_when_reopened(self):
        """Test that completed_at is cleared when status changes back to pendiente."""
        task = TaskFactory(status="completada")
        task.save()  # This should set completed_at

        assert task.completed_at is not None

        task.status = "pendiente"
        task.save()

        assert task.completed_at is None

    def test_task_ordering(self):
        """Test that tasks are ordered by created_at descending (newest first)."""
        user = UserFactory()
        task1 = TaskFactory(owner=user, title="Old Task")
        task2 = TaskFactory(owner=user, title="New Task")

        tasks = Task.objects.filter(owner=user)

        assert tasks[0] == task2  # Newest first
        assert tasks[1] == task1
