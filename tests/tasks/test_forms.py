"""
Tests for Task forms.
"""

import pytest
from django.utils import timezone

from tasks.forms import TaskForm
from tests.tasks.factories import TaskFactory, UserFactory


@pytest.mark.django_db
class TestTaskForm:
    """Test cases for TaskForm."""

    def test_task_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            "title": "Test Task",
            "description": "Test description",
            "priority": "high",
            "status": "pending",
            "due_date": timezone.now().date(),
        }
        form = TaskForm(data=form_data)

        assert form.is_valid()

    def test_task_form_required_field_title(self):
        """Test that title is required."""
        form_data = {
            "description": "Test description",
            "priority": "medium",
            "status": "pending",
        }
        form = TaskForm(data=form_data)

        assert not form.is_valid()
        assert "title" in form.errors

    def test_task_form_empty_title(self):
        """Test that empty/whitespace title is invalid."""
        form_data = {"title": "   ", "priority": "medium", "status": "pending"}
        form = TaskForm(data=form_data)

        assert not form.is_valid()

    def test_task_form_title_max_length(self):
        """Test that title exceeding 200 chars is invalid."""
        form_data = {"title": "x" * 201, "priority": "medium", "status": "pending"}
        form = TaskForm(data=form_data)

        assert not form.is_valid()
        assert "title" in form.errors

    def test_task_form_description_max_length(self):
        """Test that description exceeding 2000 chars is invalid."""
        form_data = {
            "title": "Test Task",
            "description": "x" * 2001,
            "priority": "medium",
            "status": "pending",
        }
        form = TaskForm(data=form_data)

        assert not form.is_valid()
        assert "description" in form.errors

    def test_task_form_optional_description(self):
        """Test that description is optional."""
        form_data = {"title": "Test Task", "priority": "medium", "status": "pending"}
        form = TaskForm(data=form_data)

        assert form.is_valid()

    def test_task_form_optional_due_date(self):
        """Test that due_date is optional."""
        form_data = {"title": "Test Task", "priority": "medium", "status": "pending"}
        form = TaskForm(data=form_data)

        assert form.is_valid()

    def test_task_form_excludes_owner(self):
        """Test that owner field is not in form."""
        form = TaskForm()

        assert "owner" not in form.fields

    def test_task_form_priority_choices(self):
        """Test that priority has correct choices."""
        form = TaskForm()

        priority_choices = [choice[0] for choice in form.fields["priority"].choices]
        assert "high" in priority_choices
        assert "medium" in priority_choices
        assert "low" in priority_choices

    def test_task_form_status_choices(self):
        """Test that status has correct choices."""
        form = TaskForm()

        status_choices = [choice[0] for choice in form.fields["status"].choices]
        assert "pending" in status_choices
        assert "completed" in status_choices

    def test_task_form_save(self):
        """Test saving form creates task instance."""
        user = UserFactory()
        form_data = {
            "title": "Test Task",
            "description": "Test description",
            "priority": "high",
            "status": "pending",
        }
        form = TaskForm(data=form_data)

        assert form.is_valid()

        task = form.save(commit=False)
        task.owner = user
        task.save()

        assert task.title == "Test Task"
        assert task.owner == user
