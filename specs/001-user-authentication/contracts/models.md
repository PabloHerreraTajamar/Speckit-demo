# Authentication Models Contract

**Version**: 1.0.0  
**Feature**: 001-user-authentication

## User Model Contract

### Manager Methods

#### `User.objects.create_user(email, username, password, **extra_fields)`
**Purpose**: Create a regular user with hashed password  
**Returns**: User instance  
**Raises**: `ValueError` if email or username missing

**Example**:
```python
user = User.objects.create_user(
    email='user@example.com',
    username='johndoe',
    password='SecurePass123!',
    first_name='John'
)
```

#### `User.objects.create_superuser(email, username, password, **extra_fields)`
**Purpose**: Create admin user with is_staff=True, is_superuser=True  
**Returns**: User instance  
**Example**: Same as create_user

---

### Instance Methods

#### `user.set_password(raw_password)`
**Purpose**: Hash and set password using bcrypt  
**Returns**: None (call `user.save()` after)

#### `user.check_password(raw_password)`
**Purpose**: Verify password against hash  
**Returns**: Boolean

#### `user.get_full_name()`
**Purpose**: Return "first_name last_name" or email if names blank  
**Returns**: String

---

## AuthenticationLog Model Contract

### Class Methods

#### `AuthenticationLog.objects.log_registration(user, request)`
**Purpose**: Log successful user registration  
**Returns**: AuthenticationLog instance

#### `AuthenticationLog.objects.log_login(user, request, success=True)`
**Purpose**: Log login attempt (success or failure)  
**Returns**: AuthenticationLog instance

#### `AuthenticationLog.objects.log_logout(user, request)`
**Purpose**: Log user logout  
**Returns**: AuthenticationLog instance

#### `AuthenticationLog.objects.log_password_change(user, request)`
**Purpose**: Log password change  
**Returns**: AuthenticationLog instance

---

### Query Methods

#### `AuthenticationLog.objects.recent_logins(user, limit=10)`
**Purpose**: Get user's recent login attempts  
**Returns**: QuerySet of AuthenticationLog (ordered by -timestamp)

#### `AuthenticationLog.objects.failed_attempts(hours=24)`
**Purpose**: Get all failed login attempts in last N hours  
**Returns**: QuerySet of AuthenticationLog

**Example**:
```python
logs = AuthenticationLog.objects.recent_logins(user, limit=5)
for log in logs:
    print(f"{log.timestamp}: {log.event_type} from {log.ip_address}")
```

---

## References

- [Django Model Managers](https://docs.djangoproject.com/en/5.0/topics/db/managers/)
- [Django User Model](https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#django.contrib.auth.models.User)
