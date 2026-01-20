"""
Azure Blob Storage backend for Task Attachments.
Handles file upload, download, and deletion operations.
"""
from datetime import datetime, timedelta, timezone
from django.core.files.storage import Storage
from django.conf import settings
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceNotFoundError, AzureError
import logging
import uuid
from .utils import sanitize_filename

logger = logging.getLogger(__name__)


class AzureBlobStorage(Storage):
    """
    Custom storage backend for Azure Blob Storage.
    Handles file upload, download, deletion, and URL generation with SAS tokens.
    """
    
    def __init__(self):
        """Initialize Azure Blob Storage client."""
        try:
            self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
            self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {str(e)}")
            raise
    
    def _get_blob_client(self, name):
        """
        Get blob client for specific blob.
        
        Args:
            name: Blob name
            
        Returns:
            BlobClient instance
        """
        return self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=name
        )
    
    def generate_blob_name(self, task_id, original_filename):
        """
        Generate unique blob name using pattern: task_id/timestamp_uuid_sanitized_filename
        
        Args:
            task_id: Task ID
            original_filename: Original filename
            
        Returns:
            Unique blob name
        """
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        sanitized = sanitize_filename(original_filename)
        
        return f"{task_id}/{timestamp}_{unique_id}_{sanitized}"
    
    def save(self, name, content, max_length=None):
        """
        Save file to Azure Blob Storage.
        
        Args:
            name: Blob name
            content: File content
            max_length: Not used
            
        Returns:
            Blob name
            
        Raises:
            AzureError: If upload fails
        """
        try:
            blob_client = self._get_blob_client(name)
            blob_client.upload_blob(content, overwrite=True)
            logger.info(f"Successfully uploaded blob: {name}")
            return name
        except AzureError as e:
            logger.error(f"Failed to upload blob {name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading blob {name}: {str(e)}")
            raise
    
    def delete(self, name):
        """
        Delete file from Azure Blob Storage.
        
        Args:
            name: Blob name
            
        Returns:
            True if deleted, False if not found
        """
        try:
            blob_client = self._get_blob_client(name)
            
            if blob_client.exists():
                blob_client.delete_blob()
                logger.info(f"Successfully deleted blob: {name}")
                return True
            
            logger.warning(f"Blob not found for deletion: {name}")
            return False
        except AzureError as e:
            logger.error(f"Failed to delete blob {name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting blob {name}: {str(e)}")
            raise
    
    def exists(self, name):
        """
        Check if blob exists in Azure Blob Storage.
        
        Args:
            name: Blob name
            
        Returns:
            True if exists, False otherwise
        """
        blob_client = self._get_blob_client(name)
        return blob_client.exists()
    
    def size(self, name):
        """
        Get blob size in bytes.
        
        Args:
            name: Blob name
            
        Returns:
            Size in bytes
        """
        blob_client = self._get_blob_client(name)
        properties = blob_client.get_blob_properties()
        return properties.size
    
    def url(self, name):
        """
        Get blob URL (without SAS token).
        Not recommended - use get_signed_url() instead.
        
        Args:
            name: Blob name
            
        Returns:
            Blob URL
        """
        blob_client = self._get_blob_client(name)
        return blob_client.url
    
    def get_signed_url(self, name, expiry_hours=1):
        """
        Generate signed URL with SAS token for secure blob access.
        
        Args:
            name: Blob name
            expiry_hours: URL expiry time in hours (default 1 hour)
            
        Returns:
            Signed URL with SAS token
        """
        blob_client = self._get_blob_client(name)
        
        # Extract account name and key from connection string
        conn_parts = dict(item.split('=', 1) for item in self.connection_string.split(';') if '=' in item)
        account_name = conn_parts.get('AccountName')
        account_key = conn_parts.get('AccountKey')
        
        # Generate SAS token with timezone-aware datetime
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self.container_name,
            blob_name=name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        )
        
        # Return signed URL
        return f"{blob_client.url}?{sas_token}"

