"""
Signal handlers for Task Attachment lifecycle events.
Handles cascade deletion of attachments when tasks are deleted.
"""
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from .models import Attachment
from .storage import AzureBlobStorage
import logging

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Attachment)
def delete_blob_on_attachment_delete(sender, instance, **kwargs):
    """
    Delete blob from Azure Storage when Attachment is deleted.
    
    Args:
        sender: Model class (Attachment)
        instance: Attachment instance being deleted
        **kwargs: Additional keyword arguments
    """
    try:
        storage = AzureBlobStorage()
        blob_name = instance.blob_name
        
        if storage.exists(blob_name):
            storage.delete(blob_name)
            logger.info(f'Deleted blob {blob_name} for attachment {instance.id}')
        else:
            logger.warning(f'Blob {blob_name} not found for attachment {instance.id}')
    
    except Exception as e:
        logger.error(f'Failed to delete blob {instance.blob_name}: {str(e)}')
        # Don't raise - allow DB deletion to proceed even if blob deletion fails

