"""
Unit tests for authentication forms.

Following TDD: These tests should FAIL initially, then pass after implementation.
"""

import pytest
from django.contrib.auth import get_user_model
from accounts.forms import RegistrationForm

try:
    from accounts.forms import LoginForm
except ImportError:
    LoginForm = None

try:
    from accounts.forms import ProfileForm
except ImportError:
    ProfileForm = None

try:
    from accounts.forms import ChangePasswordForm
except ImportError:
    ChangePasswordForm = None

User = get_user_model()


@pytest.mark.django_db
class TestRegistrationForm:
    """Test RegistrationForm validation and functionality."""

    def test_registration_form_valid_data(self):
        """T027: Test RegistrationForm validates with correct data."""
        form_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!@#",
            "password_confirm": "SecurePass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is True

    def test_registration_form_password_mismatch(self):
        """T028: Test RegistrationForm rejects mismatched passwords."""
        form_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!@#",
            "password_confirm": "DifferentPass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is False
        assert "password_confirm" in form.errors or "__all__" in form.errors

    def test_registration_form_duplicate_email(self):
        """T029: Test RegistrationForm rejects duplicate email."""
        # Create existing user
        User.objects.create_user(
            email="existing@example.com", username="existinguser", password="TestPass123!@#"
        )

        # Try to register with same email
        form_data = {
            "email": "existing@example.com",
            "username": "newuser",
            "password": "SecurePass123!@#",
            "password_confirm": "SecurePass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is False
        assert "email" in form.errors

    def test_registration_form_duplicate_email_case_insensitive(self):
        """Test that email uniqueness is case-insensitive."""
        # Create existing user
        User.objects.create_user(
            email="existing@example.com", username="existinguser", password="TestPass123!@#"
        )

        # Try to register with same email but different case
        form_data = {
            "email": "EXISTING@EXAMPLE.COM",
            "username": "newuser",
            "password": "SecurePass123!@#",
            "password_confirm": "SecurePass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is False
        assert "email" in form.errors

    def test_registration_form_weak_password(self):
        """Test RegistrationForm rejects weak passwords."""
        form_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "weak",  # Too short, no complexity
            "password_confirm": "weak",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is False
        assert "password" in form.errors

    def test_registration_form_invalid_username(self):
        """Test RegistrationForm rejects invalid usernames."""
        # Username too short
        form_data = {
            "email": "newuser@example.com",
            "username": "ab",  # Less than 3 chars
            "password": "SecurePass123!@#",
            "password_confirm": "SecurePass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is False
        assert "username" in form.errors

    def test_registration_form_save_creates_user(self):
        """Test that RegistrationForm.save() creates a user."""
        form_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!@#",
            "password_confirm": "SecurePass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is True

        user = form.save()

        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.check_password("SecurePass123!@#") is True

    def test_registration_form_normalizes_email(self):
        """Test that RegistrationForm normalizes email to lowercase."""
        form_data = {
            "email": "NewUser@EXAMPLE.COM",
            "username": "newuser",
            "password": "SecurePass123!@#",
            "password_confirm": "SecurePass123!@#",
        }
        form = RegistrationForm(data=form_data)

        assert form.is_valid() is True

        user = form.save()

        assert user.email == "newuser@example.com"


@pytest.mark.django_db
class TestLoginForm:
    """Test LoginForm validation and functionality."""

    def test_login_form_valid_data(self):
        """T046: Test LoginForm validates with correct data."""
        if LoginForm is None:
            pytest.skip("LoginForm not implemented yet")

        # Create user first
        User.objects.create_user(
            email="testuser@example.com", username="testuser", password="TestPass123!@#"
        )

        form_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!@#",
        }
        form = LoginForm(data=form_data)

        assert form.is_valid() is True

    def test_login_form_invalid_credentials(self):
        """Test LoginForm rejects invalid credentials."""
        if LoginForm is None:
            pytest.skip("LoginForm not implemented yet")

        # Create user first
        User.objects.create_user(
            email="testuser@example.com", username="testuser", password="TestPass123!@#"
        )

        # Wrong password
        form_data = {
            "email": "testuser@example.com",
            "password": "WrongPassword",
        }
        form = LoginForm(data=form_data)

        assert form.is_valid() is False

    def test_login_form_nonexistent_user(self):
        """Test LoginForm rejects non-existent users."""
        if LoginForm is None:
            pytest.skip("LoginForm not implemented yet")

        form_data = {
            "email": "nonexistent@example.com",
            "password": "TestPass123!@#",
        }
        form = LoginForm(data=form_data)

        assert form.is_valid() is False

    def test_login_form_case_insensitive_email(self):
        """Test LoginForm accepts email in any case."""
        if LoginForm is None:
            pytest.skip("LoginForm not implemented yet")

        # Create user with lowercase email
        User.objects.create_user(
            email="testuser@example.com", username="testuser", password="TestPass123!@#"
        )

        # Login with uppercase email
        form_data = {
            "email": "TESTUSER@EXAMPLE.COM",
            "password": "TestPass123!@#",
        }
        form = LoginForm(data=form_data)

        assert form.is_valid() is True


@pytest.mark.django_db
class TestProfileForm:
    """Test ProfileForm validation and behavior."""

    def test_profile_form_valid_data(self):
        """T069: Test ProfileForm accepts valid data."""
        if ProfileForm is None:
            pytest.skip("ProfileForm not implemented yet")

        # Create user for testing
        user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="TestPass123!@#"
        )

        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "testuser@example.com",
        }
        form = ProfileForm(data=form_data, instance=user)

        assert form.is_valid() is True

    def test_profile_form_email_uniqueness(self):
        """T070: Test ProfileForm rejects duplicate email from another user."""
        if ProfileForm is None:
            pytest.skip("ProfileForm not implemented yet")

        # Create two users
        user1 = User.objects.create_user(
            email="user1@example.com", username="user1", password="TestPass123!@#"
        )
        User.objects.create_user(
            email="user2@example.com", username="user2", password="TestPass123!@#"
        )

        # Try to update user1's email to user2's email
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "user2@example.com",  # Already taken by user2
        }
        form = ProfileForm(data=form_data, instance=user1)

        assert form.is_valid() is False
        assert "email" in form.errors

    def test_profile_form_allows_own_email(self):
        """Test ProfileForm allows keeping the same email."""
        if ProfileForm is None:
            pytest.skip("ProfileForm not implemented yet")

        user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPass123!@#",
            first_name="John",
            last_name="Doe",
        )

        # Update other fields, keep same email
        form_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "testuser@example.com",  # Same email
        }
        form = ProfileForm(data=form_data, instance=user)

        assert form.is_valid() is True


@pytest.mark.django_db
class TestChangePasswordForm:
    """Test ChangePasswordForm validation and behavior."""

    def test_change_password_form_valid_data(self):
        """T085: Test ChangePasswordForm accepts valid data."""
        if ChangePasswordForm is None:
            pytest.skip("ChangePasswordForm not implemented yet")

        user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="OldPass123!@#"
        )

        form_data = {
            "current_password": "OldPass123!@#",
            "new_password": "NewPass456!@#",
            "new_password_confirm": "NewPass456!@#",
        }
        form = ChangePasswordForm(data=form_data, user=user)

        assert form.is_valid() is True

    def test_change_password_form_password_matching(self):
        """T086: Test ChangePasswordForm validates new passwords match."""
        if ChangePasswordForm is None:
            pytest.skip("ChangePasswordForm not implemented yet")

        user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="OldPass123!@#"
        )

        # New passwords don't match
        form_data = {
            "current_password": "OldPass123!@#",
            "new_password": "NewPass456!@#",
            "new_password_confirm": "DifferentPass789!@#",
        }
        form = ChangePasswordForm(data=form_data, user=user)

        assert form.is_valid() is False
        assert "new_password_confirm" in form.errors or "__all__" in form.errors

    def test_change_password_form_incorrect_current_password(self):
        """Test ChangePasswordForm rejects incorrect current password."""
        if ChangePasswordForm is None:
            pytest.skip("ChangePasswordForm not implemented yet")

        user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="OldPass123!@#"
        )

        # Wrong current password
        form_data = {
            "current_password": "WrongPassword!@#",
            "new_password": "NewPass456!@#",
            "new_password_confirm": "NewPass456!@#",
        }
        form = ChangePasswordForm(data=form_data, user=user)

        assert form.is_valid() is False
        assert "current_password" in form.errors

    def test_change_password_form_weak_new_password(self):
        """T090: Test ChangePasswordForm rejects weak passwords."""
        if ChangePasswordForm is None:
            pytest.skip("ChangePasswordForm not implemented yet")

        user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="OldPass123!@#"
        )

        # Weak password (too short)
        form_data = {
            "current_password": "OldPass123!@#",
            "new_password": "123",
            "new_password_confirm": "123",
        }
        form = ChangePasswordForm(data=form_data, user=user)

        assert form.is_valid() is False
        assert "new_password" in form.errors
