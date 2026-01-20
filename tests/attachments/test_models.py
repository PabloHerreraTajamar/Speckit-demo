"""
Tests for Attachment model.
"""
import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from attachments.models import Attachment
from tasks.models import Task


@pytest.fixture
def user(django_user_model):
    """Create test user."""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def task(user):
    """Create test task."""
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        status='todo',
        priority='medium',
        owner=user
    )


@pytest.mark.django_db
class TestAttachmentModel:
    """Tests for Attachment model."""
    
    def test_create_attachment(self, task):
        """Test creating attachment with required fields."""
        attachment = Attachment.objects.create(
            task=task,
            file_name='test.pdf',
            blob_name='unique-blob-name.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        assert attachment.id is not None
        assert attachment.task == task
        assert attachment.file_name == 'test.pdf'
        assert attachment.blob_name == 'unique-blob-name.pdf'
        assert attachment.file_size == 1024
        assert attachment.content_type == 'application/pdf'
        assert attachment.created_at is not None
    
    def test_attachment_string_representation(self, task):
        """Test __str__ method."""
        attachment = Attachment.objects.create(
            task=task,
            file_name='document.pdf',
            blob_name='blob.pdf',
            file_size=2048,
            content_type='application/pdf'
        )
        
        assert str(attachment) == f'document.pdf (Task: {task.id})'
    
    def test_task_can_have_multiple_attachments(self, task):
        """Test that a task can have multiple attachments."""
        attachment1 = Attachment.objects.create(
            task=task,
            file_name='file1.pdf',
            blob_name='blob1.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        attachment2 = Attachment.objects.create(
            task=task,
            file_name='file2.jpg',
            blob_name='blob2.jpg',
            file_size=2048,
            content_type='image/jpeg'
        )
        
        assert task.attachments.count() == 2
        assert attachment1 in task.attachments.all()
        assert attachment2 in task.attachments.all()
    
    def test_attachment_ordering(self, task):
        """Test that attachments are ordered by creation date (newest first)."""
        attachment1 = Attachment.objects.create(
            task=task,
            file_name='first.pdf',
            blob_name='blob1.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        attachment2 = Attachment.objects.create(
            task=task,
            file_name='second.pdf',
            blob_name='blob2.pdf',
            file_size=2048,
            content_type='application/pdf'
        )
        
        attachments = task.attachments.all()
        assert attachments[0] == attachment2  # Newest first
        assert attachments[1] == attachment1
    
    def test_file_size_positive(self, task):
        """Test that file size must be positive."""
        with pytest.raises(ValidationError):
            attachment = Attachment(
                task=task,
                file_name='test.pdf',
                blob_name='blob.pdf',
                file_size=0,  # Invalid: zero size
                content_type='application/pdf'
            )
            attachment.full_clean()
    
    def test_blob_name_unique(self, task):
        """Test that blob names must be unique."""
        Attachment.objects.create(
            task=task,
            file_name='file1.pdf',
            blob_name='unique-blob.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        # Try to create another attachment with the same blob name
        with pytest.raises(Exception):  # Will raise IntegrityError
            Attachment.objects.create(
                task=task,
                file_name='file2.pdf',
                blob_name='unique-blob.pdf',  # Duplicate
                file_size=2048,
                content_type='application/pdf'
            )
