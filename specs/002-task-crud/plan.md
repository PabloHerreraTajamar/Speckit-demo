# Implementation Plan: Task CRUD Operations

**Branch**: `002-task-crud` | **Date**: 2026-01-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-task-crud/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement complete task management system where authenticated users can create, read, update, and delete their personal tasks. Tasks include title (required), optional description, due date, priority (alta/media/baja), and status (pendiente/completada). Users can filter by status/priority, sort by multiple criteria, view paginated lists (20 per page), and manage only their own tasks with strict ownership enforcement.

## Technical Context

**Language/Version**: Python 3.11+ with Django 5.0  
**Primary Dependencies**: Django 5.0 (ORM, pagination, forms), pytest-django 4.5+ (testing)  
**Storage**: Azure Database for PostgreSQL (provisioned via Feature 004)  
**Testing**: pytest with pytest-django, factory_boy for fixtures, >80% coverage  
**Target Platform**: Azure App Service (Linux Python 3.11, provisioned via Feature 004)  
**Project Type**: Web application (Django MVT architecture)  
**Performance Goals**: <2s task list load (100 tasks), <1s filter/sort operations, <30s task creation  
**Constraints**: Strict ownership isolation, >80% test coverage (TDD), CSRF protection, input validation  
**Scale/Scope**: ~800 LOC (models, views, forms, tests), 5 user stories, 30 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Código Limpio en Python**: ✅ PASS
- Task model follows Object Calisthenics (single responsibility, encapsulation)
- Views and forms use single-purpose classes
- No ELSE statements via early returns
- QuerySet filters encapsulated in manager methods
- Entity classes <50 lines

**Principle III - Test-First (TDD)**: ✅ PASS
- All CRUD operations tested before implementation
- Unit tests for models, forms, views
- Integration tests for workflows (create → filter → update → delete)
- >80% coverage enforced

**Principle IV - Seguridad Primero**: ✅ PASS
- Ownership validation on all operations (only owner can view/edit/delete)
- CSRF protection on all forms
- Input validation (title length, description length, XSS prevention)
- Authorization checks via ownership comparison
- Django ORM prevents SQL injection

**Other Principles**: N/A (Principles II and V handled by Feature 004)

## Project Structure

### Documentation (this feature)

```text
specs/002-task-crud/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
taskmanager/                     # Django project root
├── tasks/                       # Task management app (Feature 002)
│   ├── __init__.py
│   ├── models.py                # Task model
│   ├── forms.py                 # TaskForm (create/edit)
│   ├── views.py                 # TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView
│   ├── urls.py                  # URL routing for task endpoints
│   ├── managers.py              # TaskQuerySet with filter/sort methods
│   ├── validators.py            # Title/description length validation
│   ├── filters.py               # TaskFilter class for query building
│   └── migrations/
│       └── 0001_initial.py
├── accounts/                    # Authentication app (Feature 001, dependency)
│   └── models.py                # User model (owner foreign key)
├── taskmanager/                 # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── templates/
│   └── tasks/
│       ├── task_list.html       # Paginated list with filters
│       ├── task_detail.html     # Full task details
│       ├── task_form.html       # Create/edit form
│       └── task_confirm_delete.html
└── static/
    └── tasks/
        └── css/
            └── tasks.css

tests/
├── tasks/                       # Feature 002 tests
│   ├── test_models.py           # Task model tests
│   ├── test_forms.py            # Form validation tests
│   ├── test_views.py            # View authorization tests
│   ├── test_crud_workflows.py   # End-to-end CRUD tests
│   ├── test_filters.py          # Filtering and sorting tests
│   ├── test_pagination.py       # Pagination tests
│   └── factories.py             # Factory classes for test data
└── conftest.py
```

**Structure Decision**: Django app `tasks` for Feature 002, depends on `accounts` app from Feature 001 for User model. Follows Django class-based views (ListView, DetailView, CreateView, UpdateView, DeleteView) for CRUD operations. Pagination handled by Django Paginator. Filtering via custom TaskFilter class. Tests use factory_boy for generating test tasks.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: ✅ NO VIOLATIONS

All constitutional principles followed:
- Principle I (Código Limpio): Object Calisthenics in models, views, forms ✓
- Principle III (Test-First): TDD with >80% coverage ✓
- Principle IV (Seguridad Primero): Ownership checks, CSRF, validation ✓

**Estimated Total**: ~800 LOC  
**Actual Total**: TBD (post-implementation)

---

## Phase Execution Summary

### Phase 0: Research
**Status**: ✅ COMPLETE (2026-01-19)

**Artifact**: [research.md](research.md)

**Key Decisions**:
1. Django Class-Based Views (CreateView, UpdateView, DeleteView, ListView, DetailView)
2. QuerySet filtering via custom TaskQuerySet manager
3. Django Paginator for pagination (20 items per page)
4. Custom TaskFilter class for filter/sort logic
5. factory_boy for test data generation
6. Ownership validation via get_queryset override in views
7. Auto-update completed_at timestamp in model save()
8. RESTful URL routing with namespacing

**Open Questions**: ✅ ALL RESOLVED

---

### Phase 1: Design
**Status**: ✅ COMPLETE (2026-01-19)

**Artifacts**:
- [x] [data-model.md](data-model.md) - Task model schema
- [x] [contracts/README.md](contracts/README.md) - Contracts overview
- [x] [contracts/views.md](contracts/views.md) - HTTP request/response contracts for CRUD endpoints
- [x] [contracts/models.md](contracts/models.md) - Task model methods and queryset contracts
- [x] [quickstart.md](quickstart.md) - Development setup guide

**Key Design Elements**:
1. **Data Model**: Task (title, description, due_date, priority, status, created_at, updated_at, completed_at, owner FK)
2. **Validation**: Title max 200 chars, description max 2000 chars, whitespace trimming
3. **Authorization**: User can only view/edit/delete their own tasks (owner FK check)
4. **Filtering**: Status (pendiente/completada), priority (alta/media/baja), sort by creation/due_date/priority
5. **Pagination**: 20 tasks per page, Django Paginator
6. **Indexes**: 4 composite indexes (owner+created_at, owner+status, owner+priority, owner+due_date)

---

### Phase 2: Task Generation
**Status**: ⏳ NOT STARTED

**Next Command**: `/speckit.tasks` on branch `002-task-crud`

---

### Phase 3: Implementation
**Status**: ⏳ NOT STARTED

---

## Agent Context Updates

**New Technologies Discovered**:
- Django Paginator (built-in pagination)
- factory_boy 3.3+ (test data generation)
- Django QuerySet filtering (filter/exclude/order_by)

**Rationale**: These technologies are standard Django patterns for CRUD applications and are required for Feature 002 task management implementation.

---

## Implementation Readiness

### Prerequisites Met
- ✅ Specification complete and validated
- ✅ Constitution check passed (3 principles applicable)
- ✅ Technical research finalized
- ✅ Data model defined (Task model with owner FK)
- ✅ Contracts documented (views, models)
- ✅ Quickstart guide written

### Ready for `/speckit.tasks`
- ✅ All design artifacts complete
- ✅ No remaining NEEDS CLARIFICATION markers
- ✅ Acceptance criteria testable
- ✅ Django app structure defined

---

## Artifacts Checklist

- [x] **plan.md** (this file) - Implementation plan
- [x] **research.md** - Technology decisions
- [x] **data-model.md** - Task model schema
- [x] **contracts/README.md** - Contracts overview
- [x] **contracts/views.md** - CRUD endpoint contracts
- [x] **contracts/models.md** - Task model methods
- [x] **quickstart.md** - Development setup guide

---

## Next Command

**Execute**: `/speckit.tasks` on branch `002-task-crud`

**Purpose**: Generate implementation tasks for:
1. Task model creation (fields, validation, migrations)
2. CRUD views (Create, Read, Update, Delete, List)
3. Forms and validators (TaskForm with validation)
4. Filtering and pagination (TaskFilter, Paginator)
5. Templates (list, detail, form, delete confirmation)
6. Tests (model, form, view, workflow, filters, pagination)

---

## References

- **Specification**: [spec.md](spec.md) - Feature requirements and acceptance criteria
- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Django Class-Based Views**: https://docs.djangoproject.com/en/5.0/topics/class-based-views/
- **Django Pagination**: https://docs.djangoproject.com/en/5.0/topics/pagination/
- **factory_boy**: https://factoryboy.readthedocs.io/
