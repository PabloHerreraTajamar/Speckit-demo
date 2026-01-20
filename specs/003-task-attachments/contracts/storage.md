# Storage Backend Contracts - Task File Attachments

**Date**: 2026-01-19  
**Feature**: 003-task-attachments  
**Version**: 1.0.0

---

## AzureBlobStorage

**Class**: `attachments.storage.AzureBlobStorage`  
**Extends**: `django.core.files.storage.Storage`

**Purpose**: Custom Django storage backend for Azure Blob Storage operations.

### Initialization

#### `__init__(self)`

**Pre-conditions**:
- Environment variables set:
  - `AZURE_STORAGE_CONNECTION_STRING`
  - `AZURE_STORAGE_CONTAINER_NAME`
  - `AZURE_STORAGE_ACCOUNT_NAME`
  - `AZURE_STORAGE_ACCOUNT_KEY`

**Post-conditions**:
- `BlobServiceClient` initialized
- Connection to Azure Storage established

**Raises**: `ValueError` if environment variables missing

---

### Methods

#### `generate_blob_name(task_id, original_filename)`

**Pre-conditions**:
- `task_id` is integer
- `original_filename` is non-empty string

**Post-conditions**:
- Returns unique blob name string

**Returns**: `str` - Format: `{task_id}/{timestamp}_{uuid}_{sanitized_filename}`

**Example**:
```python
storage = AzureBlobStorage()
blob_name = storage.generate_blob_name(42, "My Report.pdf")
# Returns: "42/20260119103045_a3f7b2c1_my-report.pdf"
```

**Sanitization Rules**:
- Filename converted to lowercase
- Spaces and special chars replaced with hyphens
- Filename truncated to 50 characters (excluding extension)
- Extension preserved

---

#### `_save(name, content)`

**Pre-conditions**:
- `name` is blob name string (from `generate_blob_name`)
- `content` is file-like object (Django UploadedFile)

**Post-conditions**:
- File uploaded to Azure Blob Storage
- Blob created in container
- Returns blob name

**Returns**: `str` - Blob name (same as input `name`)

**Raises**:
- `ResourceNotFoundError`: Container doesn't exist
- `ServiceRequestError`: Azure service unavailable
- `AzureError`: Generic Azure SDK error

**Example**:
```python
blob_name = storage._save('42/20260119_uuid_file.pdf', uploaded_file)
# Uploads file, returns '42/20260119_uuid_file.pdf'
```

**Implementation Detail**: Uses `upload_blob(content, overwrite=False)` to prevent accidental overwrites

---

#### `_open(name, mode='rb')`

**Pre-conditions**:
- `name` is existing blob name
- `mode` is 'rb' (read binary)

**Post-conditions**:
- Returns blob download stream

**Returns**: `StorageStreamDownloader` - File-like object for reading blob

**Raises**:
- `ResourceNotFoundError`: Blob doesn't exist
- `AzureError`: Storage service error

**Usage**: Primarily for internal Django operations, not direct downloads

---

#### `delete(name)`

**Pre-conditions**:
- `name` is blob name string

**Post-conditions**:
- Blob deleted from Azure Storage
- No error if blob doesn't exist (idempotent)

**Raises**: `AzureError` if service error occurs

**Example**:
```python
storage.delete('42/20260119_uuid_file.pdf')  # Deletes blob
storage.delete('42/20260119_uuid_file.pdf')  # No error (already deleted)
```

---

#### `exists(name)`

**Pre-conditions**:
- `name` is blob name string

**Post-conditions**:
- Returns True if blob exists, False otherwise

**Returns**: `bool`

**Example**:
```python
exists = storage.exists('42/20260119_uuid_file.pdf')  # True or False
```

---

#### `url(name)`

**Pre-conditions**:
- `name` is blob name string
- Blob should exist (but not enforced)

**Post-conditions**:
- Returns signed URL with 1-hour expiration

**Returns**: `str` - Azure Blob URL with SAS token

**URL Format**:
```
https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}
```

**SAS Token Permissions**: Read-only (`BlobSasPermissions(read=True)`)

**Expiration**: 1 hour from generation

**Example**:
```python
download_url = storage.url('42/20260119_uuid_file.pdf')
# Returns: "https://account.blob.core.windows.net/container/42/20260119_uuid_file.pdf?sv=2021-06-08&st=2026-01-19T10:30:00Z&se=2026-01-19T11:30:00Z&sr=b&sp=r&sig=..."
```

**Security**: URL grants temporary read access without requiring authentication

---

### Error Handling Contracts

#### Storage Service Unavailable

**Scenario**: Azure Blob Storage is down or unreachable

**Exception**: `ServiceRequestError`

**User Message**: "Storage service unavailable, please try again later"

**Logging**: Error logged with full exception details

**Recovery**: User can retry operation after service restoration

---

#### Container Not Found

**Scenario**: Container doesn't exist (misconfiguration)

**Exception**: `ResourceNotFoundError`

**User Message**: "Storage service configuration error. Please contact support."

**Logging**: Critical error logged (infrastructure issue)

**Recovery**: Admin must verify Feature 004 provisioning

---

#### Blob Already Exists

**Scenario**: UUID collision (extremely rare, ~1 in 2^128)

**Exception**: `ResourceExistsError` (if `overwrite=False`)

**User Message**: "Upload conflict detected, please retry"

**Logging**: Warning logged with blob name

**Recovery**: User retries, new UUID generated

---

#### Network Timeout

**Scenario**: Network interruption during upload/download

**Exception**: `AzureError` (connection timeout)

**User Message**: "Network error occurred, please try again"

**Logging**: Error logged with operation type

**Recovery**: Azure SDK auto-retries transient failures (3 attempts), then fails

---

### Performance Characteristics

- **Upload**: O(n) where n = file size, streaming prevents memory issues
- **Download URL generation**: O(1), no network call (SAS generated locally)
- **Delete**: O(1), single blob operation
- **Exists check**: O(1), HEAD request to blob

---

### Testing Contracts

#### Unit Tests (Fake Storage)

**Scenario**: Fast in-memory tests without Azure dependency

**Mock Strategy**: Replace `BlobServiceClient` with fake in-memory dict

**Example**:
```python
class FakeBlobStorage:
    def __init__(self):
        self.blobs = {}
    
    def upload_blob(self, content):
        self.blobs[name] = content.read()
```

---

#### Integration Tests (Azurite Emulator)

**Scenario**: Realistic Azure Blob Storage API testing

**Setup**: Docker container running Azurite emulator

**Connection String**: `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;...`

**Container**: Auto-created in test setup

**Cleanup**: All blobs deleted after each test

---

## References

- [Azure Blob Storage SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme)
- [Django Custom Storage](https://docs.djangoproject.com/en/5.0/howto/custom-file-storage/)
- [SAS Token Generation](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
