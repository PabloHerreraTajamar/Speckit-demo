# Authentication Contracts

This directory defines the **interfaces** and **contracts** for the user authentication system, serving as the agreement between the authentication layer and consuming features.

## Purpose

Authentication contracts ensure that:
1. **Input interfaces** are validated and documented (what authentication accepts)
2. **Output interfaces** are predictable and consumable (what authentication provides)
3. **Behavior contracts** are stable across refactorings (guaranteed functionality)

---

## Contract Files

### 1. [views.md](views.md)
Defines HTTP request/response contracts for authentication views.

**Purpose**: Documents URL patterns, request methods, form fields, response codes, and redirect behaviors for registration, login, logout, profile, and password change views.

**Consumers**:
- Frontend templates (form fields, CSRF tokens)
- Integration tests (expected status codes, redirects)
- Future API layer (if REST API added)

---

### 2. [models.md](models.md)
Defines data model contracts for User and AuthenticationLog.

**Purpose**: Documents model methods, manager methods, querysets, and guaranteed behaviors for user account and audit log operations.

**Consumers**:
- Other Django apps (tasks, attachments need User foreign keys)
- Admin interface (user management)
- Background tasks (email sending, cleanup jobs)

---

### 3. [signals.md](signals.md)
Defines Django signals emitted by authentication system.

**Purpose**: Documents when signals fire (registration, login, logout) and what data they provide for event-driven integrations.

**Consumers**:
- Analytics system (track user activity)
- Notification system (welcome emails, alerts)
- Audit logging (AuthenticationLog creation)

---

## Contract Guarantees

### Stability
- View URL patterns MUST NOT change without major version bump
- Model method signatures MUST remain backward-compatible
- Signal payloads MUST only add fields, never remove

### Validation
- All inputs validated via Django forms (automatic CSRF protection)
- All outputs tested in integration test suite
- Contract conformance checked in CI/CD

### Documentation
- Every view has request/response example
- Every model method has docstring and usage example
- Every signal has sender and kwargs documented

---

## Usage Example

**Feature 002 (Task CRUD) consuming authentication contracts**:

```python
# tasks/models.py
from django.conf import settings

class Task(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Contract: User model
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    # ...

# tasks/views.py
from django.contrib.auth.decorators import login_required

@login_required  # Contract: User must be authenticated
def create_task(request):
    task = Task.objects.create(owner=request.user)  # Contract: request.user is User instance
    # ...
```

---

## Versioning

Contracts follow Semantic Versioning:
- **Major**: Breaking changes (URL change, method signature change, signal removed)
- **Minor**: New features added (new view, new model method, new signal)
- **Patch**: Bug fixes or documentation updates

**Current Version**: 1.0.0 (initial contract for Feature 001)

---

## References

- [Django URL Patterns](https://docs.djangoproject.com/en/5.0/topics/http/urls/)
- [Django Model Methods](https://docs.djangoproject.com/en/5.0/topics/db/models/#model-methods)
- [Django Signals](https://docs.djangoproject.com/en/5.0/topics/signals/)
