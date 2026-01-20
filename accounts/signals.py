"""
Django signal receivers for authentication events.

This module handles logging of authentication events (login, logout, failed attempts,
and password changes) to the AuthenticationLog model for security auditing.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import AuthenticationLog

User = get_user_model()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log successful user login.

    Args:
        sender: The class of the user that just logged in
        request: The current HttpRequest instance
        user: The user instance that just logged in
        **kwargs: Additional keyword arguments
    """
    ip_address = request.META.get("REMOTE_ADDR") or "127.0.0.1"
    user_agent = request.META.get("HTTP_USER_AGENT") or ""

    AuthenticationLog.objects.create(
        user=user, event_type="login", ip_address=ip_address, user_agent=user_agent, success=True
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Log failed user login attempt.

    Args:
        sender: The sender of the signal
        credentials: Dict containing credentials attempted (usually contains 'username')
        request: The current HttpRequest instance
        **kwargs: Additional keyword arguments
    """
    # Handle case where request may be None or META may not exist
    ip_address = "127.0.0.1"
    user_agent = ""

    if request and hasattr(request, "META") and request.META:
        ip_address = request.META.get("REMOTE_ADDR") or "127.0.0.1"
        user_agent = request.META.get("HTTP_USER_AGENT") or ""

    # Extract attempted email/username from credentials
    attempted_email = credentials.get("username", "")  # Django uses 'username' key even for email

    AuthenticationLog.objects.create(
        user=None,  # No user associated with failed login
        event_type="failed_login",
        ip_address=ip_address,
        user_agent=user_agent,
        success=False,
        metadata={"attempted_email": attempted_email},
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout.

    Args:
        sender: The class of the user that just logged out
        request: The current HttpRequest instance
        user: The user instance that just logged out
        **kwargs: Additional keyword arguments
    """
    # Handle case where request may be None or META may not exist
    ip_address = "127.0.0.1"
    user_agent = ""

    if request and hasattr(request, "META") and request.META:
        ip_address = request.META.get("REMOTE_ADDR") or "127.0.0.1"
        user_agent = request.META.get("HTTP_USER_AGENT") or ""

    AuthenticationLog.objects.create(
        user=user, event_type="logout", ip_address=ip_address, user_agent=user_agent, success=True
    )


@receiver(post_save, sender=User)
def log_password_change(sender, instance, **kwargs):
    """
    Log password change event.

    This signal is triggered when a user model is saved. We check if the password
    has changed to log the password change event.

    Args:
        sender: The User model class
        instance: The user instance being saved
        **kwargs: Additional keyword arguments
    """
    # Only log if this is an update (not creation) and password was changed
    if kwargs.get("created", False):
        return

    # Check if password was changed by comparing with database
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Password has been changed if the hashed password is different
            if old_instance.password != instance.password:
                AuthenticationLog.objects.create(
                    user=instance,
                    event_type="password_change",
                    ip_address="127.0.0.1",  # IP not available in model save
                    user_agent="",
                    success=True,
                )
        except User.DoesNotExist:
            pass
