from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    Provides email-based authentication instead of username.
    """

    def normalize_email(self, email):
        """
        Normalize email by lowercasing the domain and local part.
        Overrides Django's default to lowercase the entire email.
        """
        if not email:
            return email
        return email.lower()

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular user with email and password.

        Args:
            email: User's email address (used for login)
            username: Unique username (3-30 alphanumeric characters)
            password: Plain text password (will be hashed)
            **extra_fields: Additional fields (first_name, last_name, etc.)

        Returns:
            User instance

        Raises:
            ValueError: If email or username is not provided
        """
        if not email:
            raise ValueError("Email address is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hash password with bcrypt
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser with admin privileges.

        Args:
            email: Admin email address
            username: Admin username
            password: Admin password
            **extra_fields: Additional fields

        Returns:
            User instance with admin privileges
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, username, password, **extra_fields)
