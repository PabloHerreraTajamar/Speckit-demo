"""
Views for user authentication.

This module contains views for user registration, login, logout, and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm


@csrf_protect
@require_http_methods(["GET", "POST"])
def register(request):
    """
    Handle user registration.

    GET: Display registration form
    POST: Process registration form and create user

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered registration form or redirect to login
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            messages.success(
                request, f"Account created successfully for {user.email}! You can now log in."
            )

            # Redirect to login page after successful registration
            return redirect("accounts:login")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login.

    GET: Display login form
    POST: Authenticate user and create session

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered login form or redirect to dashboard
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect(request.GET.get("next", "/tasks/"))

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.get_user()

            # Create session using Django's login function
            auth_login(request, user)

            messages.success(request, f"Welcome back, {user.email}!")

            # Redirect to 'next' parameter or default to tasks list
            next_url = request.GET.get("next", "/tasks/")
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request):
    """
    Handle user logout.

    POST: Destroy user session and logout

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Redirect to login page
    """
    # Logout user (destroys session)
    auth_logout(request)

    messages.success(request, "You have been logged out successfully.")

    return redirect("accounts:login")


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """
    Handle user profile viewing and updating.

    GET: Display profile form with current user data
    POST: Update user profile information

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered profile form or redirect to profile
    """
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

            messages.success(request, "Profile updated successfully!")

            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """
    Handle user password change.

    GET: Display password change form
    POST: Process password change and redirect to profile

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered password change form or redirect to profile
    """
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()

            messages.success(request, "Password changed successfully!")

            return redirect("accounts:profile")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, "accounts/change_password.html", {"form": form})
