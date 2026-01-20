# View Contracts - Task File Attachments

**Date**: 2026-01-19  
**Feature**: 003-task-attachments  
**Version**: 1.0.0

---

## AttachmentUploadView

**Endpoint**: `POST /tasks/<int:task_id>/attachments/upload/`  
**Class**: `attachments.views.AttachmentUploadView` (Django FormView)

**Pre-conditions**:
- User must be authenticated
- Task with `task_id` exists
- `task.owner == request.user`
- Valid CSRF token
- Form contains valid file upload

**Post-conditions**:
- File validated (size <= 10MB, allowed type, not empty)
- MIME type detected via python-magic
- Blob name generated with pattern `task_id/timestamp_uuid_filename`
- File uploaded to Azure Blob Storage
- Attachment record created in database
- Redirect to task detail page
- Success message displayed

**Form Data** (multipart/form-data):
- `file` (required): File upload field

**Validation**:
- File size max 10MB
- File type in allowed list (PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG)
- MIME type matches extension
- Task attachment count < 5
- File not empty (> 0 bytes)

**HTTP Status**:
- 302: Redirect to task detail (success)
- 400: Validation error (size, type, limit)
- 403: Forbidden (not task owner)
- 404: Task not found

**Error Messages**:
- "File size exceeds 10MB limit"
- "File type not allowed. Allowed: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG"
- "Maximum 5 attachments per task"
- "Cannot upload empty file"
- "You can only attach files to your own tasks"
- "Storage service unavailable, please try again"

---

## AttachmentDownloadView

**Endpoint**: `GET /attachments/<int:pk>/download/`  
**Class**: `attachments.views.AttachmentDownloadView` (Django View)

**Pre-conditions**:
- User must be authenticated
- Attachment with `pk` exists
- `attachment.task.owner == request.user`

**Post-conditions**:
- Redirect to signed Azure Blob URL (1-hour expiration)
- User's browser downloads file with original filename
- No file content proxied through Django

**HTTP Status**:
- 302: Redirect to signed blob URL (success)
- 403: Forbidden (not task owner)
- 404: Attachment not found

**Example Flow**:
1. User clicks "Download" button
2. Django view validates ownership
3. Generate signed URL via `attachment.get_download_url()`
4. Redirect to `https://{account}.blob.core.windows.net/{container}/{blob}?{sas_token}`
5. Browser downloads directly from Azure Storage

---

## AttachmentDeleteView

**Endpoint**: `GET /attachments/<int:pk>/delete/` (confirmation), `POST /attachments/<int:pk>/delete/` (confirm)  
**Class**: `attachments.views.AttachmentDeleteView` (Django DeleteView)

**Pre-conditions**:
- User must be authenticated
- Attachment with `pk` exists
- `attachment.task.owner == request.user`
- For POST: Valid CSRF token

**Post-conditions**:
- File deleted from Azure Blob Storage
- Attachment record deleted from database
- Redirect to task detail page
- Success message displayed

**HTTP Status**:
- 200: Confirmation form (GET)
- 302: Redirect to task detail (POST success)
- 403: Forbidden (not task owner)
- 404: Attachment not found

**Side Effects**:
- Blob deleted from Azure Storage (via `Attachment.delete()` override)
- If blob deletion fails, record still deleted (logged error)

---

## AttachmentListView (Task Detail Page Integration)

**Endpoint**: `GET /tasks/<int:pk>/`  
**Class**: `tasks.views.TaskDetailView` (extended with attachments)

**Pre-conditions**:
- User must be authenticated
- Task with `pk` exists
- `task.owner == request.user`

**Post-conditions**:
- Task details displayed
- Attachment list rendered (queryset: `task.attachments.all()`)
- Each attachment shows: original filename, file size, upload date, download link, delete button

**Context Data**:
- `task` (Task): Task object
- `attachments` (queryset): `task.attachments.all()` (ordered by `-uploaded_at`)
- `can_upload` (bool): `task.attachments.count() < 5`

**Template Rendering**:
```html
{% for attachment in task.attachments.all %}
  <li>
    <strong>{{ attachment.original_filename }}</strong>
    ({{ attachment.file_size|filesizeformat }})
    - Uploaded {{ attachment.uploaded_at|date:"Y-m-d H:i" }}
    <a href="{% url 'attachments:download' attachment.pk %}">Download</a>
    <a href="{% url 'attachments:delete' attachment.pk %}">Delete</a>
  </li>
{% empty %}
  <p>No attachments</p>
{% endfor %}

{% if can_upload %}
  <a href="{% url 'attachments:upload' task.pk %}">Upload File</a>
{% else %}
  <p>Maximum 5 attachments reached</p>
{% endif %}
```

---

## Authorization Invariant

**All views** must enforce ownership:
```python
def get_queryset(self):
    return super().get_queryset().filter(task__owner=self.request.user)
```

For upload view:
```python
def dispatch(self, request, *args, **kwargs):
    task = get_object_or_404(Task, pk=kwargs['task_id'])
    if task.owner != request.user:
        raise PermissionDenied("You can only attach files to your own tasks")
    return super().dispatch(request, *args, **kwargs)
```

---

## Error Handling Contract

**Storage Service Errors**:
- All Azure SDK exceptions caught and converted to user-friendly messages
- Errors logged for debugging
- User sees actionable error message

**Network Failures**:
- Upload interrupted: Transaction rolled back, no partial data saved
- Download interrupted: User can retry (signed URL still valid for 1 hour)

**Concurrent Operations**:
- Multiple users uploading to different tasks: No conflicts (UUID blob naming)
- Same user uploading multiple files: Each processed independently

---

## References

- [Django Class-Based Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/)
- [Django File Uploads](https://docs.djangoproject.com/en/5.0/topics/http/file-uploads/)
