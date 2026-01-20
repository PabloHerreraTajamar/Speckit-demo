"""
Validators for Task model fields.
"""

from django.core.exceptions import ValidationError


def validate_title_length(value):
    """
    Validate task title is not empty and within length limits.

    Raises:
        ValidationError: If title is empty after trimming or exceeds 200 chars
    """
    if not value or len(value.strip()) == 0:
        raise ValidationError("Title cannot be empty", code="empty_title")
    if len(value) > 200:
        raise ValidationError(
            "Title cannot exceed 200 characters", code="title_too_long"
        )


def validate_description_length(value):
    """
    Validate task description length.

    Raises:
        ValidationError: If description exceeds 2000 chars
    """
    if value and len(value) > 2000:
        raise ValidationError(
            "Description cannot exceed 2000 characters", code="description_too_long"
        )
