from django.db import models
from django.core.validators import MinValueValidator
from tasks.models import Task


class Attachment(models.Model):
    """
    File attachment for a Task.
    Stores metadata about files uploaded to Azure Blob Storage.
    """
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text='Task this attachment belongs to'
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text='Original filename'
    )
    
    blob_name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Unique blob name in Azure storage'
    )
    
    file_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='File size in bytes'
    )
    
    content_type = models.CharField(
        max_length=100,
        help_text='MIME type of the file'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Upload timestamp'
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest first
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        indexes = [
            models.Index(fields=['task', '-created_at']),
            models.Index(fields=['blob_name']),
        ]
    
    def __str__(self):
        return f'{self.file_name} (Task: {self.task.id})'

