# Quickstart: User Authentication System

**Feature**: 001-user-authentication  
**Branch**: `001-user-authentication`  
**Estimated Time**: 30 minutes (first setup), 10 minutes (subsequent)

## Prerequisites

### 1. Infrastructure Provisioned

Feature 004 (Azure Infrastructure) must be completed:
```powershell
# Verify infrastructure exists
az group show --name rg-dev-taskmanager-eastus

# Get database connection details
cd terraform
terraform output database_fqdn
terraform output database_name
```

### 2. Development Environment

```powershell
# Python 3.11+
python --version

# Virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install django==5.0 psycopg2-binary bcrypt pytest pytest-django pytest-cov
```

---

## Step 1: Initialize Django Project

```powershell
# Create Django project
django-admin startproject taskmanager .

# Create accounts app
python manage.py startapp accounts

# Verify structure
ls
# Expected: manage.py, taskmanager/, accounts/, venv/
```

---

## Step 2: Configure Database

Edit `taskmanager/settings/base.py`:

```python
# Split settings
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',  # Feature 001
]

# Custom User model (MUST be set before first migration)
AUTH_USER_MODEL = 'accounts.User'

# Password hashers (bcrypt first)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Database (from Terraform outputs)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DATABASE_HOST'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},
    }
}

# Security settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True  # Force HTTPS
```

Create `taskmanager/settings/development.py`:
```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

---

## Step 3: Load Environment Variables

```powershell
# From Feature 004 Terraform outputs
cd terraform
.\set-env-vars.ps1  # Loads DATABASE_HOST, DATABASE_NAME, etc.

# Or manually:
$env:DATABASE_HOST = "psql-dev-taskmanager-eastus.postgres.database.azure.com"
$env:DATABASE_NAME = "taskmanager"
$env:DATABASE_USER = "psqladmin"
$env:DATABASE_PASSWORD = "..." # From terraform output -raw database_admin_password
$env:DJANGO_SETTINGS_MODULE = "taskmanager.settings.development"
```

---

## Step 4: Create User Model

Edit `accounts/models.py` (see [data-model.md](data-model.md) for full schema):

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, db_index=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user'
        ordering = ['-date_joined']
```

Create `accounts/managers.py`:
```python
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def normalize_email(self, email):
        return email.lower() if email else email
    
    def create_user(self, email, username, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
```

---

## Step 5: Run Migrations

```powershell
# Create migrations
python manage.py makemigrations accounts

# Expected output:
# Migrations for 'accounts':
#   accounts\migrations\0001_initial.py
#     - Create model User
#     - Create model AuthenticationLog

# Apply migrations
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying accounts.0001_initial... OK
#   Applying contenttypes.0001_initial... OK
#   Applying sessions.0001_initial... OK
```

---

## Step 6: Create Test User

```powershell
# Interactive shell
python manage.py shell

>>> from accounts.models import User
>>> user = User.objects.create_user(
...     email='test@example.com',
...     username='testuser',
...     password='TestPass123!'
... )
>>> user.check_password('TestPass123!')
True
>>> user.password[:7]  # Should start with 'bcrypt'
'bcrypt$'
>>> exit()
```

---

## Step 7: Create Views and Forms

Edit `accounts/forms.py`:
```python
from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
```

Edit `accounts/views.py`:
```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
```

---

## Step 8: Configure URLs

Edit `accounts/urls.py`:
```python
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
```

Edit `taskmanager/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
```

---

## Step 9: Create Templates

Create `templates/accounts/register.html`:
```html
<!DOCTYPE html>
<html>
<head><title>Register</title></head>
<body>
    <h1>Register</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Register</button>
    </form>
</body>
</html>
```

---

## Step 10: Run Development Server

```powershell
# Start server
python manage.py runserver

# Open browser: http://localhost:8000/accounts/register/
```

**Test Registration**:
1. Navigate to http://localhost:8000/accounts/register/
2. Fill form: email=`user@test.com`, username=`newuser`, password=`SecurePass123!`
3. Submit → Should redirect to login page
4. Verify in database:
   ```powershell
   python manage.py shell
   >>> from accounts.models import User
   >>> User.objects.filter(email='user@test.com').exists()
   True
   ```

---

## Step 11: Write Tests (TDD)

Create `tests/accounts/test_registration.py`:
```python
import pytest
from accounts.models import User

@pytest.mark.django_db
def test_user_registration_creates_user(client):
    response = client.post('/accounts/register/', {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
    })
    assert response.status_code == 302  # Redirect
    assert User.objects.filter(email='test@example.com').exists()

@pytest.mark.django_db
def test_user_password_is_hashed():
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='TestPass123!'
    )
    assert user.password != 'TestPass123!'
    assert user.password.startswith('bcrypt')
```

Run tests:
```powershell
pytest tests/accounts/ -v --cov=accounts

# Expected output:
# tests/accounts/test_registration.py::test_user_registration_creates_user PASSED
# tests/accounts/test_registration.py::test_user_password_is_hashed PASSED
# Coverage: 85%
```

---

## Common Operations

### Create Superuser
```powershell
python manage.py createsuperuser
# Email: admin@example.com
# Username: admin
# Password: AdminPass123!
```

### View Authentication Logs
```powershell
python manage.py shell
>>> from accounts.models import AuthenticationLog
>>> AuthenticationLog.objects.all()
```

### Reset Database
```powershell
python manage.py flush
python manage.py migrate
```

---

## Troubleshooting

### Issue: "relation 'accounts_user' does not exist"
**Solution**: Run migrations: `python manage.py migrate`

### Issue: "AUTH_USER_MODEL error"
**Solution**: Set `AUTH_USER_MODEL = 'accounts.User'` before first migration, then delete database and re-migrate

### Issue: Password not hashing
**Solution**: Verify `django[bcrypt]` installed: `pip install django[bcrypt]`

### Issue: CSRF token missing
**Solution**: Add `{% csrf_token %}` to all POST forms

---

## Next Steps

After authentication system works:
1. Deploy to Azure App Service (Feature 004 infrastructure)
2. Implement Feature 002 (Task CRUD) with user ownership
3. Add profile picture upload (Feature 003 blob storage)

---

## References

- [Django Tutorial - User Authentication](https://docs.djangoproject.com/en/5.0/intro/tutorial07/)
- [Django Authentication System](https://docs.djangoproject.com/en/5.0/topics/auth/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
