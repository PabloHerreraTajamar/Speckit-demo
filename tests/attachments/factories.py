"""
Factories for Attachment tests.
"""
import factory
from factory.django import DjangoModelFactory
from attachments.models import Attachment
from tests.tasks.factories import TaskFactory


class AttachmentFactory(DjangoModelFactory):
    """Factory for creating Attachment instances in tests."""
    
    class Meta:
        model = Attachment
    
    task = factory.SubFactory(TaskFactory)
    file_name = factory.Sequence(lambda n: f'test_file_{n}.pdf')
    blob_name = factory.Sequence(lambda n: f'task_{n}_blob_{n}.pdf')
    file_size = 1024  # 1KB default
    content_type = 'application/pdf'
