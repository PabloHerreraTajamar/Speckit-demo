# Quickstart Guide - Task CRUD Operations

**Date**: 2026-01-19  
**Feature**: 002-task-crud  
**Branch**: `002-task-crud`

## Overview

This guide helps developers set up and test the Task CRUD feature locally. Follow these steps to create the Task model, views, and run basic workflows.

---

## Prerequisites

- Feature 001 (User Authentication) completed
- PostgreSQL database running
- Python 3.11+ virtual environment activated
- Django project initialized

---

## Step 1: Create Django App

```powershell
# Create tasks app
python manage.py startapp tasks

# Add to INSTALLED_APPS in settings.py
# 'tasks',
```

---

## Step 2: Create Task Model

**File**: `tasks/models.py`

```python
from django.db import models
from django.conf import settings
from django.utils import timezone
from .validators import validate_title_length, validate_description_length

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
    ]
    
    title = models.CharField(max_length=200, validators=[validate_title_length])
    description = models.TextField(max_length=2000, blank=True, validators=[validate_description_length])
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='media', db_index=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendiente', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    
    class Meta:
        db_table = 'tasks_task'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.status == 'completada' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status == 'pendiente':
            self.completed_at = None
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
```

**File**: `tasks/validators.py`

```python
from django.core.exceptions import ValidationError

def validate_title_length(value):
    if not value or len(value.strip()) == 0:
        raise ValidationError("Title cannot be empty", code='empty_title')
    if len(value) > 200:
        raise ValidationError("Title cannot exceed 200 characters", code='title_too_long')

def validate_description_length(value):
    if value and len(value) > 2000:
        raise ValidationError("Description cannot exceed 2000 characters", code='description_too_long')
```

---

## Step 3: Run Migrations

```powershell
# Create migration file
python manage.py makemigrations tasks

# Apply migration
python manage.py migrate tasks
```

**Expected Output**:
```
Migrations for 'tasks':
  tasks\migrations\0001_initial.py
    - Create model Task
Running migrations:
  Applying tasks.0001_initial... OK
```

---

## Step 4: Create CRUD Views

**File**: `tasks/views.py`

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Task
from .forms import TaskForm

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().filter(owner=self.request.user)
        
        status = self.request.GET.get('status')
        if status in ['pendiente', 'completada']:
            qs = qs.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority in ['alta', 'media', 'baja']:
            qs = qs.filter(priority=priority)
        
        return qs

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
```

**File**: `tasks/forms.py`

```python
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
```

---

## Step 5: Configure URLs

**File**: `tasks/urls.py`

```python
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
]
```

**File**: `taskmanager/urls.py` (main project)

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns ...
    path('tasks/', include('tasks.urls')),
]
```

---

## Step 6: Test Workflows

### Create a Task

```powershell
# Start Django shell
python manage.py shell
```

```python
from accounts.models import User
from tasks.models import Task
from datetime import date

# Get user
user = User.objects.first()

# Create task
task = Task.objects.create(
    title='Write documentation',
    description='Complete the quickstart guide',
    due_date=date(2026, 1, 25),
    priority='alta',
    owner=user
)

print(task)  # Output: Write documentation (Pendiente)
```

### List Tasks

```python
# List all user tasks
tasks = Task.objects.for_user(user)
print(tasks.count())

# Filter by status
pending = tasks.filter(status='pendiente')
print(pending.count())
```

### Update Task Status

```python
task.status = 'completada'
task.save()

print(task.completed_at)  # Output: 2026-01-19 10:30:00+00:00
```

### Test Pagination

```python
# Create 25 test tasks
for i in range(25):
    Task.objects.create(
        title=f'Task {i+1}',
        owner=user
    )

# Query with pagination
from django.core.paginator import Paginator

tasks = Task.objects.for_user(user)
paginator = Paginator(tasks, 20)

print(paginator.num_pages)  # Output: 2
print(paginator.page(1).object_list.count())  # Output: 20
```

---

## Step 7: Run Tests

```powershell
# Run all task tests
pytest tests/tasks/ -v

# Run with coverage
pytest tests/tasks/ --cov=tasks --cov-report=html
```

**Expected Coverage**: > 80%

---

## Step 8: Access via Browser

1. Start development server:
   ```powershell
   python manage.py runserver
   ```

2. Navigate to: `http://localhost:8000/tasks/`

3. Test workflows:
   - ✅ View task list (empty initially)
   - ✅ Create new task via `/tasks/create/`
   - ✅ View task detail via `/tasks/<id>/`
   - ✅ Edit task via `/tasks/<id>/edit/`
   - ✅ Delete task via `/tasks/<id>/delete/`
   - ✅ Filter by status: `/tasks/?status=pendiente`
   - ✅ Filter by priority: `/tasks/?priority=alta`
   - ✅ Pagination: `/tasks/?page=2`

---

## Troubleshooting

### Migration Fails

**Error**: `accounts.User` table does not exist

**Fix**: Run Feature 001 migrations first:
```powershell
python manage.py migrate accounts
```

### Task Creation Fails

**Error**: `NOT NULL constraint failed: tasks_task.owner_id`

**Fix**: Ensure `owner` is set in view:
```python
def form_valid(self, form):
    form.instance.owner = self.request.user
    return super().form_valid(form)
```

### Completed Timestamp Not Set

**Error**: `completed_at` is None after marking complete

**Fix**: Verify `save()` override in model:
```python
def save(self, *args, **kwargs):
    if self.status == 'completada' and not self.completed_at:
        self.completed_at = timezone.now()
    super().save(*args, **kwargs)
```

---

## Next Steps

- **Feature 003**: Add task attachments with Azure Blob Storage
- **Testing**: Write comprehensive tests with factory_boy
- **UI**: Create Bootstrap templates for task views
- **API**: Add REST API for mobile clients

---

## References

- [Django Class-Based Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/)
- [Django Pagination](https://docs.djangoproject.com/en/5.0/topics/pagination/)
- [pytest-django](https://pytest-django.readthedocs.io/)
