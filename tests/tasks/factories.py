"""
Factory classes for generating test data.
"""

import factory
from django.utils import timezone

from accounts.models import User
from tasks.models import Task


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances in tests."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if create:
            obj.set_password(extracted or "testpass123")
            obj.save()


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory for creating Task instances in tests."""

    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker("paragraph")
    owner = factory.SubFactory(UserFactory)
    priority = "medium"
    status = "pending"
    due_date = factory.Faker("future_date", end_date="+30d")
