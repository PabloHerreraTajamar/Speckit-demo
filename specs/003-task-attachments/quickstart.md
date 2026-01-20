# Quickstart Guide - Task File Attachments

**Date**: 2026-01-19  
**Feature**: 003-task-attachments  
**Branch**: `003-task-attachments`

## Overview

This guide helps developers set up and test the file attachment feature using Azure Blob Storage. Follow these steps to create the Attachment model, validators, storage backend, and test upload/download workflows.

---

## Prerequisites

- Feature 001 (User Authentication) completed
- Feature 002 (Task CRUD) completed
- Feature 004 (Azure Infrastructure) completed
- Azure Blob Storage provisioned
- PostgreSQL database running
- Python 3.11+ virtual environment activated
- Django project initialized

---

## Step 1: Install Dependencies

```powershell
# Install Azure Blob Storage SDK
pip install azure-storage-blob==12.19.0

# Install python-magic for MIME type detection
# Windows
pip install python-magic-bin==0.4.14

# Linux (also requires system package)
pip install python-magic==0.4.27
# sudo apt-get install libmagic1
```

**Update requirements.txt**:
```
azure-storage-blob==12.19.0
python-magic-bin==0.4.14  # Windows
# python-magic==0.4.27  # Linux
```

---

## Step 2: Configure Azure Storage Settings

**File**: `settings.py`

```python
import os

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'taskmanager-attachments-dev')
AZURE_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_STORAGE_ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB (Django default)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB (matches attachment limit)
```

**Environment Variables** (`.env` file):
```bash
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=youraccountname;AccountKey=youraccountkey;EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER_NAME="taskmanager-attachments-dev"
AZURE_STORAGE_ACCOUNT_NAME="youraccountname"
AZURE_STORAGE_ACCOUNT_KEY="youraccountkey"
```

---

## Step 3: Create Django App

```powershell
# Create attachments app
python manage.py startapp attachments

# Add to INSTALLED_APPS in settings.py
# 'attachments',
```

---

## Step 4: Create Storage Backend

**File**: `attachments/storage.py`

```python
from django.core.files.storage import Storage
from django.conf import settings
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import uuid
import os
from django.utils.text import slugify

class AzureBlobStorage(Storage):
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.client = BlobServiceClient.from_connection_string(self.connection_string)
    
    def generate_blob_name(self, task_id, original_filename):
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        name, ext = os.path.splitext(original_filename)
        safe_name = slugify(name)[:50]
        safe_filename = f"{safe_name}{ext.lower()}"
        return f"{task_id}/{timestamp}_{unique_id}_{safe_filename}"
    
    def _save(self, name, content):
        blob_client = self.client.get_blob_client(container=self.container_name, blob=name)
        blob_client.upload_blob(content, overwrite=False)
        return name
    
    def delete(self, name):
        blob_client = self.client.get_blob_client(container=self.container_name, blob=name)
        blob_client.delete_blob()
    
    def url(self, name):
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{name}"
        return f"{blob_url}?{sas_token}"
```

---

## Step 5: Create Validators

**File**: `attachments/validators.py`

```python
from django.core.exceptions import ValidationError
import magic
import os

def validate_file_size(file):
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(f"File size exceeds 10MB limit. File size: {file.size / 1024 / 1024:.2f}MB")
    if file.size == 0:
        raise ValidationError("Cannot upload empty file (0 bytes)")

def validate_mime_type(file):
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
        'image/jpeg',
        'image/png',
    }
    
    file.seek(0)
    file_header = file.read(2048)
    file.seek(0)
    
    mime = magic.from_buffer(file_header, mime=True)
    
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"File type '{mime}' not allowed. Allowed: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG")
    
    return mime
```

---

## Step 6: Create Attachment Model

**File**: `attachments/models.py`

```python
from django.db import models
from django.core.exceptions import ValidationError
from tasks.models import Task
from .storage import AzureBlobStorage
import logging

logger = logging.getLogger(__name__)

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    original_filename = models.CharField(max_length=255)
    blob_name = models.CharField(max_length=500, unique=True, db_index=True)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'attachments_attachment'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['task', '-uploaded_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(file_size__lte=10485760),
                name='file_size_limit'
            )
        ]
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New attachment
            existing_count = Attachment.objects.filter(task=self.task).count()
            if existing_count >= 5:
                raise ValidationError("Maximum 5 attachments per task")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        storage = AzureBlobStorage()
        try:
            storage.delete(self.blob_name)
        except Exception as e:
            logger.error(f"Failed to delete blob {self.blob_name}: {e}")
        super().delete(*args, **kwargs)
    
    def get_download_url(self):
        storage = AzureBlobStorage()
        return storage.url(self.blob_name)
    
    def __str__(self):
        return f"{self.original_filename} ({self.file_size} bytes)"
```

---

## Step 7: Create Signal Handler

**File**: `attachments/signals.py`

```python
from django.db.models.signals import post_delete
from django.dispatch import receiver
from tasks.models import Task
from .storage import AzureBlobStorage
import logging

logger = logging.getLogger(__name__)

@receiver(post_delete, sender=Task)
def delete_task_attachments(sender, instance, **kwargs):
    storage = AzureBlobStorage()
    container_client = storage.client.get_container_client(storage.container_name)
    
    try:
        blob_list = container_client.list_blobs(name_starts_with=f"{instance.id}/")
        for blob in blob_list:
            try:
                container_client.delete_blob(blob.name)
                logger.info(f"Deleted blob {blob.name}")
            except Exception as e:
                logger.error(f"Failed to delete blob {blob.name}: {e}")
    except Exception as e:
        logger.error(f"Failed to list blobs for task {instance.id}: {e}")
```

**File**: `attachments/apps.py`

```python
from django.apps import AppConfig

class AttachmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attachments'
    
    def ready(self):
        import attachments.signals  # Register signal handlers
```

---

## Step 8: Run Migrations

```powershell
# Create migration file
python manage.py makemigrations attachments

# Apply migration
python manage.py migrate attachments
```

---

## Step 9: Create Views

**File**: `attachments/views.py`

```python
from django.views.generic import FormView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from tasks.models import Task
from .models import Attachment
from .forms import AttachmentUploadForm
from .storage import AzureBlobStorage
from .validators import validate_file_size, validate_mime_type

class AttachmentUploadView(LoginRequiredMixin, FormView):
    form_class = AttachmentUploadForm
    template_name = 'attachments/upload.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.task = get_object_or_404(Task, pk=kwargs['task_id'])
        if self.task.owner != request.user:
            raise PermissionDenied("You can only attach files to your own tasks")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        
        # Generate blob name and upload
        storage = AzureBlobStorage()
        blob_name = storage.generate_blob_name(self.task.id, uploaded_file.name)
        storage._save(blob_name, uploaded_file)
        
        # Create attachment record
        Attachment.objects.create(
            task=self.task,
            original_filename=uploaded_file.name,
            blob_name=blob_name,
            file_size=uploaded_file.size,
            mime_type=form.cleaned_data['mime_type']
        )
        
        return redirect('tasks:detail', pk=self.task.id)

class AttachmentDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        attachment = get_object_or_404(Attachment, pk=pk)
        if attachment.task.owner != request.user:
            raise PermissionDenied("Access denied")
        
        download_url = attachment.get_download_url()
        return redirect(download_url)

class AttachmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Attachment
    template_name = 'attachments/confirm_delete.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(task__owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('tasks:detail', kwargs={'pk': self.object.task.id})
```

**File**: `attachments/forms.py`

```python
from django import forms
from .validators import validate_file_size, validate_mime_type

class AttachmentUploadForm(forms.Form):
    file = forms.FileField()
    
    def clean_file(self):
        file = self.cleaned_data['file']
        validate_file_size(file)
        mime_type = validate_mime_type(file)
        self.cleaned_data['mime_type'] = mime_type
        return file
```

---

## Step 10: Configure URLs

**File**: `attachments/urls.py`

```python
from django.urls import path
from . import views

app_name = 'attachments'

urlpatterns = [
    path('tasks/<int:task_id>/attachments/upload/', views.AttachmentUploadView.as_view(), name='upload'),
    path('attachments/<int:pk>/download/', views.AttachmentDownloadView.as_view(), name='download'),
    path('attachments/<int:pk>/delete/', views.AttachmentDeleteView.as_view(), name='delete'),
]
```

**File**: `taskmanager/urls.py`

```python
urlpatterns = [
    # ... other patterns ...
    path('', include('attachments.urls')),
]
```

---

## Step 11: Test Workflows

### Upload a File

```powershell
python manage.py shell
```

```python
from tasks.models import Task
from attachments.models import Attachment
from attachments.storage import AzureBlobStorage
from django.core.files.uploadedfile import SimpleUploadedFile

# Get task
task = Task.objects.first()

# Create fake PDF
pdf_content = b'%PDF-1.4\n%fake pdf content'
uploaded_file = SimpleUploadedFile('test.pdf', pdf_content, content_type='application/pdf')

# Upload
storage = AzureBlobStorage()
blob_name = storage.generate_blob_name(task.id, 'test.pdf')
storage._save(blob_name, uploaded_file)

# Create record
attachment = Attachment.objects.create(
    task=task,
    original_filename='test.pdf',
    blob_name=blob_name,
    file_size=len(pdf_content),
    mime_type='application/pdf'
)

print(attachment)  # test.pdf (24 bytes)
```

### Download a File

```python
download_url = attachment.get_download_url()
print(download_url)  # Signed URL with SAS token
```

### Delete a File

```python
attachment.delete()  # Deletes blob + record
```

---

## Step 12: Run Tests

```powershell
pytest tests/attachments/ -v
```

---

## Troubleshooting

### Azure Connection Error

**Error**: `ValueError: Connection string is invalid`

**Fix**: Verify environment variables in `.env` file

### Container Not Found

**Error**: `ResourceNotFoundError: Container not found`

**Fix**: Create container via Feature 004 Terraform or Azure portal

### MIME Type Detection Fails

**Error**: `ImportError: failed to find libmagic`

**Fix Windows**: Install `python-magic-bin`  
**Fix Linux**: `sudo apt-get install libmagic1`

---

## References

- [Azure Blob Storage SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme)
- [Django File Uploads](https://docs.djangoproject.com/en/5.0/topics/http/file-uploads/)
- [python-magic](https://github.com/ahupp/python-magic)
