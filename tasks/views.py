"""
Views for task management.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import TaskForm
from .models import Task


class TaskOwnerMixin(LoginRequiredMixin):
    """Mixin to ensure tasks are filtered by owner."""

    def get_queryset(self):
        """Return only tasks owned by current user."""
        return Task.objects.filter(owner=self.request.user)


class TaskListView(TaskOwnerMixin, ListView):
    """
    View for listing user's tasks with filtering and pagination.

    Supports filtering by status and priority via query parameters.
    """

    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self):
        """Filter tasks by status and priority from query params."""
        queryset = super().get_queryset()

        # Filter by status
        status = self.request.GET.get("status")
        if status in ["pending", "completed"]:
            queryset = queryset.filter(status=status)

        # Filter by priority
        priority = self.request.GET.get("priority")
        if priority in ["high", "medium", "low"]:
            queryset = queryset.filter(priority=priority)

        # Sort by parameter
        sort = self.request.GET.get("sort", "-created_at")
        if sort in [
            "-created_at",
            "created_at",
            "due_date",
            "-due_date",
            "priority",
            "-priority",
        ]:
            if sort == "priority":
                # Custom sort for priority (high > medium > low)
                queryset = queryset.order_by("priority")
            else:
                queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        """Add filter parameters and stats to context."""
        context = super().get_context_data(**kwargs)

        # Pass current filters to template
        context["current_status"] = self.request.GET.get("status", "")
        context["current_priority"] = self.request.GET.get("priority", "")
        context["current_sort"] = self.request.GET.get("sort", "-created_at")

        # Add task statistics
        all_tasks = Task.objects.filter(owner=self.request.user)
        context["total_tasks"] = all_tasks.count()
        context["pending_count"] = all_tasks.filter(status="pending").count()
        context["completed_count"] = all_tasks.filter(status="completed").count()

        return context


class TaskDetailView(TaskOwnerMixin, DetailView):
    """
    View for displaying single task details.

    Only owner can view their tasks (404 for others).
    """

    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new tasks.

    Requires authentication and auto-sets owner to logged-in user.
    """

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        """Set owner to logged-in user before saving."""
        form.instance.owner = self.request.user
        messages.success(self.request, "Task created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to task detail page after creation."""
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})


class TaskUpdateView(TaskOwnerMixin, UpdateView):
    """
    View for updating existing tasks.

    Only owner can edit their tasks.
    """

    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        """Add success message on update."""
        messages.success(self.request, "Task updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to task detail page after update."""
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})


class TaskDeleteView(TaskOwnerMixin, DeleteView):
    """
    View for deleting tasks with confirmation.

    Only owner can delete their tasks.
    """

    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:list")

    def delete(self, request, *args, **kwargs):
        """Add success message on deletion."""
        messages.success(self.request, "Task deleted successfully!")
        return super().delete(request, *args, **kwargs)
