# Authentication Views Contract

**Version**: 1.0.0  
**Feature**: 001-user-authentication

## View Catalog

### 1. RegisterView

**URL**: `/accounts/register/`  
**HTTP Method**: GET, POST  
**Authentication**: Not required  
**Template**: `accounts/register.html`

**GET Request** (display form):
- **Response**: 200 OK with registration form
- **Context**: `{'form': RegistrationForm()}`

**POST Request** (submit registration):
- **Input Fields**:
  - `email` (string, required): Valid email, normalized to lowercase
  - `username` (string, required): 3-30 alphanumeric characters
  - `password` (string, required): Min 8 chars, complexity rules
  - `password_confirm` (string, required): Must match password
  - `first_name` (string, optional)
  - `last_name` (string, optional)
  - `csrfmiddlewaretoken` (hidden): CSRF protection

- **Success Response**: 302 redirect to `/accounts/login/` with message "Account created successfully"
- **Failure Response**: 200 OK with form errors displayed
- **Side Effects**: User created, password bcrypt hashed, registration logged

---

### 2. LoginView

**URL**: `/accounts/login/`  
**HTTP Method**: GET, POST  
**Authentication**: Not required  
**Template**: `accounts/login.html`

**GET Request**:
- **Response**: 200 OK with login form
- **Query Param**: `next` (optional): Redirect URL after login

**POST Request**:
- **Input Fields**:
  - `email` (string, required): Email or username
  - `password` (string, required)
  - `remember_me` (boolean, optional): Persistent session (2 weeks)
  - `csrfmiddlewaretoken` (hidden)

- **Success Response**: 302 redirect to `next` param or `/dashboard/`
- **Failure Response**: 200 OK with generic error "Invalid credentials"
- **Side Effects**: Session created, last_login updated, login event logged

---

### 3. LogoutView

**URL**: `/accounts/logout/`  
**HTTP Method**: POST  
**Authentication**: Required  
**Template**: None (redirect only)

**POST Request**:
- **Input**: CSRF token only
- **Response**: 302 redirect to `/accounts/login/` with message "Logged out successfully"
- **Side Effects**: Session deleted, logout event logged

---

### 4. ProfileView

**URL**: `/accounts/profile/`  
**HTTP Method**: GET, POST  
**Authentication**: Required (`@login_required`)  
**Template**: `accounts/profile.html`

**GET Request**:
- **Response**: 200 OK with profile form pre-filled
- **Context**: `{'form': ProfileForm(instance=request.user)}`

**POST Request**:
- **Input Fields**:
  - `first_name` (string, optional)
  - `last_name` (string, optional)
  - `email` (string, required): Must be unique
  - `csrfmiddlewaretoken` (hidden)

- **Success Response**: 200 OK with message "Profile updated"
- **Failure Response**: 200 OK with form errors (e.g., "Email already in use")
- **Side Effects**: User record updated

---

### 5. ChangePasswordView

**URL**: `/accounts/profile/password/`  
**HTTP Method**: GET, POST  
**Authentication**: Required (`@login_required`)  
**Template**: `accounts/change_password.html`

**GET Request**:
- **Response**: 200 OK with password change form

**POST Request**:
- **Input Fields**:
  - `current_password` (string, required)
  - `new_password` (string, required): Complexity validation
  - `new_password_confirm` (string, required): Must match
  - `csrfmiddlewaretoken` (hidden)

- **Success Response**: 302 redirect to `/accounts/profile/` with message "Password changed successfully"
- **Failure Response**: 200 OK with errors (e.g., "Current password is incorrect")
- **Side Effects**: Password updated (bcrypt rehashed), password change logged

---

## Common Response Headers

All views return:
- `Content-Type: text/html; charset=utf-8`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Set-Cookie: csrftoken=...` (CSRF protection)
- `Set-Cookie: sessionid=...` (after login, HttpOnly, Secure, SameSite=Lax)

---

## Error Handling

- **400 Bad Request**: Invalid form data (validation errors shown in template)
- **403 Forbidden**: CSRF token missing or invalid
- **404 Not Found**: URL does not exist
- **500 Internal Server Error**: Unhandled exception (logged to Application Insights)

---

## CSRF Protection

All POST requests MUST include:
```html
{% csrf_token %}
<!-- Renders hidden input: <input type="hidden" name="csrfmiddlewaretoken" value="..."> -->
```

JavaScript AJAX requests MUST include:
```javascript
fetch('/accounts/logout/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken')
    }
})
```

---

## Redirect Behavior

| Scenario | Redirect To | Message |
|----------|-------------|---------|
| Registration success | `/accounts/login/` | "Account created successfully" |
| Login success (no `next`) | `/dashboard/` | None |
| Login success (with `next`) | Value of `next` param | None |
| Logout success | `/accounts/login/` | "Logged out successfully" |
| Unauthenticated user accesses protected view | `/accounts/login/?next=/protected/` | "Please login to continue" |
| Profile update success | `/accounts/profile/` (same page) | "Profile updated" |
| Password change success | `/accounts/profile/` | "Password changed successfully" |

---

## Session Management

**Session Cookie Configuration**:
```python
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks (default)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'
```

**Session Data Structure**:
```python
{
    '_auth_user_id': '123',  # User primary key
    '_auth_user_backend': 'django.contrib.auth.backends.ModelBackend',
    '_auth_user_hash': '...',  # Password hash verification
}
```

---

## References

- [Django Class-Based Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/)
- [Django Authentication Views](https://docs.djangoproject.com/en/5.0/topics/auth/default/#module-django.contrib.auth.views)
- [Django CSRF Protection](https://docs.djangoproject.com/en/5.0/ref/csrf/)
