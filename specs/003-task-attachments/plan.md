# Implementation Plan: Task File Attachments

**Branch**: `003-task-attachments` | **Date**: 2026-01-19 | **Spec**: [spec.md](spec.md)

## Summary

Implement file attachment system for tasks using Azure Blob Storage. Authenticated users can upload files (max 10MB, allowed types: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG) to their tasks (max 5 per task), view/download attachments, and delete them. System enforces strict ownership validation, generates unique blob names, validates file types via extension and MIME type, and ensures cascade deletion when tasks are deleted.

## Technical Context

**Language/Version**: Python 3.11+ with Django 5.0  
**Primary Dependencies**: 
- azure-storage-blob 12.19+ (Azure Blob Storage SDK)
- python-magic 0.4+ (MIME type detection)
- Django 5.0 (file upload handling, model relationships)
- pytest-django 4.5+ (testing framework)

**Storage**: Azure Blob Storage (provisioned via Feature 004)  
**Testing**: pytest with pytest-django, moto/localstack for Azure emulation, >80% coverage  
**Target Platform**: Azure App Service (Linux Python 3.11)  
**Project Type**: Web application (Django MVT with Azure integration)  
**Performance Goals**: 
- Upload <30s for 5MB files
- Download <5s for typical files
- Attachment list render <1s
- Deletion <5s (blob + record)

**Constraints**: 
- Max 10MB per file
- Max 5 attachments per task
- Allowed file types: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
- Unique blob naming: taskId_timestamp_uuid_originalFilename
- Signed URLs expire in 1 hour
- Strict ownership validation
- >80% test coverage (TDD)

**Scale/Scope**: ~1200 LOC (models, views, storage backend, validators, tests), 3 user stories, 20 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Código Limpio en Python**: ✅ PASS
- Attachment model follows Object Calisthenics (single responsibility)
- Storage backend encapsulated in separate class
- File validators in dedicated module
- No ELSE statements via early returns
- Entity classes <50 lines

**Principle II - Infraestructura como Código**: ✅ PASS
- Azure Blob Storage provisioned via Terraform (Feature 004)
- Storage account connection managed via environment variables
- Container naming follows convention: taskmanager-attachments-{env}

**Principle III - Test-First (TDD)**: ✅ PASS
- All upload/download/delete operations tested before implementation
- Unit tests for validators, storage backend, model methods
- Integration tests for workflows (upload → view → download → delete)
- >80% coverage enforced

**Principle IV - Seguridad Primero**: ✅ PASS
- Ownership validation on all operations (upload, download, delete)
- File type validation (extension + MIME type)
- File size validation (10MB limit)
- Filename sanitization to prevent path traversal
- Signed URLs with 1-hour expiration
- CSRF protection on upload/delete forms

**Principle V - Cloud-Native**: ✅ PASS
- Azure Blob Storage as managed PaaS service
- Streaming uploads for large files
- Connection string from environment variables
- Graceful error handling for storage service failures
- Azure SDK integration for resilient operations

## Project Structure

```
taskmanager/
├── apps/
│   ├── attachments/
│   │   ├── __init__.py
│   │   ├── models.py              # Attachment model
│   │   ├── views.py               # Upload, download, delete views
│   │   ├── forms.py               # AttachmentUploadForm
│   │   ├── validators.py          # File size, type, MIME validators
│   │   ├── storage.py             # Azure Blob Storage backend
│   │   ├── signals.py             # Task deletion cascade handler
│   │   ├── urls.py                # Attachment routes
│   │   └── migrations/
│   │       └── 0001_initial.py
│   └── tasks/
│       └── models.py              # Task model (from Feature 002)
├── tests/
│   └── attachments/
│       ├── __init__.py
│       ├── test_models.py         # Attachment model tests
│       ├── test_validators.py     # File validation tests
│       ├── test_storage.py        # Storage backend tests
│       ├── test_views.py          # View authorization tests
│       ├── test_workflows.py      # End-to-end upload/download/delete
│       ├── test_signals.py        # Cascade deletion tests
│       └── factories.py           # Factory classes for test data
└── conftest.py
```

**Structure Decision**: Django app `attachments` for Feature 003, depends on `tasks` app (Feature 002) and `accounts` app (Feature 001). Uses Azure Blob Storage SDK for file operations. File validation via custom validators. Signed URLs for secure downloads. Cascade deletion via Django signals.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: ✅ NO VIOLATIONS

All constitutional principles followed:
- Principle I (Código Limpio): Object Calisthenics in models, views, storage ✓
- Principle II (IaC): Azure Blob Storage via Terraform ✓
- Principle III (Test-First): TDD with >80% coverage ✓
- Principle IV (Seguridad Primero): Ownership, validation, sanitization ✓
- Principle V (Cloud-Native): Azure SDK, streaming, environment config ✓

**Estimated Total**: ~1200 LOC  
**Actual Total**: TBD (post-implementation)

---

## Phase Execution Summary

### Phase 0: Research
**Status**: ✅ COMPLETE (2026-01-19)

**Artifact**: [research.md](research.md)

**Key Decisions**:
1. Azure Blob Storage SDK integration (azure-storage-blob 12.19+, custom Django storage backend)
2. MIME type detection (python-magic 0.4+ with libmagic)
3. Blob naming strategy (`task_id/timestamp_uuid_sanitized_filename`)
4. Signed URLs (Azure SAS tokens with 1-hour expiration)
5. Cascade deletion (Django post_delete signal on Task model)
6. File streaming (Django default chunked upload + SDK streaming)
7. Testing (in-memory fake for unit tests, Azurite emulator for integration)
8. Error handling (try-except with Azure SDK exceptions, user-friendly messages)

**Open Questions**: ✅ ALL RESOLVED

---

### Phase 1: Design
**Status**: ✅ COMPLETE (2026-01-19)

**Artifacts**:
- [x] [data-model.md](data-model.md) - Attachment model schema, validators, storage backend
- [x] [contracts/README.md](contracts/README.md) - Contracts overview
- [x] [contracts/views.md](contracts/views.md) - Upload/download/delete endpoint contracts
- [x] [contracts/models.md](contracts/models.md) - Attachment model methods, validators
- [x] [contracts/storage.md](contracts/storage.md) - Azure Blob Storage backend contracts
- [x] [quickstart.md](quickstart.md) - Development setup guide (12 steps)

**Key Design Elements**:
1. **Data Model**: Attachment (task FK, original_filename, blob_name, file_size, mime_type, uploaded_at)
2. **Validators**: File size (10MB), MIME type (content-based), extension whitelist
3. **Storage**: Custom Django storage backend (AzureBlobStorage)
4. **Security**: Ownership validation, signed URLs, filename sanitization
5. **Deletion**: Cascade via signals (task deletion → blob deletion)
6. **Dependencies**: azure-storage-blob, python-magic, Azurite for testing

---

### Phase 2: Task Generation
**Status**: ⏳ NOT STARTED

**Next Command**: `/speckit.tasks` on branch `003-task-attachments`

---

### Phase 3: Implementation
**Status**: ✅ COMPLETE (2026-01-20)

**Summary**: All 81 tasks completed across 6 phases:
- Phase 1 (Setup): 8/8 tasks ✅
- Phase 2 (Foundational): 12/12 tasks ✅  
- Phase 3 (US1 - Upload): 14/14 tasks ✅
- Phase 4 (US2 - View/Download): 14/14 tasks ✅
- Phase 5 (US3 - Delete): 13/13 tasks ✅
- Phase 6 (Polish): 20/20 tasks ✅

**Implementation Highlights**:
- Complete file upload system with validation (size, type, MIME)
- Azure Blob Storage integration with signed URLs
- Ownership-based access control
- Cascade deletion via Django signals
- Error handling and logging throughout
- Comprehensive test suite (unit + integration)
- User-friendly templates with progress indicators
- Static CSS for attachment UI

---

## Agent Context Updates

**New Technologies Discovered**:
- azure-storage-blob 12.19+ (Azure Blob Storage SDK)
- python-magic 0.4+ (MIME type detection via libmagic)
- Azure SAS tokens (signed URLs for secure downloads)
- Azurite (local Azure emulator for testing)

**Rationale**: These technologies are required for cloud-native file storage with Azure and secure file handling per Feature 003 specification.

---

## Implementation Readiness

### Prerequisites Met
- ✅ Specification complete and validated
- ✅ Constitution check passed (all 5 principles applicable)
- ✅ Technical research finalized
- ✅ Data model defined (Attachment model + validators + storage backend)
- ✅ Contracts documented (views, models, storage)
- ✅ Quickstart guide written

### Ready for `/speckit.tasks`
- ✅ All design artifacts complete
- ✅ No remaining NEEDS CLARIFICATION markers
- ✅ Acceptance criteria testable
- ✅ Django app structure defined

---

## Artifacts Checklist

- [x] **plan.md** (this file) - Implementation plan
- [x] **research.md** - Technology decisions (8 decisions documented)
- [x] **data-model.md** - Attachment model schema, validators, storage backend, signals
- [x] **contracts/README.md** - Contracts overview
- [x] **contracts/views.md** - Upload/download/delete endpoint contracts
- [x] **contracts/models.md** - Attachment model methods, validators
- [x] **contracts/storage.md** - Azure Blob Storage backend contracts
- [x] **quickstart.md** - Development setup guide (12 steps)

---

## Next Command

**Execute**: Continue Phase 0 research (create research.md)

---

## References

- **Specification**: [spec.md](spec.md) - Feature requirements and acceptance criteria
- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Azure Blob Storage SDK**: https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme
- **Django File Uploads**: https://docs.djangoproject.com/en/5.0/topics/http/file-uploads/
- **python-magic**: https://pypi.org/project/python-magic/
