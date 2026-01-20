# Authentication Signals Contract

**Version**: 1.0.0  
**Feature**: 001-user-authentication

## Signal Definitions

### 1. user_registered

**Sender**: `User` model  
**Fired When**: After successful user registration  
**Signal Type**: Django post_save with `created=True`

**kwargs**:
```python
{
    'instance': User,      # The newly created user
    'created': True,       # Always True for this signal
    'raw': False,          # False (normal save)
    'using': 'default',    # Database alias
    'update_fields': None
}
```

**Use Case**: Send welcome email, create user profile, track registration in analytics

**Example Receiver**:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    if created:
        # User was just created
        AuthenticationLog.objects.log_registration(instance, request)
```

---

### 2. user_logged_in

**Sender**: `django.contrib.auth`  
**Fired When**: After successful login (via authenticate + login)  
**Signal Type**: Django built-in signal

**kwargs**:
```python
{
    'user': User,    # The authenticated user
    'request': HttpRequest
}
```

**Use Case**: Update last_login, log authentication event, track session start

**Example Receiver**:
```python
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def log_login_event(sender, request, user, **kwargs):
    AuthenticationLog.objects.log_login(user, request, success=True)
```

---

### 3. user_logged_out

**Sender**: `django.contrib.auth`  
**Fired When**: After logout (session deleted)  
**Signal Type**: Django built-in signal

**kwargs**:
```python
{
    'user': User,    # The logged-out user
    'request': HttpRequest
}
```

**Use Case**: Log logout event, track session duration

**Example Receiver**:
```python
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

@receiver(user_logged_out)
def log_logout_event(sender, request, user, **kwargs):
    if user:  # user can be None if anonymous
        AuthenticationLog.objects.log_logout(user, request)
```

---

### 4. user_login_failed

**Sender**: `django.contrib.auth`  
**Fired When**: Authentication fails (wrong password or non-existent user)  
**Signal Type**: Django built-in signal

**kwargs**:
```python
{
    'credentials': dict,  # {'username': '...', 'password': '***'}
    'request': HttpRequest
}
```

**Use Case**: Log failed attempts, implement rate limiting, detect brute force attacks

**Example Receiver**:
```python
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    AuthenticationLog.objects.create(
        user=None,
        event_type='failed_login',
        ip_address=request.META.get('REMOTE_ADDR'),
        success=False,
        metadata={'attempted_email': credentials.get('username')}
    )
```

---

## Signal Guarantees

1. **Ordering**: Signals fire synchronously, receivers execute in registration order
2. **Transaction**: Signals fire inside database transaction (can be rolled back)
3. **Exceptions**: If receiver raises exception, request fails (handle gracefully)

---

## References

- [Django Signals Documentation](https://docs.djangoproject.com/en/5.0/topics/signals/)
- [Django Auth Signals](https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#module-django.contrib.auth.signals)
