import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_password_complexity(password):
    """
    Validate password meets complexity requirements (FR-005).

    Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

    Args:
        password: Password string to validate

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise ValidationError(
            _("Password must be at least 8 characters long."), code="password_too_short"
        )

    if not re.search(r"[A-Z]", password):
        raise ValidationError(
            _("Password must contain at least one uppercase letter."), code="password_no_upper"
        )

    if not re.search(r"[a-z]", password):
        raise ValidationError(
            _("Password must contain at least one lowercase letter."), code="password_no_lower"
        )

    if not re.search(r"\d", password):
        raise ValidationError(
            _("Password must contain at least one digit."), code="password_no_digit"
        )

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            _('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'),
            code="password_no_special",
        )


def validate_username(username):
    """
    Validate username format (FR-003).

    Requirements:
        - 3-30 characters
        - Alphanumeric only (letters and numbers)

    Args:
        username: Username string to validate

    Raises:
        ValidationError: If username doesn't meet requirements
    """
    if len(username) < 3:
        raise ValidationError(
            _("Username must be at least 3 characters long."), code="username_too_short"
        )

    if len(username) > 30:
        raise ValidationError(
            _("Username must not exceed 30 characters."), code="username_too_long"
        )

    if not re.match(r"^[a-zA-Z0-9]+$", username):
        raise ValidationError(
            _("Username must contain only letters and numbers."), code="username_invalid_characters"
        )
