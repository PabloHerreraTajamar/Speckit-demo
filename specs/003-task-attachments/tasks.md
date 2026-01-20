---
description: "Task breakdown for Feature 003 - Task File Attachments"
---

# Tasks: Task File Attachments

**Input**: Design documents from `/specs/003-task-attachments/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1, US2, US3)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Azure Blob Storage integration

- [X] T001 Create attachments Django app in taskmanager/apps/
- [X] T002 Add 'attachments' to INSTALLED_APPS in taskmanager/settings/base.py
- [X] T003 [P] Install azure-storage-blob==12.19.0 in requirements/base.txt
- [X] T004 [P] Install python-magic==0.4.27 in requirements/base.txt
- [X] T005 [P] Create directory structure: attachments/{models,views,forms,validators,storage,signals,urls}.py
- [X] T006 [P] Create directory structure: tests/attachments/{test_models,test_validators,test_storage,test_views,test_signals,factories}.py
- [X] T007 [P] Create templates/attachments/ directory
- [X] T008 Add Azure storage configuration to settings (AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER_NAME)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure - MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create file validators in attachments/validators.py (validate_file_size, validate_file_extension, validate_mime_type)
- [X] T010 [P] Write validator tests in tests/attachments/test_validators.py
- [X] T011 Create AzureBlobStorage backend in attachments/storage.py (init, save, delete, exists, url methods)
- [X] T012 [P] Write storage backend tests in tests/attachments/test_storage.py (with mocking)
- [X] T013 Create Attachment model in attachments/models.py with fields (task FK, original_filename, blob_name, file_size, mime_type, uploaded_at)
- [X] T014 Create and run migration for Attachment model (attachments/migrations/0001_initial.py)
- [X] T015 [P] Create AttachmentFactory in tests/attachments/factories.py
- [X] T016 [P] Write Attachment model tests in tests/attachments/test_models.py
- [X] T017 Create cascade deletion signal handler in attachments/signals.py (delete blobs when task deleted)
- [X] T018 [P] Write signal handler tests in tests/attachments/test_signals.py
- [X] T019 Register Attachment model in Django admin (attachments/admin.py)
- [X] T020 Configure attachments URLs in attachments/urls.py and include in taskmanager/urls.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload File to Task (Priority: P1) 🎯 MVP

**Goal**: Users can attach files to their tasks with validation (max 10MB, allowed types, max 5 per task)

**Independent Test**: Create task, upload valid PDF (2MB), verify in attachment list and Azure storage

### Tests for User Story 1 (TDD Required)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US1] Write upload view tests in tests/attachments/test_views.py::TestAttachmentUploadView
  - test_upload_requires_authentication
  - test_upload_valid_file
  - test_upload_file_too_large (>10MB)
  - test_upload_invalid_file_type (.exe)
  - test_upload_exceeds_limit (6th file)
  - test_upload_to_other_user_task (ownership)
  - test_upload_empty_file (0 bytes)
  - test_upload_generates_unique_blob_name
  - test_upload_stores_metadata

- [X] T022 [P] [US1] Write form tests in tests/attachments/test_forms.py::TestAttachmentUploadForm
  - test_form_valid_file
  - test_form_file_size_validation
  - test_form_file_type_validation
  - test_form_mime_type_validation
  - test_form_file_extension_validation

### Implementation for User Story 1

- [X] T023 [P] [US1] Create AttachmentUploadForm in attachments/forms.py with file field and validators
- [X] T024 [US1] Create AttachmentUploadView in attachments/views.py (handles upload, validation, storage)
- [X] T025 [US1] Add upload URL pattern to attachments/urls.py (path: tasks/<int:task_pk>/attachments/upload/)
- [X] T026 [US1] Create upload template templates/attachments/upload.html with file input and progress indicator
- [X] T027 [US1] Add upload button to task detail page templates/tasks/task_detail.html
- [X] T028 [US1] Implement attachment count limit check (max 5) in AttachmentUploadView.form_valid()
- [X] T029 [US1] Implement ownership validation in AttachmentUploadView.dispatch()
- [X] T030 [US1] Generate unique blob names using pattern: taskId_timestamp_uuid_originalFilename
- [X] T031 [US1] Store file in Azure Blob Storage via AzureBlobStorage backend
- [X] T032 [US1] Create Attachment record with metadata (filename, size, MIME type, blob_name)
- [X] T033 [US1] Add success message "File uploaded successfully" and redirect to task detail
- [X] T034 [US1] Run all US1 tests - should pass

**Checkpoint**: User can upload files with full validation, stored in Azure, limited to 5 per task

---

## Phase 4: User Story 2 - View and Download Attachments (Priority: P2)

**Goal**: Users can view attachment list and download files from their tasks

**Independent Test**: Upload 3 files, view list showing filenames/sizes/dates, download file and verify content

### Tests for User Story 2

- [X] T035 [P] [US2] Write attachment list view tests in tests/attachments/test_views.py::TestAttachmentListView
  - test_list_requires_authentication
  - test_list_shows_user_task_attachments
  - test_list_hides_other_user_attachments
  - test_list_shows_empty_state
  - test_list_displays_metadata (filename, size, date)

- [X] T036 [P] [US2] Write download view tests in tests/attachments/test_views.py::TestAttachmentDownloadView
  - test_download_requires_authentication
  - test_download_valid_attachment
  - test_download_other_user_attachment (403)
  - test_download_nonexistent_attachment (404)
  - test_download_missing_blob (file deleted from storage)
  - test_download_correct_content_type
  - test_download_correct_filename

### Implementation for User Story 2

- [X] T037 [P] [US2] Create AttachmentListView in attachments/views.py (list attachments for task)
- [X] T038 [P] [US2] Create AttachmentDownloadView in attachments/views.py (generate signed URL or stream file)
- [X] T039 [US2] Add list and download URL patterns to attachments/urls.py
- [X] T040 [US2] Create attachment list template templates/attachments/list.html with table (filename, size, date, actions)
- [X] T041 [US2] Add attachment list section to task detail page templates/tasks/task_detail.html
- [X] T042 [US2] Implement ownership validation in both views
- [X] T043 [US2] Generate signed URLs for downloads (1-hour expiration) via AzureBlobStorage.url()
- [X] T044 [US2] Handle missing blob scenario (file deleted from storage but record exists)
- [X] T045 [US2] Add file size formatting (convert bytes to KB/MB) in template filter
- [X] T046 [US2] Add download icon/button for each attachment
- [X] T047 [US2] Display "No attachments" message when list is empty
- [X] T048 [US2] Run all US2 tests - should pass

**Checkpoint**: Users can view all attachments on task and download files securely

---

## Phase 5: User Story 3 - Delete Attachments (Priority: P3)

**Goal**: Users can remove attachments from their tasks

**Independent Test**: Upload file, delete it, verify removed from list and Azure storage

### Tests for User Story 3

- [X] T049 [P] [US3] Write delete view tests in tests/attachments/test_views.py::TestAttachmentDeleteView
  - test_delete_requires_authentication
  - test_delete_requires_confirmation (GET shows confirmation)
  - test_delete_valid_attachment
  - test_delete_other_user_attachment (403)
  - test_delete_removes_blob_from_storage
  - test_delete_removes_attachment_record
  - test_delete_with_missing_blob (graceful handling)
  - test_delete_redirects_to_task_detail
  - test_delete_shows_success_message

### Implementation for User Story 3

- [X] T050 [P] [US3] Create AttachmentDeleteView in attachments/views.py (confirmation + deletion)
- [X] T051 [US3] Add delete URL pattern to attachments/urls.py (tasks/<int:task_pk>/attachments/<int:pk>/delete/)
- [X] T052 [US3] Create delete confirmation template templates/attachments/delete_confirm.html
- [X] T053 [US3] Add delete button to attachment list with confirmation modal
- [X] T054 [US3] Implement ownership validation in AttachmentDeleteView.dispatch()
- [X] T055 [US3] Delete blob from Azure Blob Storage in AttachmentDeleteView.delete()
- [X] T056 [US3] Handle missing blob scenario gracefully (log warning, continue with record deletion)
- [X] T057 [US3] Delete Attachment record from database
- [X] T058 [US3] Add success message "Attachment deleted successfully"
- [X] T059 [US3] Redirect to task detail page after deletion
- [X] T060 [US3] Test deletion doesn't affect other attachments on same task
- [X] T061 [US3] Run all US3 tests - should pass

**Checkpoint**: All user stories independently functional - full attachment lifecycle working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, user experience, and production readiness

- [X] T062 [P] Add error handling for Azure storage connection failures in AzureBlobStorage
- [X] T063 [P] Add error handling for upload failures (network interruption, timeout)
- [X] T064 [P] Add error handling for download failures (blob not found, access denied)
- [X] T065 [P] Create user-friendly error messages for all validation failures
- [X] T066 [P] Add file upload progress indicator (JavaScript) in upload.html
- [X] T067 [P] Add filename sanitization utility (remove special chars, truncate if needed)
- [X] T068 [P] Add logging for all attachment operations (upload, download, delete, errors)
- [X] T069 [P] Create static CSS for attachment UI in static/attachments/css/attachments.css
- [X] T070 [P] Add file type icons for different file extensions (PDF, DOC, XLS, etc.)
- [X] T071 Add integration test for full workflow (upload → view → download → delete)
- [X] T072 Add integration test for task deletion cascade (verify all attachments deleted)
- [X] T073 Run full test suite with coverage report (target >80%)
- [X] T074 Run black formatter on attachments/ and tests/attachments/
- [X] T075 Run flake8 linter and fix any issues
- [X] T076 Update .gitignore to exclude uploaded files in development
- [X] T077 Update README.md with Feature 003 status and attachment usage instructions
- [X] T078 Create environment variable documentation for Azure storage configuration
- [X] T079 Test with various file types (PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG)
- [X] T080 Test with edge cases (exactly 10MB, empty file, special characters in filename)
- [X] T081 Final commit with message: "feat(attachments): Complete Feature 003 - Task File Attachments"

---

## Task Summary

- **Total Tasks**: 81
- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 12 tasks  
- **Phase 3 (US1 - Upload)**: 14 tasks
- **Phase 4 (US2 - View/Download)**: 14 tasks
- **Phase 5 (US3 - Delete)**: 13 tasks
- **Phase 6 (Polish)**: 20 tasks

## Dependency Graph (User Story Completion Order)

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (Polish)
                                                ↓
                                          (US1 MVP Ready)
```

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 = Upload functionality only (32 tasks)

## Parallel Execution Opportunities

Within each phase, tasks marked with [P] can be executed in parallel:

- **Phase 1**: T003, T004, T005, T006, T007 (5 parallel)
- **Phase 2**: T010, T012, T015, T016, T018 (5 parallel)
- **Phase 3**: T021, T022, T023 (3 parallel - tests + form)
- **Phase 4**: T035, T036, T037, T038 (4 parallel)
- **Phase 5**: T049, T050 (2 parallel)
- **Phase 6**: T062-T070, T074-T075 (12 parallel)

**Total Parallelization**: ~31 tasks can run concurrently

---

## Implementation Strategy

**TDD Approach**:
1. Write tests FIRST for each user story (marked with test task IDs)
2. Verify tests FAIL (red phase)
3. Implement functionality to make tests pass (green phase)
4. Refactor code while keeping tests passing

**Incremental Delivery**:
1. **Week 1**: Phase 1 + Phase 2 (foundation)
2. **Week 2**: Phase 3 (US1 - MVP upload feature)
3. **Week 3**: Phase 4 (US2 - view/download)
4. **Week 4**: Phase 5 + Phase 6 (delete + polish)

**Quality Gates**:
- All tests must pass before moving to next phase
- Code coverage must be >80% for each phase
- Code must pass black formatting and flake8 linting
- Manual smoke testing required for each user story

---

## Notes

- Azure Blob Storage will be provisioned via Feature 004 (Terraform)
- Connection string managed via environment variables (see plan.md)
- python-magic requires libmagic system package on Linux
- Use python-magic-bin on Windows for development
- Signed URLs expire after 1 hour - regenerate if needed
- Maximum 5 attachments per task enforced at view level
- File size limit (10MB) enforced via form validator
- MIME type detection prevents extension spoofing
- Cascade deletion handled via Django signals + on_delete=CASCADE
