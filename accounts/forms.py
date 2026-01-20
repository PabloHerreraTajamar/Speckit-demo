"""
Forms for user authentication.

This module contains forms for user registration, login, and profile management.
"""

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from accounts.validators import validate_password_complexity, validate_username

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """
    Form for user registration.

    Handles email/username/password validation and user creation with bcrypt hashing.

    Fields:
        email: User's email address (will be normalized to lowercase)
        username: Unique username (3-30 alphanumeric characters)
        password: Plain text password (will be hashed with bcrypt)
        password_confirm: Password confirmation field
    """

    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password_complexity],
        help_text="Minimum 8 characters with uppercase, lowercase, digit, and special character",
    )
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add username validator to the field
        self.fields["username"].validators.append(validate_username)

        # Customize field attributes
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "your.email@example.com"}
        )
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "username"}
        )
        self.fields["password"].widget.attrs.update({"class": "form-control"})
        self.fields["password_confirm"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        """
        Validate email uniqueness and normalize to lowercase.

        Returns:
            str: Normalized email address

        Raises:
            ValidationError: If email already exists
        """
        email = self.cleaned_data.get("email")

        if not email:
            raise ValidationError("Email address is required")

        # Normalize email to lowercase
        email = email.lower()

        # Check if email already exists (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")

        return email

    def clean(self):
        """
        Validate that passwords match.

        Returns:
            dict: Cleaned data

        Raises:
            ValidationError: If passwords don't match
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError({"password_confirm": "Passwords do not match."})

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user with hashed password.

        Args:
            commit: Whether to save to database immediately

        Returns:
            User: The created user instance
        """
        user = super().save(commit=False)

        # Use set_password to hash with bcrypt
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    """
    Form for user login.

    Authenticates users with email/password and provides generic error messages
    to prevent user enumeration attacks.

    Fields:
        email: User's email address
        password: User's password
    """

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "your.email@example.com",
                "autocomplete": "email",
            }
        ),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "current-password"}
        ),
        label="Password",
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validate credentials and authenticate user.

        Returns:
            dict: Cleaned data

        Raises:
            ValidationError: If credentials are invalid
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            # Normalize email to lowercase
            email = email.lower()

            # Try to get the user
            try:
                user = User.objects.get(email__iexact=email)

                # Check password
                if user.check_password(password):
                    self.user = user
                else:
                    # Generic error message to prevent user enumeration
                    raise ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                # Generic error message to prevent user enumeration
                raise ValidationError("Invalid email or password.")

        return cleaned_data

    def get_user(self):
        """
        Return the authenticated user.

        Returns:
            User or None: Authenticated user if credentials are valid
        """
        return self.user


class ProfileForm(forms.ModelForm):
    """
    Form for user profile management.

    Allows users to update their first name, last name, and email.
    Validates email uniqueness (excluding current user).
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First Name",
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last Name",
                    "autocomplete": "family-name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                    "autocomplete": "email",
                }
            ),
        }

    def clean_email(self):
        """
        Validate email uniqueness.

        Ensures no other user has this email, but allows the current user
        to keep their existing email.

        Returns:
            str: Normalized (lowercase) email address

        Raises:
            ValidationError: If email is already in use by another user
        """
        email = self.cleaned_data.get("email", "").lower()

        # Check if another user has this email
        qs = User.objects.filter(email=email)

        # Exclude current user from check (allow keeping same email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("This email address is already in use.")

        return email


class ChangePasswordForm(forms.Form):
    """Form for changing user password."""

    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Current Password"}
        )
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New Password"}),
        help_text="Enter a strong password",
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm New Password"}
        )
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """Validate current password is correct."""
        current_password = self.cleaned_data.get("current_password")
        if self.user and not self.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        """Validate new passwords match and meet requirements."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise ValidationError("New passwords do not match.")

            # Validate password strength
            if self.user:
                try:
                    password_validation.validate_password(new_password, self.user)
                except ValidationError as e:
                    raise ValidationError({"new_password": e.messages})

        return cleaned_data

    def save(self):
        """Update user password."""
        if self.user:
            self.user.set_password(self.cleaned_data["new_password"])
            self.user.save()
        return self.user
