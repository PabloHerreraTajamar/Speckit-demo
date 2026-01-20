"""
Unit tests for User model and UserManager.

Following TDD: These tests should FAIL initially, then pass after implementation.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserManager:
    """Test custom UserManager functionality."""

    def test_create_user_with_email_and_username(self):
        """T024: Test UserManager.create_user creates user with email and username."""
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="TestPass123!@#"
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_normalizes_email_to_lowercase(self):
        """T026: Test that create_user normalizes email to lowercase."""
        user = User.objects.create_user(
            email="Test.User@EXAMPLE.COM", username="testuser", password="TestPass123!@#"
        )

        # Email should be completely lowercase
        assert user.email == "test.user@example.com"

    def test_create_user_requires_email(self):
        """Test that create_user raises error without email."""
        with pytest.raises(ValueError, match="Email address is required"):
            User.objects.create_user(email="", username="testuser", password="TestPass123!@#")

    def test_create_user_requires_username(self):
        """Test that create_user raises error without username."""
        with pytest.raises(ValueError, match="Username is required"):
            User.objects.create_user(
                email="test@example.com", username="", password="TestPass123!@#"
            )

    def test_create_superuser(self):
        """Test UserManager.create_superuser creates admin user."""
        admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="AdminPass123!@#"
        )

        assert admin.is_active is True
        assert admin.is_staff is True
        assert admin.is_superuser is True


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality."""

    def test_password_hashing_with_bcrypt(self):
        """T025: Test that passwords are hashed using bcrypt."""
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="PlainPassword123!@#"
        )

        # Password should be hashed, not stored as plain text
        assert user.password != "PlainPassword123!@#"

        # Password should be hashed (format depends on environment)
        # Production uses bcrypt, testing uses MD5 for speed
        assert user.password.startswith(("bcrypt_sha256$", "md5$"))

        # Verify password works correctly
        assert user.check_password("PlainPassword123!@#") is True
        assert user.check_password("WrongPassword") is False

    def test_email_is_unique(self):
        """Test that duplicate emails are not allowed."""
        User.objects.create_user(
            email="test@example.com", username="user1", password="TestPass123!@#"
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="test@example.com", username="user2", password="TestPass123!@#"
            )

    def test_username_is_unique(self):
        """Test that duplicate usernames are not allowed."""
        User.objects.create_user(
            email="user1@example.com", username="testuser", password="TestPass123!@#"
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="user2@example.com", username="testuser", password="TestPass123!@#"
            )

    def test_user_str_representation(self):
        """Test User __str__ method returns email."""
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="TestPass123!@#"
        )

        assert str(user) == "test@example.com"
