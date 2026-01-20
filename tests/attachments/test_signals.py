"""
Tests for attachment signal handlers.
"""
import pytest
from unittest.mock import Mock, patch
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
class TestAttachmentDeletionSignal:
    """Tests for attachment deletion signal handler."""
    
    def test_blob_deleted_when_attachment_deleted(self, task):
        """Test that blob is deleted from Azure storage when attachment is deleted."""
        attachment = Attachment.objects.create(
            task=task,
            file_name='test.pdf',
            blob_name='unique-blob.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            mock_storage_instance = Mock()
            MockStorage.return_value = mock_storage_instance
            mock_storage_instance.exists.return_value = True
            
            attachment.delete()
            
            mock_storage_instance.exists.assert_called_once_with('unique-blob.pdf')
            mock_storage_instance.delete.assert_called_once_with('unique-blob.pdf')
    
    def test_signal_handles_missing_blob(self, task):
        """Test that signal handles case where blob doesn't exist in storage."""
        attachment = Attachment.objects.create(
            task=task,
            file_name='test.pdf',
            blob_name='missing-blob.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            mock_storage_instance = Mock()
            MockStorage.return_value = mock_storage_instance
            mock_storage_instance.exists.return_value = False
            
            # Should not raise exception
            attachment.delete()
            
            mock_storage_instance.exists.assert_called_once_with('missing-blob.pdf')
            mock_storage_instance.delete.assert_not_called()
    
    def test_db_deletion_proceeds_despite_storage_error(self, task):
        """Test that DB deletion proceeds even if blob deletion fails."""
        attachment = Attachment.objects.create(
            task=task,
            file_name='test.pdf',
            blob_name='error-blob.pdf',
            file_size=1024,
            content_type='application/pdf'
        )
        
        attachment_id = attachment.id
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            MockStorage.side_effect = Exception("Storage connection error")
            
            # Should not raise exception - DB deletion should proceed
            attachment.delete()
        
        # Verify attachment was deleted from DB
        assert not Attachment.objects.filter(id=attachment_id).exists()
    
    def test_cascade_delete_on_task_deletion(self, task):
        """Test that attachments are deleted when parent task is deleted."""
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
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            mock_storage_instance = Mock()
            MockStorage.return_value = mock_storage_instance
            mock_storage_instance.exists.return_value = True
            
            task.delete()
            
            # Both blobs should be deleted
            assert mock_storage_instance.delete.call_count == 2
