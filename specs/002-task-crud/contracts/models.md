# Model Contracts - Task CRUD Operations

**Date**: 2026-01-19  
**Feature**: 002-task-crud  
**Version**: 1.0.0

---

## Task Model

**Class**: `tasks.models.Task`  
**Extends**: `django.db.models.Model`

**Purpose**: Represents a user's personal task.

### Fields

| Field | Type | Constraints | Default |
|-------|------|------------|---------|
| `id` | BigAutoField | PRIMARY KEY | auto |
| `title` | CharField(200) | NOT NULL, validated | - |
| `description` | TextField(2000) | nullable, validated | '' |
| `due_date` | DateField | nullable | None |
| `priority` | CharField(10) | choices, indexed | 'media' |
| `status` | CharField(15) | choices, indexed | 'pendiente' |
| `created_at` | DateTimeField | auto_now_add, indexed | now() |
| `updated_at` | DateTimeField | auto_now | now() |
| `completed_at` | DateTimeField | nullable | None |
| `owner` | ForeignKey(User) | CASCADE, indexed | - |

### Methods

#### `save(self, *args, **kwargs)`

**Pre-conditions**:
- `title` is not empty (after strip)
- `title` max 200 chars
- `description` max 2000 chars (if provided)
- `owner` exists (foreign key valid)

**Post-conditions**:
- If `status == 'completada'` and `completed_at is None`: auto-set `completed_at = now()`
- If `status == 'pendiente'`: clear `completed_at = None`
- `updated_at` auto-updated by Django

**Side Effects**:
- Writes to database
- Sends `post_save` signal

**Example**:
```python
task = Task(title='Test', owner=user)
task.save()  # created_at and updated_at auto-set

task.status = 'completada'
task.save()  # completed_at auto-set
```

---

#### `__str__(self)`

**Returns**: `"{title} ({status_display})"`  
**Example**: `"Complete proposal (Pendiente)"`

---

### QuerySet Methods

**Manager**: `Task.objects` (TaskManager)

#### `for_user(user)`

**Pre-conditions**: `user` is valid User instance  
**Post-conditions**: Returns queryset filtered by `owner=user`  
**Returns**: TaskQuerySet

```python
tasks = Task.objects.for_user(request.user)
```

---

#### `pending()`

**Post-conditions**: Returns queryset filtered by `status='pendiente'`  
**Returns**: TaskQuerySet

```python
pending_tasks = Task.objects.for_user(user).pending()
```

---

#### `completed()`

**Post-conditions**: Returns queryset filtered by `status='completada'`  
**Returns**: TaskQuerySet

```python
completed_tasks = Task.objects.for_user(user).completed()
```

---

#### `high_priority()`

**Post-conditions**: Returns queryset filtered by `priority='alta'`  
**Returns**: TaskQuerySet

```python
urgent_tasks = Task.objects.for_user(user).high_priority()
```

---

#### `by_due_date()`

**Post-conditions**: Returns queryset ordered by `due_date` ASC (nulls last)  
**Returns**: TaskQuerySet

```python
sorted_tasks = Task.objects.for_user(user).by_due_date()
```

---

#### `by_priority()`

**Post-conditions**: Returns queryset ordered by priority (alta → media → baja)  
**Returns**: TaskQuerySet

```python
sorted_tasks = Task.objects.for_user(user).by_priority()
```

---

### Validation

**Validators**:
- `validate_title_length`: Title cannot be empty, max 200 chars
- `validate_description_length`: Description max 2000 chars

**Validation Errors**:
```python
from django.core.exceptions import ValidationError

# Empty title
task = Task(title='', owner=user)
task.full_clean()  # raises ValidationError: "Title cannot be empty"

# Title too long
task = Task(title='x' * 201, owner=user)
task.full_clean()  # raises ValidationError: "Title cannot exceed 200 characters"
```

---

### Invariants

1. **Ownership Immutability**: `owner` cannot change after creation
2. **Status-Timestamp Coupling**: `completed_at` auto-managed based on `status`
3. **Created-at Immutability**: `created_at` never changes after creation
4. **Priority Choices**: Must be one of 'alta', 'media', 'baja'
5. **Status Choices**: Must be one of 'pendiente', 'completada'

---

### Meta Options

```python
class Meta:
    db_table = 'tasks_task'
    ordering = ['-created_at']  # Newest first by default
    indexes = [
        Index(fields=['owner', '-created_at']),  # List view optimization
        Index(fields=['owner', 'status']),       # Status filter optimization
        Index(fields=['owner', 'priority']),     # Priority filter optimization
        Index(fields=['owner', 'due_date']),     # Due date sorting optimization
    ]
```

---

### Related Names

**From User model**:
```python
user.tasks.all()  # All tasks owned by user
user.tasks.pending()  # Pending tasks
user.tasks.completed()  # Completed tasks
```

---

## References

- [Django Model API](https://docs.djangoproject.com/en/5.0/ref/models/instances/)
- [Django QuerySet API](https://docs.djangoproject.com/en/5.0/ref/models/querysets/)
- [Django Validators](https://docs.djangoproject.com/en/5.0/ref/validators/)
