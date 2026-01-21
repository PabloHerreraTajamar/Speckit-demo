"""
Tests for Task views.
"""

import pytest
from django.urls import reverse

from tasks.models import Task
from tests.tasks.factories import TaskFactory, UserFactory


@pytest.mark.django_db
class TestTaskCreateView:
    """Test cases for TaskCreateView."""

    def test_create_view_requires_authentication(self, client):
        """Test that create view requires login."""
        url = reverse("tasks:create")
        response = client.get(url)

        assert response.status_code == 302  # Redirect to login
        assert "/accounts/login/" in response.url

    def test_create_view_get_authenticated(self, client):
        """Test GET request to create view when authenticated."""
        user = UserFactory(password="testpass123")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:create")
        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context

    def test_create_view_post_valid_data(self, client):
        """Test POST request with valid data creates task."""
        user = UserFactory(password="testpass123")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:create")

        data = {
            "title": "New Task",
            "description": "Task description",
            "priority": "high",
            "status": "pending",
        }
        response = client.post(url, data)

        assert response.status_code == 302  # Redirect after success
        assert Task.objects.filter(title="New Task").exists()

        task = Task.objects.get(title="New Task")
        assert task.owner == user  # Owner auto-set

    def test_create_view_post_invalid_data(self, client):
        """Test POST request with invalid data shows errors."""
        user = UserFactory(password="testpass123")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:create")

        data = {"title": "", "priority": "medium", "status": "pending"}  # Empty title
        response = client.post(url, data)

        assert response.status_code == 200  # Re-render form
        assert "form" in response.context
        assert response.context["form"].errors
        assert not Task.objects.filter(owner=user).exists()

    def test_create_view_owner_auto_set(self, client):
        """Test that owner is automatically set to logged-in user."""
        user = UserFactory(password="testpass123")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:create")

        data = {"title": "Auto Owner Task", "priority": "medium", "status": "pending"}
        response = client.post(url, data)

        task = Task.objects.get(title="Auto Owner Task")
        assert task.owner == user

    def test_create_view_success_message(self, client):
        """Test that success message is displayed after creating task."""
        user = UserFactory(password="testpass123")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:create")

        data = {
            "title": "Task with Message",
            "priority": "medium",
            "status": "pending",
        }
        response = client.post(url, data, follow=True)

        messages = list(response.context["messages"])
        assert len(messages) > 0
        assert "created successfully" in str(messages[0]).lower()


@pytest.mark.django_db
class TestTaskListView:
    """Test cases for TaskListView."""

    def test_list_view_requires_authentication(self, client):
        """Test that list view requires login."""
        url = reverse("tasks:list")
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_list_view_shows_user_tasks_only(self, client):
        """Test that users only see their own tasks."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory(password="testpass123")

        task1 = TaskFactory(owner=user1, title="User 1 Task")
        task2 = TaskFactory(owner=user2, title="User 2 Task")

        client.login(username=user1.email, password="testpass123")
        url = reverse("tasks:list")
        response = client.get(url)

        assert response.status_code == 200
        assert task1 in response.context["tasks"]
        assert task2 not in response.context["tasks"]

    def test_list_view_filter_by_status(self, client):
        """Test filtering tasks by status."""
        user = UserFactory(password="testpass123")
        task1 = TaskFactory(owner=user, status="pending")
        task2 = TaskFactory(owner=user, status="completed")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:list") + "?status=pending"
        response = client.get(url)

        tasks = list(response.context["tasks"])
        assert task1 in tasks
        assert task2 not in tasks

    def test_list_view_filter_by_priority(self, client):
        """Test filtering tasks by priority."""
        user = UserFactory(password="testpass123")
        task1 = TaskFactory(owner=user, priority="high")
        task2 = TaskFactory(owner=user, priority="low")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:list") + "?priority=high"
        response = client.get(url)

        tasks = list(response.context["tasks"])
        assert task1 in tasks
        assert task2 not in tasks

    def test_list_view_statistics(self, client):
        """Test that statistics are displayed correctly."""
        user = UserFactory(password="testpass123")
        TaskFactory.create_batch(3, owner=user, status="pending")
        TaskFactory.create_batch(2, owner=user, status="completed")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:list")
        response = client.get(url)

        assert response.context["total_tasks"] == 5
        assert response.context["pending_count"] == 3
        assert response.context["completed_count"] == 2

    def test_list_view_pagination(self, client):
        """Test that pagination works correctly."""
        user = UserFactory(password="testpass123")
        TaskFactory.create_batch(25, owner=user)

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:list")
        response = client.get(url)

        assert response.context["is_paginated"]
        assert len(response.context["tasks"]) == 20

    def test_list_view_empty_state(self, client):
        """Test empty state when no tasks exist."""
        user = UserFactory(password="testpass123")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:list")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["tasks"]) == 0


@pytest.mark.django_db
class TestTaskDetailView:
    """Test cases for TaskDetailView."""

    def test_detail_view_requires_authentication(self, client):
        """Test that detail view requires login."""
        task = TaskFactory()
        url = reverse("tasks:detail", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_detail_view_shows_task(self, client):
        """Test that task details are displayed."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user, title="Test Task")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:detail", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["task"] == task

    def test_detail_view_denies_other_users(self, client):
        """Test that users cannot view other users' tasks."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory(password="testpass123")
        task = TaskFactory(owner=user2)

        client.login(username=user1.email, password="testpass123")
        url = reverse("tasks:detail", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestTaskUpdateView:
    """Test cases for TaskUpdateView."""

    def test_update_view_requires_authentication(self, client):
        """Test that update view requires login."""
        task = TaskFactory()
        url = reverse("tasks:edit", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_update_view_get_authenticated(self, client):
        """Test GET request to update view."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:edit", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["task"] == task

    def test_update_view_post_valid_data(self, client):
        """Test POST request with valid data updates task."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user, title="Old Title")

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:edit", kwargs={"pk": task.pk})
        data = {
            "title": "New Title",
            "priority": "high",
            "status": "completed",
        }
        response = client.post(url, data)

        assert response.status_code == 302

        task.refresh_from_db()
        assert task.title == "New Title"
        assert task.priority == "high"
        assert task.status == "completed"

    def test_update_view_denies_other_users(self, client):
        """Test that users cannot edit other users' tasks."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory(password="testpass123")
        task = TaskFactory(owner=user2)

        client.login(username=user1.email, password="testpass123")
        url = reverse("tasks:edit", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 404

    def test_update_view_success_message(self, client):
        """Test success message is displayed."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:edit", kwargs={"pk": task.pk})
        data = {
            "title": "Updated Task",
            "priority": "medium",
            "status": "pending",
        }
        response = client.post(url, data, follow=True)

        # Verify successful redirect to detail page
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.title == "Updated Task"


@pytest.mark.django_db
class TestTaskDeleteView:
    """Test cases for TaskDeleteView."""

    def test_delete_view_requires_authentication(self, client):
        """Test that delete view requires login."""
        task = TaskFactory()
        url = reverse("tasks:delete", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_delete_view_get_shows_confirmation(self, client):
        """Test GET request shows confirmation page."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:delete", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["task"] == task

    def test_delete_view_post_deletes_task(self, client):
        """Test POST request deletes the task."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        task_pk = task.pk

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:delete", kwargs={"pk": task.pk})
        response = client.post(url)

        assert response.status_code == 302
        assert not Task.objects.filter(pk=task_pk).exists()

    def test_delete_view_denies_other_users(self, client):
        """Test that users cannot delete other users' tasks."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory(password="testpass123")
        task = TaskFactory(owner=user2)

        client.login(username=user1.email, password="testpass123")
        url = reverse("tasks:delete", kwargs={"pk": task.pk})
        response = client.get(url)

        assert response.status_code == 404

    def test_delete_view_success_message(self, client):
        """Test success message is displayed."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        task_pk = task.pk

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:delete", kwargs={"pk": task.pk})
        response = client.post(url, follow=True)

        # Verify successful redirect and deletion
        assert response.status_code == 200
        assert not Task.objects.filter(pk=task_pk).exists()

    def test_delete_view_redirects_to_list(self, client):
        """Test that delete redirects to task list."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)

        client.login(username=user.email, password="testpass123")
        url = reverse("tasks:delete", kwargs={"pk": task.pk})
        response = client.post(url)

        assert response.status_code == 302
        assert response.url == reverse("tasks:list")
