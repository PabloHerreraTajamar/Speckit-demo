from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses email as the primary authentication field instead of username.

    Fields:
        email: Unique email address (used for login)
        username: Unique username (3-30 alphanumeric characters)
        first_name: Optional first name
        last_name: Optional last name
        date_joined: Account creation timestamp
        last_login: Last successful login timestamp
        is_active: Account active status
        is_staff: Admin panel access
        is_superuser: Full admin privileges
    """

    email = models.EmailField(
        unique=True, db_index=True, help_text="User's email address (used for login)"
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Unique username (3-30 alphanumeric characters)",
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    objects = UserManager()

    # Use email for authentication instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Required for createsuperuser command

    class Meta:
        db_table = "accounts_user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


class AuthenticationLog(models.Model):
    """
    Audit log for all authentication events.
    Tracks user registration, login, logout, and failed login attempts.

    Fields:
        user: Foreign key to User (null for failed login attempts)
        event_type: Type of event (registration, login, logout, failed_login)
        ip_address: IP address of the request
        user_agent: Browser user agent string
        timestamp: When the event occurred
        success: Whether the event succeeded (True for all except failed_login)
        metadata: Optional JSON field for additional event data
    """

    EVENT_TYPES = [
        ("registration", "User Registration"),
        ("login", "User Login"),
        ("logout", "User Logout"),
        ("failed_login", "Failed Login Attempt"),
        ("password_change", "Password Change"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authentication_logs",
        help_text="User who performed the action (null for failed logins)",
    )
    event_type = models.CharField(
        max_length=20, choices=EVENT_TYPES, db_index=True, help_text="Type of authentication event"
    )
    ip_address = models.GenericIPAddressField(help_text="IP address of the request")
    user_agent = models.TextField(blank=True, help_text="Browser user agent string")
    timestamp = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When the event occurred"
    )
    success = models.BooleanField(default=True, help_text="Whether the event succeeded")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional event data (JSON)")

    class Meta:
        db_table = "accounts_authentication_log"
        verbose_name = "authentication log"
        verbose_name_plural = "authentication logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp", "event_type"]),
            models.Index(fields=["user", "-timestamp"]),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else "Unknown"
        return f"{self.event_type} - {user_email} - {self.timestamp}"
