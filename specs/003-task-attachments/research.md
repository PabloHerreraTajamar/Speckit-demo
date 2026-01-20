# Phase 0: Research - Task File Attachments

**Date**: 2026-01-19  
**Feature**: 003-task-attachments  
**Branch**: `003-task-attachments`

## Overview

This document contains technology decisions and best practices research for implementing file attachment functionality using Azure Blob Storage. All NEEDS CLARIFICATION markers have been resolved.

---

## Decision 1: Azure Blob Storage SDK Integration

**Question**: How to integrate azure-storage-blob SDK with Django file handling?

**Decision**: Use `azure-storage-blob` 12.19+ with custom Django storage backend

**Rationale**:
- azure-storage-blob is the official Microsoft SDK with full feature support
- Custom storage backend allows seamless integration with Django's file handling
- Enables use of Django's FileField while storing in Azure Blob Storage
- Provides connection pooling and automatic retry logic

**Implementation Pattern**:
```python
from azure.storage.blob import BlobServiceClient, generate_blob_sas
from django.core.files.storage import Storage

class AzureBlobStorage(Storage):
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self.client = BlobServiceClient.from_connection_string(self.connection_string)
    
    def _save(self, name, content):
        blob_client = self.client.get_blob_client(container=self.container_name, blob=name)
        blob_client.upload_blob(content, overwrite=True)
        return name
    
    def url(self, name):
        # Generate signed URL with 1-hour expiration
        return generate_signed_url(name, expires_in=3600)
```

**Alternatives Considered**:
- django-storages: Adds unnecessary abstraction layer, Feature 004 already provisions storage
- Direct REST API calls: Low-level, requires manual retry logic and connection management

---

## Decision 2: MIME Type Detection

**Question**: Best practices for MIME type detection (python-magic vs filetype)?

**Decision**: Use `python-magic` 0.4+ for MIME type detection

**Rationale**:
- python-magic uses libmagic (same as Unix `file` command), highly accurate
- Detects MIME type by inspecting file content, not just extension
- Prevents extension spoofing attacks (e.g., malware.exe renamed to document.pdf)
- Industry standard for content-based file type detection

**Implementation Pattern**:
```python
import magic

def validate_file_type(uploaded_file):
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
    
    # Read first 2048 bytes for magic number detection
    uploaded_file.seek(0)
    file_content = uploaded_file.read(2048)
    uploaded_file.seek(0)
    
    mime = magic.from_buffer(file_content, mime=True)
    
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"File type {mime} not allowed")
```

**Alternatives Considered**:
- filetype: Less accurate, smaller MIME type database
- Extension-only validation: Easily bypassed by renaming files

**Dependencies**:
- Linux: libmagic (system package)
- Windows: python-magic-bin (includes libmagic DLL)

---

## Decision 3: Blob Naming Strategy

**Question**: Blob naming strategy to ensure uniqueness and prevent collisions?

**Decision**: Use pattern `{task_id}/{timestamp}_{uuid4}_{sanitized_filename}`

**Rationale**:
- Task ID prefix enables efficient deletion when task is deleted (list blobs by prefix)
- Timestamp provides chronological ordering for debugging
- UUID4 ensures global uniqueness even with concurrent uploads
- Original filename preserved for user-friendly downloads
- Sanitization prevents path traversal attacks

**Implementation Pattern**:
```python
import uuid
from datetime import datetime
from django.utils.text import slugify
import os

def generate_blob_name(task_id, original_filename):
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    
    # Sanitize filename: remove special chars, keep extension
    name, ext = os.path.splitext(original_filename)
    safe_name = slugify(name)[:50]  # Limit length
    safe_filename = f"{safe_name}{ext.lower()}"
    
    return f"{task_id}/{timestamp}_{unique_id}_{safe_filename}"

# Example: "42/20260119103045_a3f7b2c1_project_proposal.pdf"
```

**Alternatives Considered**:
- UUID-only names: Loses user-friendly filename
- Original filename only: Collisions possible, no uniqueness guarantee
- Flat structure (no task_id prefix): Requires full container scan for task deletion

---

## Decision 4: Secure Download URLs

**Question**: Signed URL generation for secure downloads without authentication headers?

**Decision**: Use Azure Blob SAS (Shared Access Signature) tokens with 1-hour expiration

**Rationale**:
- SAS tokens provide time-limited access without exposing storage account keys
- No authentication headers required in download request (browser-friendly)
- Granular permissions (read-only for downloads)
- Automatic expiration prevents long-lived access
- Supported natively by azure-storage-blob SDK

**Implementation Pattern**:
```python
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

def generate_download_url(blob_name):
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
        container_name=settings.AZURE_STORAGE_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=settings.AZURE_STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    
    blob_url = f"https://{account_name}.blob.core.windows.net/{container}/{blob_name}"
    return f"{blob_url}?{sas_token}"
```

**Alternatives Considered**:
- Azure AD authentication: Requires user to authenticate with Azure, complex for web downloads
- Proxy downloads through Django: Unnecessary bandwidth usage, slower performance
- Public blob access: Security risk, no expiration control

---

## Decision 5: Cascade Deletion Strategy

**Question**: How to handle cascade deletion when task is deleted (signals vs override)?

**Decision**: Use Django `post_delete` signal on Task model to delete attachments

**Rationale**:
- Signals keep deletion logic decoupled from Task model (separation of concerns)
- Automatically triggered by Django ORM delete operations
- Works with both single delete and queryset bulk delete
- Allows batch deletion of blobs using prefix filter (efficient)

**Implementation Pattern**:
```python
from django.db.models.signals import post_delete
from django.dispatch import receiver
from tasks.models import Task
from .storage import AzureBlobStorage

@receiver(post_delete, sender=Task)
def delete_task_attachments(sender, instance, **kwargs):
    storage = AzureBlobStorage()
    
    # Delete all blobs with prefix "task_id/"
    container_client = storage.client.get_container_client(storage.container_name)
    blob_list = container_client.list_blobs(name_starts_with=f"{instance.id}/")
    
    for blob in blob_list:
        container_client.delete_blob(blob.name)
    
    # Django ORM cascade handles Attachment records automatically
```

**Alternatives Considered**:
- Override Task.delete(): Tightly couples Task to attachments feature
- ON DELETE CASCADE in database: Only deletes records, not blob files
- Manual deletion in views: Error-prone, can be bypassed

---

## Decision 6: File Upload Streaming

**Question**: File streaming approach for large files (chunked upload)?

**Decision**: Use Django's default chunked upload handling (2.5MB chunks) with `upload_blob` streaming

**Rationale**:
- Django automatically chunks uploads larger than FILE_UPLOAD_MAX_MEMORY_SIZE (2.5MB default)
- azure-storage-blob SDK handles streaming efficiently with `upload_blob(data)`
- Prevents memory exhaustion on large file uploads
- Works seamlessly with Django's TemporaryUploadedFile

**Implementation Pattern**:
```python
# Django automatically chunks to TemporaryUploadedFile if > 2.5MB
def upload_attachment(request, task_id):
    uploaded_file = request.FILES['file']
    
    # Django provides file-like object (InMemoryUploadedFile or TemporaryUploadedFile)
    blob_name = generate_blob_name(task_id, uploaded_file.name)
    blob_client = storage.client.get_blob_client(container=container, blob=blob_name)
    
    # upload_blob accepts file-like objects and streams automatically
    blob_client.upload_blob(uploaded_file, overwrite=False)
```

**Configuration**:
```python
# settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB (Django default)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB (matches attachment limit)
```

**Alternatives Considered**:
- Manual chunking: Reinvents Django's built-in functionality
- Load entire file to memory: OOM risk on large files

---

## Decision 7: Azure Blob Storage Testing

**Question**: How to mock Azure Blob Storage in tests (moto, azure-storage-blob test utilities)?

**Decision**: Use in-memory fake storage for unit tests, Azurite emulator for integration tests

**Rationale**:
- In-memory fake is fast, no external dependencies for unit tests
- Azurite is official Microsoft emulator, provides full Azure Blob Storage API compatibility
- Separation allows fast unit tests, realistic integration tests
- No mocking library overhead (moto doesn't support Azure well)

**Unit Test Pattern** (in-memory):
```python
# tests/fakes.py
class FakeBlobStorage:
    def __init__(self):
        self.blobs = {}
    
    def upload_blob(self, name, content):
        self.blobs[name] = content.read()
    
    def download_blob(self, name):
        return self.blobs.get(name)

# tests/test_storage.py
def test_upload_file(monkeypatch):
    fake_storage = FakeBlobStorage()
    monkeypatch.setattr('attachments.storage.storage_client', fake_storage)
    # ... test logic
```

**Integration Test Pattern** (Azurite):
```bash
# docker-compose.test.yml
services:
  azurite:
    image: mcr.microsoft.com/azure-storage/azurite
    ports:
      - "10000:10000"

# pytest uses connection string pointing to localhost:10000
```

**Alternatives Considered**:
- moto: Doesn't support Azure services (AWS-only)
- Always use real Azure: Slow tests, requires credentials, costs money
- unittest.mock: Brittle, doesn't catch SDK API changes

---

## Decision 8: Storage Service Error Handling

**Question**: Error handling patterns for storage service failures?

**Decision**: Use try-except with Azure SDK exceptions, return user-friendly messages

**Rationale**:
- Azure SDK raises specific exceptions for different failure modes
- Graceful degradation improves user experience
- Logging errors enables debugging without exposing internals
- Retry logic for transient failures (built into SDK)

**Implementation Pattern**:
```python
from azure.core.exceptions import AzureError, ResourceNotFoundError, ServiceRequestError
import logging

logger = logging.getLogger(__name__)

def upload_file_to_blob(blob_name, file_content):
    try:
        blob_client.upload_blob(file_content, overwrite=False)
    except ResourceNotFoundError:
        logger.error(f"Container not found: {container_name}")
        raise ValidationError("Storage service configuration error. Please contact support.")
    except ServiceRequestError as e:
        logger.error(f"Storage service unavailable: {e}")
        raise ValidationError("Storage service unavailable. Please try again later.")
    except AzureError as e:
        logger.error(f"Azure storage error: {e}")
        raise ValidationError("File upload failed. Please try again.")
```

**Error Scenarios**:
- Network timeout: Retry automatically (SDK handles)
- Container not found: Configuration error, log and notify admin
- Blob already exists: Should not happen with UUID naming
- Service unavailable: Transient, show retry message

**Alternatives Considered**:
- Expose raw Azure errors: Security risk, confusing for users
- Generic "error occurred" message: Not actionable for users
- No error handling: Poor user experience, crashes application

---

## Technology Summary

**Final Stack**:
1. **azure-storage-blob 12.19+**: Official Azure SDK for blob operations
2. **python-magic 0.4+**: MIME type detection via libmagic
3. **Django FileField**: Integration with Django forms and models
4. **SAS tokens**: Secure time-limited download URLs
5. **Django signals**: Decoupled cascade deletion
6. **Azurite**: Local Azure emulator for integration tests
7. **Chunked uploads**: Django default (2.5MB chunks) + SDK streaming

**Environment Variables Required**:
- `AZURE_STORAGE_CONNECTION_STRING`: Connection string from Feature 004
- `AZURE_STORAGE_CONTAINER_NAME`: Container name (e.g., taskmanager-attachments-dev)
- `AZURE_STORAGE_ACCOUNT_NAME`: Storage account name
- `AZURE_STORAGE_ACCOUNT_KEY`: Storage account key (for SAS generation)

**System Dependencies**:
- Linux: `libmagic1` (apt-get install libmagic1)
- Windows: Included in python-magic-bin package

---

## Open Questions

✅ **ALL RESOLVED**

---

## References

- [Azure Blob Storage SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme)
- [python-magic Documentation](https://github.com/ahupp/python-magic)
- [Django File Uploads](https://docs.djangoproject.com/en/5.0/topics/http/file-uploads/)
- [SAS Token Documentation](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
- [Azurite Emulator](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
