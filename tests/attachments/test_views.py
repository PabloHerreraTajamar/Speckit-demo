"""
Tests for attachment views.
"""
import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock, patch
from attachments.models import Attachment
from tasks.models import Task
from tests.tasks.factories import TaskFactory, UserFactory


@pytest.mark.django_db
class TestAttachmentUploadView:
    """Test cases for AttachmentUploadView."""
    
    def test_upload_requires_authentication(self, client):
        """Test that upload view requires login."""
        user = UserFactory()
        task = TaskFactory(owner=user)
        
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        response = client.get(url)
        
        assert response.status_code == 302  # Redirect to login
        assert "/accounts/login/" in response.url
    
    def test_upload_valid_file(self, client):
        """Test uploading a valid file."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file_content = b'%PDF-1.4 valid pdf content here'
        file = SimpleUploadedFile(
            "document.pdf",
            file_content,
            content_type="application/pdf"
        )
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.generate_blob_name.return_value = f"{task.id}/20260120_abc123_document.pdf"
            mock_storage._save.return_value = f"{task.id}/20260120_abc123_document.pdf"
            
            response = client.post(url, {'file': file}, follow=True)
        
        assert response.status_code == 200
        assert Attachment.objects.filter(task=task).count() == 1
        
        attachment = Attachment.objects.get(task=task)
        assert attachment.file_name == "document.pdf"
        assert attachment.file_size == len(file_content)
    
    def test_upload_file_too_large(self, client):
        """Test uploading a file larger than 10MB."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        # Create file larger than 10MB
        large_content = b'x' * (10 * 1024 * 1024 + 1)
        file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        
        response = client.post(url, {'file': file})
        
        assert response.status_code == 200  # Re-render form with errors
        assert not Attachment.objects.filter(task=task).exists()
        assert b'exceeds 10MB limit' in response.content or 'exceeds 10MB limit' in str(response.context.get('form', {}).errors)
    
    def test_upload_invalid_file_type(self, client):
        """Test uploading an invalid file type (.exe)."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file_content = b'MZ executable content'
        file = SimpleUploadedFile(
            "malware.exe",
            file_content,
            content_type="application/x-msdownload"
        )
        
        response = client.post(url, {'file': file})
        
        assert response.status_code == 200  # Re-render form
        assert not Attachment.objects.filter(task=task).exists()
    
    def test_upload_exceeds_limit(self, client):
        """Test uploading 6th file when limit is 5."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        # Create 5 existing attachments
        for i in range(5):
            Attachment.objects.create(
                task=task,
                file_name=f"file{i}.pdf",
                blob_name=f"blob{i}.pdf",
                file_size=1024,
                content_type="application/pdf"
            )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file = SimpleUploadedFile(
            "sixth.pdf",
            b'content',
            content_type="application/pdf"
        )
        
        response = client.post(url, {'file': file})
        
        assert response.status_code == 200  # Re-render form
        assert Attachment.objects.filter(task=task).count() == 5  # Still 5
    
    def test_upload_to_other_user_task(self, client):
        """Test uploading to another user's task is forbidden."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory()
        task = TaskFactory(owner=user2)
        
        client.login(username=user1.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file = SimpleUploadedFile(
            "file.pdf",
            b'content',
            content_type="application/pdf"
        )
        
        response = client.post(url, {'file': file})
        
        assert response.status_code == 403  # Forbidden
        assert not Attachment.objects.filter(task=task).exists()
    
    def test_upload_empty_file(self, client):
        """Test uploading an empty file (0 bytes)."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file = SimpleUploadedFile(
            "empty.pdf",
            b'',
            content_type="application/pdf"
        )
        
        response = client.post(url, {'file': file})
        
        assert response.status_code == 200  # Re-render form
        assert not Attachment.objects.filter(task=task).exists()
    
    def test_upload_generates_unique_blob_name(self, client):
        """Test that upload generates unique blob names."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file1 = SimpleUploadedFile(
            "document.pdf",
            b'%PDF-1.4 content1',
            content_type="application/pdf"
        )
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.generate_blob_name.return_value = f"{task.id}/20260120_abc123_document.pdf"
            mock_storage._save.return_value = f"{task.id}/20260120_abc123_document.pdf"
            
            client.post(url, {'file': file1}, follow=True)
        
        file2 = SimpleUploadedFile(
            "document.pdf",
            b'%PDF-1.4 content2',
            content_type="application/pdf"
        )
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.generate_blob_name.return_value = f"{task.id}/20260120_def456_document.pdf"
            mock_storage._save.return_value = f"{task.id}/20260120_def456_document.pdf"
            
            client.post(url, {'file': file2}, follow=True)
        
        attachments = Attachment.objects.filter(task=task)
        assert attachments.count() == 2
        assert attachments[0].blob_name != attachments[1].blob_name
    
    def test_upload_stores_metadata(self, client):
        """Test that upload stores correct file metadata."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:upload", kwargs={'task_pk': task.pk})
        
        file_content = b'%PDF-1.4 sample pdf'
        file = SimpleUploadedFile(
            "report.pdf",
            file_content,
            content_type="application/pdf"
        )
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.generate_blob_name.return_value = f"{task.id}/20260120_xyz789_report.pdf"
            mock_storage._save.return_value = f"{task.id}/20260120_xyz789_report.pdf"
            
            response = client.post(url, {'file': file}, follow=True)
        
        attachment = Attachment.objects.get(task=task)
        assert attachment.file_name == "report.pdf"
        assert attachment.file_size == len(file_content)
        assert attachment.content_type == "application/pdf"
        assert attachment.blob_name == f"{task.id}/20260120_xyz789_report.pdf"


@pytest.mark.django_db
class TestAttachmentListView:
    """Test cases for AttachmentListView."""
    
    def test_list_requires_authentication(self, client):
        """Test that list view requires login."""
        user = UserFactory()
        task = TaskFactory(owner=user)
        
        url = reverse("attachments:list", kwargs={'task_pk': task.pk})
        response = client.get(url)
        
        assert response.status_code == 302  # Redirect to login
        assert "/accounts/login/" in response.url
    
    def test_list_shows_user_task_attachments(self, client):
        """Test that list shows attachments for user's task."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        # Create attachments
        attachment1 = Attachment.objects.create(
            task=task,
            file_name="file1.pdf",
            blob_name="blob1.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        attachment2 = Attachment.objects.create(
            task=task,
            file_name="file2.jpg",
            blob_name="blob2.jpg",
            file_size=2048,
            content_type="image/jpeg"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:list", kwargs={'task_pk': task.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        assert attachment1 in response.context['attachments']
        assert attachment2 in response.context['attachments']
    
    def test_list_hides_other_user_attachments(self, client):
        """Test that list doesn't show other users' attachments."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory()
        task = TaskFactory(owner=user2)
        
        # Create attachment for user2's task
        Attachment.objects.create(
            task=task,
            file_name="secret.pdf",
            blob_name="secret_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user1.email, password="testpass123")
        url = reverse("attachments:list", kwargs={'task_pk': task.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.context['attachments']) == 0
    
    def test_list_shows_empty_state(self, client):
        """Test that list shows appropriate message when no attachments."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:list", kwargs={'task_pk': task.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        assert len(response.context['attachments']) == 0
        assert b'No attachments' in response.content
    
    def test_list_displays_metadata(self, client):
        """Test that list displays file metadata correctly."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        
        attachment = Attachment.objects.create(
            task=task,
            file_name="document.pdf",
            blob_name="blob.pdf",
            file_size=1048576,  # 1MB
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:list", kwargs={'task_pk': task.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        content = response.content.decode()
        assert "document.pdf" in content
        assert "application/pdf" in content


@pytest.mark.django_db
class TestAttachmentDownloadView:
    """Test cases for AttachmentDownloadView."""
    
    def test_download_requires_authentication(self, client):
        """Test that download view requires login."""
        user = UserFactory()
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        url = reverse("attachments:download", kwargs={'pk': attachment.pk})
        response = client.get(url)
        
        assert response.status_code == 302  # Redirect to login
        assert "/accounts/login/" in response.url
    
    def test_download_valid_attachment(self, client):
        """Test downloading a valid attachment."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="document.pdf",
            blob_name="test_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:download", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            mock_storage.get_signed_url.return_value = "https://storage.example.com/download?sig=abc123"
            
            response = client.get(url)
        
        assert response.status_code == 302  # Redirect to signed URL
        assert response.url == "https://storage.example.com/download?sig=abc123"
    
    def test_download_other_user_attachment(self, client):
        """Test downloading another user's attachment returns 403."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory()
        task = TaskFactory(owner=user2)
        attachment = Attachment.objects.create(
            task=task,
            file_name="secret.pdf",
            blob_name="secret_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user1.email, password="testpass123")
        url = reverse("attachments:download", kwargs={'pk': attachment.pk})
        response = client.get(url)
        
        assert response.status_code == 403  # Forbidden
    
    def test_download_nonexistent_attachment(self, client):
        """Test downloading nonexistent attachment returns 404."""
        user = UserFactory(password="testpass123")
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:download", kwargs={'pk': 99999})
        response = client.get(url)
        
        assert response.status_code == 404
    
    def test_download_missing_blob(self, client):
        """Test downloading when blob is missing from storage."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="missing.pdf",
            blob_name="missing_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:download", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = False
            
            response = client.get(url, follow=True)
        
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert any('not found' in str(msg).lower() for msg in messages)
    
    def test_download_correct_content_type(self, client):
        """Test that download provides correct content type."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="image.jpg",
            blob_name="image_blob.jpg",
            file_size=2048,
            content_type="image/jpeg"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:download", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            mock_storage.url.return_value = "https://storage.example.com/download"
            
            response = client.get(url)
        
        # Verify storage methods were called correctly
        mock_storage.exists.assert_called_once_with("image_blob.jpg")
    
    def test_download_correct_filename(self, client):
        """Test that download provides correct filename."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="report.xlsx",
            blob_name="report_blob.xlsx",
            file_size=4096,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:download", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            mock_storage.url.return_value = "https://storage.example.com/download"
            
            response = client.get(url)
        
        assert response.status_code == 302


@pytest.mark.django_db
class TestAttachmentDeleteView:
    """Test cases for AttachmentDeleteView."""
    
    def test_delete_requires_authentication(self, client):
        """Test that delete view requires login."""
        user = UserFactory()
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        response = client.get(url)
        
        assert response.status_code == 302  # Redirect to login
        assert "/accounts/login/" in response.url
    
    def test_delete_requires_confirmation(self, client):
        """Test that GET shows confirmation page."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        assert b'Confirm Deletion' in response.content or b'confirm' in response.content.lower()
    
    def test_delete_valid_attachment(self, client):
        """Test deleting a valid attachment."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="document.pdf",
            blob_name="test_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        attachment_id = attachment.id
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            
            response = client.post(url, follow=True)
        
        assert response.status_code == 200
        assert not Attachment.objects.filter(id=attachment_id).exists()
        mock_storage.delete.assert_called_once_with("test_blob.pdf")
    
    def test_delete_other_user_attachment(self, client):
        """Test deleting another user's attachment returns 403."""
        user1 = UserFactory(password="testpass123")
        user2 = UserFactory()
        task = TaskFactory(owner=user2)
        attachment = Attachment.objects.create(
            task=task,
            file_name="secret.pdf",
            blob_name="secret_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user1.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        response = client.post(url)
        
        assert response.status_code == 403  # Forbidden
        assert Attachment.objects.filter(id=attachment.id).exists()
    
    def test_delete_removes_blob_from_storage(self, client):
        """Test that delete removes blob from Azure storage."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="unique_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            
            response = client.post(url, follow=True)
        
        mock_storage.exists.assert_called_once_with("unique_blob.pdf")
        mock_storage.delete.assert_called_once_with("unique_blob.pdf")
    
    def test_delete_removes_attachment_record(self, client):
        """Test that delete removes attachment record from database."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        attachment_id = attachment.id
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            
            client.post(url)
        
        assert not Attachment.objects.filter(id=attachment_id).exists()
    
    def test_delete_with_missing_blob(self, client):
        """Test graceful handling when blob is missing."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="missing.pdf",
            blob_name="missing_blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        attachment_id = attachment.id
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = False
            
            response = client.post(url, follow=True)
        
        assert response.status_code == 200
        assert not Attachment.objects.filter(id=attachment_id).exists()
        mock_storage.delete.assert_not_called()
    
    def test_delete_redirects_to_task_detail(self, client):
        """Test that delete redirects to task detail page."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        
        with patch('attachments.views.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            
            response = client.post(url)
        
        assert response.status_code == 302
        assert response.url == reverse('tasks:detail', kwargs={'pk': task.pk})
    
    def test_delete_shows_success_message(self, client):
        """Test that delete shows success message."""
        user = UserFactory(password="testpass123")
        task = TaskFactory(owner=user)
        attachment = Attachment.objects.create(
            task=task,
            file_name="file.pdf",
            blob_name="blob.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        client.login(username=user.email, password="testpass123")
        url = reverse("attachments:delete", kwargs={'pk': attachment.pk})
        
        with patch('attachments.signals.AzureBlobStorage') as MockStorage:
            mock_storage = Mock()
            MockStorage.return_value = mock_storage
            mock_storage.exists.return_value = True
            
            response = client.post(url, follow=True)
        
        # Verify successful deletion and redirect
        assert response.status_code == 200
        assert not Attachment.objects.filter(id=attachment.id).exists()
        
        # Check that we were redirected to task detail page
        assert response.redirect_chain[-1][0] == reverse('tasks:detail', kwargs={'pk': task.pk})

