"""
Tests for Azure Blob Storage backend.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from attachments.storage import AzureBlobStorage


@pytest.fixture
def mock_blob_service():
    """Mock Azure BlobServiceClient."""
    service_mock = MagicMock()
    container_mock = MagicMock()
    blob_mock = MagicMock()
    
    service_mock.get_blob_client.return_value = blob_mock
    service_mock.get_container_client.return_value = container_mock
    
    return service_mock


@pytest.fixture
def storage(mock_blob_service, mocker):
    """Create storage instance with mocked Azure client."""
    mocker.patch(
        'attachments.storage.BlobServiceClient.from_connection_string',
        return_value=mock_blob_service
    )
    
    # Mock Django settings
    mocker.patch(
        'attachments.storage.settings.AZURE_STORAGE_CONNECTION_STRING',
        'DefaultEndpointsProtocol=https;AccountName=test;'
    )
    mocker.patch(
        'attachments.storage.settings.AZURE_STORAGE_CONTAINER_NAME',
        'test-container'
    )
    
    storage = AzureBlobStorage()
    storage.blob_service_client = mock_blob_service
    return storage


class TestAzureBlobStorageInit:
    """Tests for storage initialization."""
    
    def test_storage_initializes_with_settings(self, mocker):
        """Test that storage initializes with Django settings."""
        mock_blob_service = MagicMock()
        mocker.patch(
            'attachments.storage.BlobServiceClient.from_connection_string',
            return_value=mock_blob_service
        )
        mocker.patch(
            'attachments.storage.settings.AZURE_STORAGE_CONNECTION_STRING',
            'test-connection-string'
        )
        mocker.patch(
            'attachments.storage.settings.AZURE_STORAGE_CONTAINER_NAME',
            'test-container'
        )
        
        storage = AzureBlobStorage()
        
        assert storage.container_name == 'test-container'


class TestSaveFile:
    """Tests for saving files to Azure Blob Storage."""
    
    def test_save_file_success(self, storage, mock_blob_service):
        """Test successful file upload."""
        file = SimpleUploadedFile("test.pdf", b"file content")
        blob_name = "test-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.upload_blob.return_value = None
        
        result = storage.save(blob_name, file)
        
        assert result == blob_name
        blob_client.upload_blob.assert_called_once()
    
    def test_save_file_overwrites_existing(self, storage, mock_blob_service):
        """Test that save overwrites existing blobs."""
        file = SimpleUploadedFile("test.pdf", b"new content")
        blob_name = "existing-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        
        storage.save(blob_name, file)
        
        # Should call upload with overwrite=True
        call_kwargs = blob_client.upload_blob.call_args.kwargs
        assert call_kwargs.get('overwrite') is True


class TestDeleteFile:
    """Tests for deleting files from Azure Blob Storage."""
    
    def test_delete_existing_file(self, storage, mock_blob_service):
        """Test deletion of existing blob."""
        blob_name = "test-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.exists.return_value = True
        
        result = storage.delete(blob_name)
        
        assert result is True
        blob_client.delete_blob.assert_called_once()
    
    def test_delete_non_existing_file(self, storage, mock_blob_service):
        """Test deletion of non-existing blob returns False."""
        blob_name = "non-existing.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.exists.return_value = False
        
        result = storage.delete(blob_name)
        
        assert result is False
        blob_client.delete_blob.assert_not_called()


class TestFileExists:
    """Tests for checking file existence."""
    
    def test_exists_returns_true_for_existing_file(self, storage, mock_blob_service):
        """Test exists() returns True for existing blob."""
        blob_name = "existing-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.exists.return_value = True
        
        result = storage.exists(blob_name)
        
        assert result is True
    
    def test_exists_returns_false_for_missing_file(self, storage, mock_blob_service):
        """Test exists() returns False for missing blob."""
        blob_name = "missing-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.exists.return_value = False
        
        result = storage.exists(blob_name)
        
        assert result is False


class TestGetSignedUrl:
    """Tests for generating signed URLs."""
    
    def test_get_signed_url_generates_valid_url(self, storage, mock_blob_service, mocker):
        """Test that signed URL is generated correctly."""
        blob_name = "test-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.url = "https://account.blob.core.windows.net/container/test-blob.pdf"
        
        # Mock generate_blob_sas function
        mocker.patch(
            'attachments.storage.generate_blob_sas',
            return_value='sas_token_123'
        )
        
        # Mock connection string parsing
        storage.connection_string = 'AccountName=testaccount;AccountKey=testkey123=='
        
        url = storage.get_signed_url(blob_name, expiry_hours=1)
        
        assert "https://" in url
        assert blob_name in url
        assert "sas_token_123" in url
    
    def test_get_signed_url_custom_expiry(self, storage, mock_blob_service, mocker):
        """Test that custom expiry time is applied."""
        blob_name = "test-blob.pdf"
        
        blob_client = mock_blob_service.get_blob_client.return_value
        blob_client.url = "https://account.blob.core.windows.net/container/test-blob.pdf"
        
        # Mock generate_blob_sas function
        mock_generate_sas = mocker.patch(
            'attachments.storage.generate_blob_sas',
            return_value='sas_token_123'
        )
        
        # Mock connection string parsing
        storage.connection_string = 'AccountName=testaccount;AccountKey=testkey123=='
        
        storage.get_signed_url(blob_name, expiry_hours=24)
        
        # Verify SAS token generation was called
        assert mock_generate_sas.called


class TestGetFileSize:
    """Tests for getting file size."""
    
    def test_get_size_returns_correct_value(self, storage, mock_blob_service):
        """Test that size() returns correct file size."""
        blob_name = "test-blob.pdf"
        expected_size = 1024
        
        blob_client = mock_blob_service.get_blob_client.return_value
        props = MagicMock()
        props.size = expected_size
        blob_client.get_blob_properties.return_value = props
        
        size = storage.size(blob_name)
        
        assert size == expected_size
