# View Contracts - Task CRUD Operations

**Date**: 2026-01-19  
**Feature**: 002-task-crud  
**Version**: 1.0.0

---

## TaskListView

**Endpoint**: `GET /tasks/`  
**Class**: `tasks.views.TaskListView` (Django ListView)

**Pre-conditions**:
- User must be authenticated
- Session is valid

**Post-conditions**:
- Returns paginated list of user's tasks (20 per page)
- Tasks filtered by `owner=request.user`
- Tasks sorted by `-created_at` by default
- Renders `tasks/task_list.html`

**Query Parameters**:
- `status` (optional): Filter by 'pendiente' or 'completada'
- `priority` (optional): Filter by 'alta', 'media', or 'baja'
- `page` (optional): Page number (default: 1)

**Context Data**:
- `task_list` (queryset): Paginated Task objects
- `page_obj` (Page): Pagination metadata
- `is_paginated` (bool): True if multiple pages

**HTTP Status**:
- 200: Success
- 302: Redirect to login (if unauthenticated)

---

## TaskDetailView

**Endpoint**: `GET /tasks/<int:pk>/`  
**Class**: `tasks.views.TaskDetailView` (Django DetailView)

**Pre-conditions**:
- User must be authenticated
- Task with `pk` exists
- `task.owner == request.user`

**Post-conditions**:
- Returns single Task object
- Renders `tasks/task_detail.html`

**Context Data**:
- `task` (Task): Single Task object

**HTTP Status**:
- 200: Success
- 302: Redirect to login (if unauthenticated)
- 404: Task not found or not owned by user

---

## TaskCreateView

**Endpoint**: `GET /tasks/create/` (form), `POST /tasks/create/` (submit)  
**Class**: `tasks.views.TaskCreateView` (Django CreateView)

**Pre-conditions**:
- User must be authenticated
- For POST: Valid CSRF token
- For POST: Valid form data

**Post-conditions**:
- Task created with `owner=request.user`
- Redirect to task detail page
- Success message displayed

**Form Data** (POST):
- `title` (required): max 200 chars
- `description` (optional): max 2000 chars
- `due_date` (optional): date format YYYY-MM-DD
- `priority` (optional): 'alta', 'media', or 'baja' (default: 'media')
- `status` (optional): 'pendiente' or 'completada' (default: 'pendiente')

**Validation**:
- Title cannot be empty
- Title max 200 chars
- Description max 2000 chars

**HTTP Status**:
- 200: Form render (GET)
- 302: Redirect to detail (POST success)
- 400: Form validation errors (POST failure)

---

## TaskUpdateView

**Endpoint**: `GET /tasks/<int:pk>/edit/` (form), `POST /tasks/<int:pk>/edit/` (submit)  
**Class**: `tasks.views.TaskUpdateView` (Django UpdateView)

**Pre-conditions**:
- User must be authenticated
- Task with `pk` exists
- `task.owner == request.user`
- For POST: Valid CSRF token
- For POST: Valid form data

**Post-conditions**:
- Task updated with new values
- If status changed to 'completada', `completed_at` auto-set
- If status changed to 'pendiente', `completed_at` cleared
- Redirect to task detail page
- Success message displayed

**Form Data** (POST):
- `title` (required): max 200 chars
- `description` (optional): max 2000 chars
- `due_date` (optional): date format YYYY-MM-DD
- `priority` (optional): 'alta', 'media', or 'baja'
- `status` (optional): 'pendiente' or 'completada'

**Invariants**:
- `owner` cannot be changed (read-only)

**HTTP Status**:
- 200: Form render (GET)
- 302: Redirect to detail (POST success)
- 400: Form validation errors (POST failure)
- 404: Task not found or not owned by user

---

## TaskDeleteView

**Endpoint**: `GET /tasks/<int:pk>/delete/` (confirmation), `POST /tasks/<int:pk>/delete/` (confirm)  
**Class**: `tasks.views.TaskDeleteView` (Django DeleteView)

**Pre-conditions**:
- User must be authenticated
- Task with `pk` exists
- `task.owner == request.user`
- For POST: Valid CSRF token

**Post-conditions**:
- Task deleted from database
- Redirect to task list page
- Success message displayed

**HTTP Status**:
- 200: Confirmation form (GET)
- 302: Redirect to list (POST success)
- 404: Task not found or not owned by user

---

## Authorization Invariant

**All views** must enforce ownership:
```python
def get_queryset(self):
    return super().get_queryset().filter(owner=self.request.user)
```

This ensures users can only view/edit/delete their own tasks.

---

## References

- [Django Class-Based Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/)
- [Django Generic Views](https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/)
