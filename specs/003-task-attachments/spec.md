# Feature Specification: Task File Attachments

**Feature Branch**: `003-task-attachments`  
**Created**: 2026-01-19  
**Status**: Draft  
**Input**: User description: "Sistema de adjuntos de archivos para tareas usando Azure Blob Storage. Los usuarios deben poder: Adjuntar archivos a una tarea (máximo 5 archivos por tarea); Ver la lista de archivos adjuntos en una tarea; Descargar archivos adjuntos; Eliminar archivos adjuntos de sus tareas. Restricciones: Tamaño máximo por archivo 10 MB; Tipos de archivo permitidos: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG; Los archivos se almacenan en Azure Blob Storage; Cada archivo tiene un nombre único generado automáticamente; Solo el propietario de la tarea puede gestionar sus adjuntos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload File to Task (Priority: P1)

Users can attach files to their tasks to keep related documents organized with each task.

**Why this priority**: File upload is the foundation of the attachment system. Without it, no other attachment functionality is possible. This is the MVP that proves file storage integration works.

**Independent Test**: Can be fully tested by creating a task, uploading a valid file (PDF, 2MB), and verifying it appears in the task's attachment list and is stored in Azure Blob Storage. Delivers immediate value by allowing document organization.

**Acceptance Scenarios**:

1. **Given** authenticated user with a task, **When** user selects a valid file (PDF, 2MB) and uploads it, **Then** file is stored in Azure Blob Storage, attachment record is created with unique filename, and file appears in task's attachment list
2. **Given** user tries to upload file, **When** file exceeds 10MB, **Then** upload fails with error "File size exceeds 10MB limit"
3. **Given** user tries to upload file, **When** file type is not allowed (e.g., .exe), **Then** upload fails with error "File type not allowed. Allowed: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG"
4. **Given** task already has 5 attachments, **When** user tries to upload another file, **Then** upload fails with error "Maximum 5 attachments per task"
5. **Given** user tries to upload file to another user's task, **When** user attempts upload, **Then** upload fails with error "You can only attach files to your own tasks"

---

### User Story 2 - View and Download Attachments (Priority: P2)

Users can view the list of files attached to a task and download them when needed.

**Why this priority**: Viewing and downloading attachments completes the basic file management cycle. Users need to retrieve uploaded files to use them.

**Independent Test**: Can be fully tested by uploading files to a task, viewing the attachment list showing filenames and sizes, then downloading a file and verifying it matches the original. Delivers file retrieval capability.

**Acceptance Scenarios**:

1. **Given** task with 3 attachments, **When** user views task details, **Then** all 3 attachments are listed with original filename, file size, upload date, and download link
2. **Given** attachment exists on task, **When** user clicks download link, **Then** file is downloaded from Azure Blob Storage with correct filename and content
3. **Given** user tries to download attachment from another user's task, **When** download is attempted, **Then** download fails with error "Access denied"
4. **Given** task has no attachments, **When** user views task details, **Then** message "No attachments" is displayed
5. **Given** attachment was deleted from storage but record exists, **When** user tries to download, **Then** error "File not found" is shown and record is marked for cleanup

---

### User Story 3 - Delete Attachments (Priority: P3)

Users can remove attachments they no longer need from their tasks.

**Why this priority**: Deletion is important for managing storage and removing outdated files, but tasks can function without deletion capability initially.

**Independent Test**: Can be fully tested by uploading a file, deleting it, and verifying it's removed from both the attachment list and Azure Blob Storage. Delivers storage management capability.

**Acceptance Scenarios**:

1. **Given** task with attachment, **When** user clicks delete on attachment, **Then** confirmation dialog appears
2. **Given** user confirms deletion, **When** confirmation is submitted, **Then** file is deleted from Azure Blob Storage, attachment record is removed, and attachment no longer appears in list
3. **Given** user tries to delete attachment from another user's task, **When** deletion is attempted, **Then** deletion fails with error "You can only delete attachments from your own tasks"
4. **Given** file already deleted from storage, **When** user deletes attachment record, **Then** record is removed without error
5. **Given** multiple attachments on task, **When** user deletes one, **Then** only that attachment is removed, others remain intact

---

### Edge Cases

- What happens when two users try to upload files with the same name to different tasks? (System generates unique blob names using task ID + timestamp + UUID)
- How does system handle network interruption during file upload? (Upload fails, user sees error, can retry)
- What happens when Azure Blob Storage is unavailable? (Upload/download fails with "Storage service unavailable, please try again")
- How does system handle filename with special characters or very long names? (Sanitize filename, truncate if necessary, preserve extension)
- What happens when user deletes a task with attachments? (All attachments are deleted from storage as part of task deletion cascade)
- How does system prevent direct URL access to blobs? (Use signed URLs with expiration or Azure AD authentication)
- What happens when file upload is interrupted at 50%? (Upload fails, no partial file saved, user must retry)
- How does system handle file type detection beyond extension? (Validate MIME type in addition to file extension)
- What happens when user tries to upload empty file (0 bytes)? (Upload fails with error "Cannot upload empty file")
- How does system handle concurrent uploads to same task? (Each upload processed independently, up to 5 total limit)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to upload files to their own tasks
- **FR-002**: System MUST validate file size does not exceed 10MB before upload
- **FR-003**: System MUST validate file type is in allowed list: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
- **FR-004**: System MUST validate file type using both extension and MIME type
- **FR-005**: System MUST enforce maximum 5 attachments per task
- **FR-006**: System MUST store files in Azure Blob Storage with unique blob names
- **FR-007**: System MUST generate unique blob names using pattern: taskId_timestamp_uuid_originalFilename
- **FR-008**: System MUST create attachment record linking blob to task with metadata (original filename, file size, upload date, MIME type)
- **FR-009**: System MUST prevent users from uploading files to tasks they don't own
- **FR-010**: System MUST display attachment list on task details page showing filename, size, upload date, and download link
- **FR-011**: System MUST allow users to download their own task attachments
- **FR-012**: System MUST prevent users from downloading attachments from tasks they don't own
- **FR-013**: System MUST generate secure download URLs (signed URLs or authenticated access)
- **FR-014**: System MUST allow users to delete attachments from their own tasks
- **FR-015**: System MUST delete files from Azure Blob Storage when attachment record is deleted
- **FR-016**: System MUST delete all task attachments from storage when task is deleted
- **FR-017**: System MUST handle storage service errors gracefully with user-friendly messages
- **FR-018**: System MUST sanitize filenames to remove special characters that could cause issues
- **FR-019**: System MUST reject empty files (0 bytes)
- **FR-020**: System MUST provide clear error messages for validation failures (size, type, limit)

### Key Entities

- **Attachment**: Represents a file attached to a task with original filename, sanitized filename, blob storage path, file size in bytes, MIME type, upload timestamp, and reference to owning task. Each attachment belongs to exactly one task.
- **BlobReference**: Represents the storage location in Azure Blob Storage with container name, blob name (unique), and access URL. Links to Attachment entity.
- **Task**: Extended to have collection of attachments (0 to 5). Task deletion cascades to all attachments.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully upload valid files in under 30 seconds (for files under 5MB on typical connection)
- **SC-002**: System rejects 100% of invalid file types before upload
- **SC-003**: System enforces 10MB size limit on 100% of uploads
- **SC-004**: System prevents 100% of unauthorized access to attachments (users can only access their own task files)
- **SC-005**: File downloads complete successfully 99% of the time (excluding network issues)
- **SC-006**: Attachment deletion removes file from storage within 5 seconds
- **SC-007**: System maintains referential integrity between attachment records and blob storage 100% of time
- **SC-008**: Users can view attachment list immediately (under 1 second) when opening task details
- **SC-009**: System handles storage service errors without data corruption 100% of time
- **SC-010**: 90% of users successfully upload their first file on first attempt

## Assumptions

- Azure Blob Storage account is provisioned and connection string is available via environment variables
- All file operations use Azure Storage SDK for Python
- Blob container naming follows convention: taskmanager-attachments-{environment} (dev, staging, prod)
- Signed URLs expire after 1 hour for security
- File uploads use streaming to handle large files efficiently
- MIME type validation uses python-magic or similar library
- Task entity already exists from Feature 2 (CRUD de Tareas)
- User authentication is already implemented from Feature 1
- HTTPS is enforced at infrastructure level
- Concurrent upload limit per user is not enforced (relies on browser limitations)
- No virus scanning on uploaded files (out of scope for MVP)
- No file versioning (replacing file requires delete + upload)

## Out of Scope

- File preview/thumbnail generation
- Image optimization or resizing
- Virus/malware scanning
- File versioning or revision history
- Bulk upload (multiple files at once)
- Drag-and-drop upload interface
- Upload progress bar
- File sharing between users
- Public file URLs
- File expiration or auto-deletion
- Storage quota per user
- Attachment search or filtering
- File metadata editing (rename, change description)
- Attachment comments or annotations
- Archive/zip download of all task attachments
