# Phase 0: Research - Task CRUD Operations

**Date**: 2026-01-19  
**Feature**: 002-task-crud  
**Branch**: `002-task-crud`

## NEEDS CLARIFICATION Review

**Status**: ✅ NO CLARIFICATIONS NEEDED

All requirements clear and implementable:
- CRUD operations explicitly defined
- Filtering/sorting criteria specified
- Pagination parameters defined (20 per page)
- Validation rules clear (title max 200, description max 2000)
- Ownership model explicit (one owner per task)

## Technology Decisions

### 1. Django Class-Based Views Strategy

**Decision**: Use Django generic CBVs for CRUD operations

**Options Evaluated**:
- **Option A**: Function-based views
  - ❌ More boilerplate for pagination, forms
  
- **Option B**: Class-Based Views (CreateView, UpdateView, DeleteView, ListView, DetailView) (SELECTED)
  - ✅ Built-in pagination support
  - ✅ Automatic form handling and validation
  - ✅ Override get_queryset for ownership filtering
  - ✅ Less code, Django idiomatic
  
- **Option C**: REST API with DRF
  - ❌ Out of scope, spec implies traditional web UI

**Rationale**: CBVs reduce boilerplate, provide pagination/form handling, and align with Django best practices. Ownership filtering via `get_queryset` override ensures users only see their tasks.

---

### 2. Task Filtering Implementation

**Decision**: Custom TaskFilter class + Django QuerySet filtering

**Implementation**:
```python
# tasks/filters.py
class TaskFilter:
    def __init__(self, queryset, params):
        self.queryset = queryset
        self.params = params
    
    def filter(self):
        qs = self.queryset
        if self.params.get('status'):
            qs = qs.filter(status=self.params['status'])
        if self.params.get('priority'):
            qs = qs.filter(priority=self.params['priority'])
        return qs
    
    def sort(self):
        sort_by = self.params.get('sort', '-created_at')  # Default newest first
        return self.queryset.order_by(sort_by)
```

**Rationale**: Encapsulates filter logic, testable independently, reusable across views.

---

### 3. Pagination Strategy

**Decision**: Django Paginator with 20 items per page

**Configuration**:
```python
# tasks/views.py
class TaskListView(ListView):
    model = Task
    paginate_by = 20
    template_name = 'tasks/task_list.html'
    
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user).order_by('-created_at')
```

**Rationale**: Django Paginator is built-in, handles edge cases (empty pages, out-of-range), integrates with ListView.

---

### 4. Validation Strategy

**Decision**: Django ModelForm with custom validators

**Validators**:
```python
# tasks/validators.py
def validate_title_length(value):
    if len(value.strip()) == 0:
        raise ValidationError("Title cannot be empty")
    if len(value) > 200:
        raise ValidationError("Title cannot exceed 200 characters")

def validate_description_length(value):
    if value and len(value) > 2000:
        raise ValidationError("Description cannot exceed 2000 characters")
```

**Rationale**: Separates validation logic, reusable across create/update, testable independently.

---

### 5. Ownership Authorization Strategy

**Decision**: Override get_queryset in CBVs + custom permission mixin

**Implementation**:
```python
# tasks/views.py
from django.contrib.auth.mixins import LoginRequiredMixin

class TaskOwnerMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

class TaskDetailView(TaskOwnerMixin, DetailView):
    model = Task  # get_queryset automatically filters by owner
```

**Rationale**: LoginRequiredMixin enforces authentication, get_queryset override ensures users only see their tasks (404 if accessing another user's task).

---

### 6. Test Data Generation

**Decision**: factory_boy for test fixtures

**Factory Example**:
```python
# tests/tasks/factories.py
import factory
from accounts.models import User
from tasks.models import Task

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task
    title = factory.Sequence(lambda n: f'Task {n}')
    owner = factory.SubFactory(UserFactory)
    priority = 'media'
    status = 'pendiente'
```

**Rationale**: factory_boy generates realistic test data, reduces boilerplate, supports relationships (owner FK).

---

### 7. Completion Timestamp Handling

**Decision**: Model save() override to auto-update completed_at

**Implementation**:
```python
# tasks/models.py
class Task(models.Model):
    # ... fields ...
    
    def save(self, *args, **kwargs):
        if self.status == 'completada' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status == 'pendiente':
            self.completed_at = None
        super().save(*args, **kwargs)
```

**Rationale**: Automatic timestamp management reduces bugs, ensures consistency (FR-022, FR-023).

---

### 8. URL Routing Pattern

**Decision**: RESTful URL structure with namespacing

**URLs**:
```python
# tasks/urls.py
app_name = 'tasks'

urlpatterns = [
    path('', TaskListView.as_view(), name='list'),
    path('create/', TaskCreateView.as_view(), name='create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='delete'),
]

# taskmanager/urls.py
urlpatterns = [
    path('tasks/', include('tasks.urls')),
]
```

**Rationale**: RESTful conventions, namespaced to avoid conflicts with future features.

---

## Technical Constraints

1. **Django Version**: 5.0 (as per constitution)
2. **Python Version**: 3.11+ (as per constitution)
3. **Database**: PostgreSQL (from Feature 004)
4. **Authentication**: User model from Feature 001 (prerequisite)
5. **CSRF Protection**: Required on all POST/PUT/DELETE operations
6. **Ownership**: Immutable (cannot transfer tasks)

---

## Performance Considerations

1. **Database Queries**:
   - Task list: Single query with filter by owner + pagination
   - Filtering: Index on status, priority, created_at columns
   - Sorting: Composite index on (owner_id, created_at) for default view

2. **Pagination**:
   - 20 items per page (spec requirement)
   - Django Paginator uses LIMIT/OFFSET (acceptable for <10k tasks)
   - Consider cursor-based pagination if users exceed 1000 tasks

3. **Response Time Targets**:
   - Task list: <2s for 100 tasks (from Technical Context)
   - Filter/sort: <1s (from Technical Context)
   - Task creation: <30s (from Technical Context)

---

## Security Considerations

1. **Ownership Validation**: get_queryset filters by owner (prevents horizontal privilege escalation)
2. **CSRF Protection**: Django middleware enabled, tokens in all forms
3. **XSS Prevention**: Django template auto-escaping (FR-029)
4. **SQL Injection**: Django ORM parameterized queries
5. **Authorization**: LoginRequiredMixin + ownership checks on all views

---

## Dependencies

### External Dependencies
- Django 5.0
- factory_boy 3.3+ (testing)
- pytest-django 4.5+ (testing)

### Internal Dependencies
- Feature 001 (User Authentication): Provides User model for owner FK

### Dependent Features
- Feature 003 (Task Attachments): Will add attachments FK to Task model

---

## Open Questions

**Status**: ✅ ALL RESOLVED

1. ~~Soft delete vs. permanent delete?~~ → Permanent delete (spec assumption)
2. ~~Pagination size?~~ → 20 per page (from spec SC-007)
3. ~~Default sort order?~~ → Newest first, creation date descending (FR-017)
4. ~~Handle concurrent edits?~~ → Last save wins, no conflict detection (edge case assumption)
5. ~~Due date timezone?~~ → Server timezone (spec assumption)

---

## References

- [Django Class-Based Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/)
- [Django Pagination](https://docs.djangoproject.com/en/5.0/topics/pagination/)
- [factory_boy Documentation](https://factoryboy.readthedocs.io/)
- [Django QuerySet API](https://docs.djangoproject.com/en/5.0/ref/models/querysets/)
