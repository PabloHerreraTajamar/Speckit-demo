# Phase 0: Research - User Authentication System

**Date**: 2026-01-19  
**Feature**: 001-user-authentication  
**Branch**: `001-user-authentication`

## NEEDS CLARIFICATION Review

**Status**: ✅ NO CLARIFICATIONS NEEDED

All requirements in `spec.md` are clear and implementable:
- Authentication mechanism explicitly defined (email/username + password)
- Security requirements clear (bcrypt, CSRF, session tokens, logging)
- User stories testable and independent
- Validation rules specified (password complexity, email format, username constraints)
- Edge cases documented and resolved

## Technology Decisions

### 1. Django Authentication Framework Strategy

**Decision**: Extend Django's built-in authentication with custom User model

**Options Evaluated**:
- **Option A**: Use Django's default User model (`django.contrib.auth.User`)
  - ❌ Requires additional profile model for extensibility
  - ❌ Username-only login (spec requires email/username)
  
- **Option B**: Custom User model inheriting `AbstractUser` (SELECTED)
  - ✅ Email as USERNAME_FIELD for flexible login
  - ✅ Direct control over fields and validation
  - ✅ Easier to extend later (future features)
  
- **Option C**: Custom User model from `AbstractBaseUser`
  - ⚠️ Too much boilerplate, reinvents Django's wheel

**Rationale**: `AbstractUser` provides authentication infrastructure (password hashing, permissions) while allowing email-based login and custom fields. Balances flexibility and Django conventions.

---

### 2. Password Hashing Library

**Decision**: Django's built-in bcrypt support via `django[bcrypt]`

**Options Evaluated**:
- **Option A**: Default PBKDF2 hasher
  - ⚠️ Less resistant to GPU-based attacks than bcrypt
  
- **Option B**: bcrypt via `django[bcrypt]` (SELECTED)
  - ✅ Industry standard for password hashing
  - ✅ Explicitly required in spec
  - ✅ Adaptive cost factor (future-proof)
  
- **Option C**: Argon2 hasher
  - ⚠️ Not specified in spec, introduces unnecessary change

**Configuration**:
```python
# settings/base.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]
```

**Rationale**: Bcrypt is spec-mandated and provides excellent security. Django's hasher abstraction allows easy configuration without custom code.

---

### 3. Session Management Strategy

**Decision**: Django database-backed sessions with default settings

**Options Evaluated**:
- **Option A**: Database sessions (`django.contrib.sessions.backends.db`) (SELECTED)
  - ✅ Persistent across server restarts
  - ✅ Easy invalidation (logout deletes session row)
  - ✅ Works with PostgreSQL (already provisioned)
  
- **Option B**: Cache-based sessions
  - ❌ Requires Redis/Memcached (not in MVP scope)
  
- **Option C**: Signed cookie sessions
  - ❌ Cannot invalidate server-side (logout doesn't work properly)

**Configuration**:
```python
# settings/base.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS-only
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

**Rationale**: Database sessions align with Security First principle (server-side control) and leverage existing PostgreSQL infrastructure from Feature 004.

---

### 4. Security Logging Implementation

**Decision**: Custom `AuthenticationLog` model + Django signals

**Options Evaluated**:
- **Option A**: Django's built-in logging to files
  - ❌ Not queryable for audit reports
  
- **Option B**: Custom model + signals (SELECTED)
  - ✅ Database-backed for queries and reporting
  - ✅ Signals auto-capture events without cluttering views
  - ✅ Future UI can display user's own login history
  
- **Option C**: Azure Application Insights only
  - ⚠️ Not required in spec, telemetry vs. audit trail

**Model Schema**:
```python
class AuthenticationLog(models.Model):
    user = models.ForeignKey(User, null=True)  # Null for failed attempts
    event_type = models.CharField(max_length=20)  # registration, login, logout, failed_login
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
```

**Rationale**: Database logging provides audit trail required by Security First principle and enables future reporting features.

---

### 5. Form Validation Architecture

**Decision**: Django Forms with custom validators

**Options Evaluated**:
- **Option A**: Model-level validation only
  - ❌ Doesn't provide user-friendly error messages
  
- **Option B**: Django Forms with validators (SELECTED)
  - ✅ Clean separation (forms validate, models enforce)
  - ✅ Automatic CSRF protection
  - ✅ Field-level and form-level validation
  
- **Option C**: REST API serializers (DRF)
  - ❌ Out of scope, spec implies traditional web forms

**Custom Validators**:
```python
# accounts/validators.py
def validate_password_complexity(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Password must contain uppercase letter")
    # ... (lowercase, number, special char)

def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9]{3,30}$', value):
        raise ValidationError("Username must be 3-30 alphanumeric characters")
```

**Rationale**: Django Forms are idiomatic for web apps, provide CSRF protection (Security First), and enable clear error messages (FR-018).

---

### 6. URL Routing Strategy

**Decision**: Dedicated `accounts` app with namespaced URLs

**Pattern**:
```python
# accounts/urls.py
app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/password/', views.ChangePasswordView.as_view(), name='change_password'),
]

# taskmanager/urls.py
urlpatterns = [
    path('accounts/', include('accounts.urls')),
]
```

**Rationale**: URL namespacing prevents collisions with future features (tasks, attachments) and follows Django best practices.

---

### 7. Email Normalization Strategy

**Decision**: Custom `UserManager` with `normalize_email()`

**Implementation**:
```python
# accounts/managers.py
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def normalize_email(self, email):
        # Lowercase entire email (domain + local part)
        return email.lower()
    
    def create_user(self, email, username, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hashes with bcrypt
        user.save(using=self._db)
        return user
```

**Rationale**: Handles edge case from spec (uppercase emails) and prevents duplicate accounts with `user@example.com` vs `USER@example.com`.

---

### 8. Testing Strategy

**Decision**: Three-tier testing with pytest-django

**Layers**:

1. **Unit Tests** (models, forms, validators)
   ```python
   # tests/accounts/test_models.py
   def test_user_password_is_hashed(db):
       user = User.objects.create_user(email='test@example.com', username='testuser', password='TestPass123!')
       assert user.password != 'TestPass123!'
       assert user.password.startswith('bcrypt')
   ```

2. **Integration Tests** (views, flows)
   ```python
   # tests/accounts/test_views.py
   def test_registration_creates_user_and_redirects(client, db):
       response = client.post('/accounts/register/', {...})
       assert response.status_code == 302
       assert User.objects.filter(email='test@example.com').exists()
   ```

3. **E2E Tests** (full authentication cycle)
   ```python
   # tests/accounts/test_authentication.py
   def test_user_can_register_login_logout(client, db):
       # Register, login, access protected page, logout, verify session invalid
   ```

**Coverage Target**: >80% (enforced via pytest-cov)

**Rationale**: Aligns with Test-First principle (TDD mandatory). Three tiers ensure unit behavior, integration correctness, and end-user flows all work.

---

## Technical Constraints

1. **Django Version**: 5.0 (as per constitution)
2. **Python Version**: 3.11+ (as per constitution)
3. **Database**: PostgreSQL (provisioned via Feature 004)
4. **Password Hashing**: bcrypt (spec requirement)
5. **CSRF Protection**: Enabled on all forms (Security First principle)
6. **Session Backend**: Database-backed (no Redis/cache in MVP)
7. **Authentication Backend**: Django default (`ModelBackend`)

---

## Performance Considerations

1. **Database Queries**:
   - User lookup by email: indexed field (Django default)
   - Session retrieval: indexed by session_key
   - Authentication logs: bulk insert via signals (no blocking)

2. **Password Hashing**:
   - Bcrypt cost factor: 12 (Django default, ~300ms per hash)
   - Acceptable for login/registration (not high-frequency operation)

3. **Session Storage**:
   - Database sessions: ~50ms lookup (PostgreSQL indexed)
   - Consider cache-backed sessions in future if >1000 concurrent users

4. **Response Time Targets** (from Technical Context):
   - Login: <200ms p95 (includes bcrypt verification ~300ms, needs optimization)
   - Registration: <500ms p95 (bcrypt hashing + DB write)
   - Profile operations: <100ms p95 (simple DB updates)

**Note**: Bcrypt cost factor may need tuning if <200ms login target cannot be met. Will validate in performance tests.

---

## Security Considerations

1. **Password Storage**: Never plaintext, always bcrypt hashed
2. **CSRF Protection**: Django middleware enabled, tokens in all forms
3. **Session Security**: 
   - HttpOnly cookies (no JavaScript access)
   - Secure cookies (HTTPS-only)
   - SameSite=Lax (CSRF mitigation)
4. **Input Validation**: All user inputs validated via forms/validators
5. **SQL Injection**: Django ORM parameterized queries (automatic protection)
6. **Authentication Logging**: All events logged with IP, user agent, timestamp
7. **Error Messages**: Generic for auth failures (FR-019, don't leak user existence)
8. **Authorization**: Each user can only access their own data (FR-020)

---

## Dependencies

### External Dependencies
- Django 5.0
- bcrypt 4.0+ (via `django[bcrypt]`)
- psycopg2-binary 2.9+ (PostgreSQL adapter)
- pytest-django 4.5+ (testing)
- pytest-cov 4.0+ (coverage reporting)

### Internal Dependencies
- Feature 004 (Azure Infrastructure): Provides PostgreSQL database and App Service
- No other feature dependencies (this is foundational)

### Dependent Features
- Feature 002 (Task CRUD): Requires user authentication for task ownership
- Feature 003 (Attachments): Requires authentication for file access control

---

## Open Questions

**Status**: ✅ ALL RESOLVED

1. ~~Email verification required?~~ → No, out of scope per spec assumptions
2. ~~Password reset workflow?~~ → Out of scope per spec
3. ~~Session timeout duration?~~ → Use Django default (2 weeks)
4. ~~Multi-factor authentication?~~ → Out of scope per spec
5. ~~Account lockout after failed attempts?~~ → Out of scope per spec
6. ~~Should username be case-sensitive?~~ → Yes (unlike email), validate alphanumeric only
7. ~~Bcrypt cost factor?~~ → Use Django default (12), may tune based on performance tests

---

## Django Configuration Decisions

### Settings Structure

**Decision**: Split settings by environment (base, development, production)

```
taskmanager/settings/
├── __init__.py
├── base.py          # Common settings (installed apps, middleware, etc.)
├── development.py   # Dev-specific (DEBUG=True, local DB, etc.)
└── production.py    # Prod settings (env vars, HTTPS, App Insights)
```

**Rationale**: Aligns with Cloud-Native principle (12-factor app, environment-specific config).

### Installed Apps Order

```python
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Project apps
    'accounts',  # Feature 001
    # 'tasks',   # Feature 002 (future)
]
```

### Custom User Model Activation

```python
# settings/base.py
AUTH_USER_MODEL = 'accounts.User'
```

**CRITICAL**: Must be set before first migration. Cannot change after database creation.

---

## Migration Strategy

1. **Initial Migration**: Create custom User model and AuthenticationLog
   ```bash
   python manage.py makemigrations accounts
   python manage.py migrate
   ```

2. **No data migration needed**: Fresh database from Feature 004

3. **Future migrations**: Add fields to User model as needed (extensible design)

---

## References

- [Django Authentication System](https://docs.djangoproject.com/en/5.0/topics/auth/)
- [Customizing Django User Model](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/)
- [Django Password Management](https://docs.djangoproject.com/en/5.0/topics/auth/passwords/)
- [bcrypt Password Hashing](https://github.com/pyca/bcrypt/)
- [Django Sessions](https://docs.djangoproject.com/en/5.0/topics/http/sessions/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
