# Model Contracts - Task File Attachments

**Date**: 2026-01-19  
**Feature**: 003-task-attachments  
**Version**: 1.0.0

---

## Attachment Model

**Class**: `attachments.models.Attachment`  
**Extends**: `django.db.models.Model`

**Purpose**: Represents a file attached to a task, stored in Azure Blob Storage.

### Fields

| Field | Type | Constraints | Default |
|-------|------|------------|---------|
| `id` | BigAutoField | PRIMARY KEY | auto |
| `task` | ForeignKey(Task) | CASCADE, indexed | - |
| `original_filename` | CharField(255) | NOT NULL | - |
| `blob_name` | CharField(500) | UNIQUE, indexed | - |
| `file_size` | PositiveIntegerField | CHECK <= 10MB | - |
| `mime_type` | CharField(100) | NOT NULL | - |
| `uploaded_at` | DateTimeField | auto_now_add, indexed | now() |

### Methods

#### `save(self, *args, **kwargs)`

**Pre-conditions**:
- `task` exists and is valid
- If new attachment: `task.attachments.count() < 5`
- `file_size <= 10485760` (10MB)

**Post-conditions**:
- Attachment record saved to database
- If constraint violated, raises `ValidationError`

**Side Effects**:
- Writes to database
- Sends `post_save` signal

**Raises**:
- `ValidationError`: If task already has 5 attachments

**Example**:
```python
attachment = Attachment(
    task=task,
    original_filename='report.pdf',
    blob_name='42/20260119103045_a3f7b2c1_report.pdf',
    file_size=2048576,
    mime_type='application/pdf'
)
attachment.save()  # OK if < 5 attachments

# 6th attachment
attachment6 = Attachment(task=task, ...)
attachment6.save()  # Raises ValidationError: "Maximum 5 attachments per task"
```

---

#### `delete(self, *args, **kwargs)`

**Pre-conditions**:
- Attachment record exists in database

**Post-conditions**:
- Blob deleted from Azure Blob Storage
- Attachment record deleted from database
- If blob deletion fails, record still deleted (logged)

**Side Effects**:
- Deletes blob from Azure Storage
- Deletes database record
- Sends `post_delete` signal

**Error Handling**:
- If blob already deleted: No error raised
- If storage service unavailable: Log error, continue with record deletion

**Example**:
```python
attachment.delete()  # Deletes blob + record

# If blob already gone
attachment.delete()  # Logs error but completes successfully
```

---

#### `get_download_url(self)`

**Pre-conditions**:
- Attachment record exists
- Blob exists in Azure Storage

**Post-conditions**:
- Returns signed URL string with 1-hour expiration

**Returns**: `str` - Signed Azure Blob URL

**Example**:
```python
url = attachment.get_download_url()
# Returns: "https://account.blob.core.windows.net/container/blob?sas_token&expiry=..."
```

---

#### `__str__(self)`

**Returns**: `"{original_filename} ({file_size} bytes)"`  
**Example**: `"proposal.pdf (2048576 bytes)"`

---

### Validation

**Validators**:
- `validate_file_size(file)`: Max 10MB, not empty
- `validate_mime_type(file)`: Content-based type checking
- `validate_file_extension(filename)`: Extension whitelist

**Validation Errors**:
```python
from attachments.validators import validate_file_size, validate_mime_type
from django.core.exceptions import ValidationError

# File too large
large_file = Mock(size=11 * 1024 * 1024)  # 11MB
validate_file_size(large_file)  # Raises ValidationError: "File size exceeds 10MB limit"

# Empty file
empty_file = Mock(size=0)
validate_file_size(empty_file)  # Raises ValidationError: "Cannot upload empty file"

# Invalid MIME type
exe_file = Mock(read=lambda n: b'MZ...')  # Windows executable header
validate_mime_type(exe_file)  # Raises ValidationError: "File type 'application/x-msdownload' not allowed"

# Valid PDF
pdf_file = Mock(read=lambda n: b'%PDF-1.4...')
mime = validate_mime_type(pdf_file)  # Returns 'application/pdf'
```

---

### Invariants

1. **Attachment Limit**: Task cannot have more than 5 attachments
2. **Blob Uniqueness**: `blob_name` is globally unique across all attachments
3. **File Size Limit**: `file_size` cannot exceed 10MB (database constraint)
4. **Cascade Deletion**: When task deleted, all attachments deleted (blob + record)
5. **Ownership Transitivity**: Attachment belongs to task, task belongs to user

---

### Meta Options

```python
class Meta:
    db_table = 'attachments_attachment'
    ordering = ['-uploaded_at']  # Newest first
    indexes = [
        Index(fields=['task', '-uploaded_at']),  # Task detail page optimization
    ]
    constraints = [
        CheckConstraint(
            check=Q(file_size__lte=10485760),  # 10MB limit
            name='file_size_limit'
        ),
    ]
```

---

### Related Names

**From Task model**:
```python
task.attachments.all()  # All attachments for task (ordered by -uploaded_at)
task.attachments.count()  # Number of attachments (max 5)
task.attachments.filter(mime_type='application/pdf')  # Filter by type
```

---

## Validator Functions

### `validate_file_size(file)`

**Pre-conditions**: `file` has `.size` attribute (Django UploadedFile)

**Post-conditions**: Raises `ValidationError` if invalid, otherwise returns `None`

**Validation Rules**:
- File size <= 10MB (10485760 bytes)
- File size > 0 bytes (not empty)

**Raises**: `ValidationError` with codes `file_too_large` or `empty_file`

---

### `validate_mime_type(file)`

**Pre-conditions**: `file` has `.read()` and `.seek()` methods

**Post-conditions**: Returns detected MIME type string if valid

**Validation Rules**:
- MIME type in allowed list:
  - `application/pdf`
  - `application/msword`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `application/vnd.ms-excel`
  - `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `text/plain`
  - `image/jpeg`
  - `image/png`

**Returns**: `str` - Detected MIME type

**Raises**: `ValidationError` with code `invalid_mime_type`

**Implementation Detail**: Uses python-magic (libmagic) for content-based detection

---

### `validate_file_extension(filename)`

**Pre-conditions**: `filename` is a string

**Post-conditions**: Raises `ValidationError` if invalid, otherwise returns `None`

**Validation Rules**:
- Extension in allowed list: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.txt`, `.jpg`, `.png`
- Case-insensitive comparison

**Raises**: `ValidationError` with code `invalid_extension`

---

## Signals

### `post_delete` signal on Task

**Receiver**: `attachments.signals.delete_task_attachments`

**Pre-conditions**: Task is being deleted

**Post-conditions**: All blobs with prefix `task_id/` deleted from Azure Storage

**Side Effects**:
- Lists all blobs in container with prefix `task_id/`
- Deletes each blob individually
- Logs success/failure for each blob
- Django ORM cascade handles Attachment records

**Error Handling**: Continues deleting remaining blobs even if one fails

---

## References

- [Django Model API](https://docs.djangoproject.com/en/5.0/ref/models/instances/)
- [Django Validators](https://docs.djangoproject.com/en/5.0/ref/validators/)
- [Django Signals](https://docs.djangoproject.com/en/5.0/topics/signals/)
