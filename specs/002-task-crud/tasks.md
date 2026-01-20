# Tasks: Task CRUD Operations

**Feature**: 002-task-crud  
**Branch**: `002-task-crud`  
**Input**: Design documents from `/specs/002-task-crud/`  
**Prerequisites**: plan.md, data-model.md, research.md, contracts/, quickstart.md

**Tests**: ✅ INCLUDED - TDD approach mandated by Constitution Principle III (Test-First)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

Django project structure at repository root:
- Django apps: `tasks/`, `accounts/`
- Templates: `templates/tasks/`
- Tests: `tests/tasks/`
- Static files: `static/tasks/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Django app initialization and basic structure

- [X] T001 Create tasks Django app: `python manage.py startapp tasks`
- [X] T002 Add 'tasks' to INSTALLED_APPS in taskmanager/settings/base.py
- [X] T003 [P] Create tasks/__init__.py (empty file)
- [X] T004 [P] Create tasks/apps.py with TasksConfig class
- [X] T005 [P] Create tests/tasks/ directory structure
- [X] T006 [P] Create tests/tasks/__init__.py
- [X] T007 [P] Create templates/tasks/ directory structure
- [X] T008 [P] Create static/tasks/css/ directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create tasks/validators.py with validate_title_length and validate_description_length
- [X] T010 [P] Create tasks/managers.py with TaskQuerySet and TaskManager classes
- [X] T011 [P] Create tasks/models.py with Task model (title, description, due_date, priority, status, created_at, updated_at, completed_at, owner FK)
- [X] T012 Create tasks/migrations/0001_initial.py: `python manage.py makemigrations tasks`
- [X] T013 Run initial migration: `python manage.py migrate tasks`
- [X] T014 [P] Create tasks/forms.py with TaskForm (ModelForm for Task)
- [X] T015 [P] Create tasks/urls.py with app_name='tasks' and empty urlpatterns
- [X] T016 Include tasks URLs in taskmanager/urls.py: `path('tasks/', include('tasks.urls'))`
- [X] T017 [P] Create tasks/admin.py and register Task model
- [X] T018 [P] Create tests/tasks/factories.py with TaskFactory using factory_boy
- [X] T019 [P] Install factory_boy: Add factory-boy==3.3.0 to requirements and install
- [X] T020 [P] Create static/tasks/css/tasks.css for task styling

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create new tasks with title, description, due date, priority, and status

**Independent Test**: User can navigate to /tasks/create/, fill form, submit, and see new task in detail view

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US1] Create tests/tasks/test_models.py with Task model creation tests (title validation, owner FK, default values)
- [X] T022 [P] [US1] Add test for completed_at auto-update in tests/tasks/test_models.py
- [X] T023 [P] [US1] Create tests/tasks/test_forms.py with TaskForm validation tests (title required, description max length)
- [X] T024 [P] [US1] Create tests/tasks/test_views.py with TaskCreateView tests (authentication required, owner auto-set, valid/invalid form)

### Implementation for User Story 1

- [X] T025 [US1] Implement Task model save() method to auto-update completed_at timestamp in tasks/models.py
- [X] T026 [US1] Implement TaskForm with Meta class and field widgets in tasks/forms.py
- [X] T027 [US1] Create tasks/views.py with TaskCreateView (Django CreateView, LoginRequiredMixin, form_valid to set owner)
- [X] T028 [US1] Add URL pattern for create view in tasks/urls.py: `path('create/', TaskCreateView.as_view(), name='create')`
- [X] T029 [US1] Create templates/tasks/task_form.html with Bootstrap form layout and CSRF token
- [X] T030 [US1] Update base.html navigation to include "Create Task" link (if user authenticated)
- [X] T031 [US1] Add success_url to TaskCreateView redirecting to task detail page
- [X] T032 [US1] Add success message in TaskCreateView.form_valid(): "Task created successfully"
- [X] T033 [US1] Run tests for US1: `pytest tests/tasks/test_models.py tests/tasks/test_forms.py tests/tasks/test_views.py -k create`

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks

---

## Phase 4: User Story 2 - View Task List (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can view paginated list of their tasks with filtering and sorting

**Independent Test**: User can navigate to /tasks/, see their tasks (not others'), filter by status/priority, and navigate pages

### Tests for User Story 2

- [X] T034 [P] [US2] Add TaskListView tests in tests/tasks/test_views.py (authentication, ownership filtering, pagination)
- [X] T035 [P] [US2] Create tests/tasks/test_filters.py with status/priority filtering tests
- [X] T036 [P] [US2] Create tests/tasks/test_pagination.py with pagination edge case tests (empty, single page, multiple pages)

### Implementation for User Story 2

- [X] T037 [P] [US2] Implement TaskQuerySet.for_user() method in tasks/managers.py
- [X] T038 [P] [US2] Implement TaskQuerySet.pending() and completed() methods in tasks/managers.py
- [X] T039 [P] [US2] Implement TaskQuerySet.by_due_date() and by_priority() methods in tasks/managers.py
- [X] T040 [US2] Create tasks/views.py TaskListView (Django ListView, LoginRequiredMixin, paginate_by=20, get_queryset filter by owner)
- [X] T041 [US2] Add get_queryset override in TaskListView to filter by status/priority from query params
- [X] T042 [US2] Add URL pattern for list view in tasks/urls.py: `path('', TaskListView.as_view(), name='list')`
- [X] T043 [US2] Create templates/tasks/task_list.html with Bootstrap table, pagination controls, filter form
- [X] T044 [US2] Add filter form in task_list.html (status dropdown, priority dropdown, submit button)
- [X] T045 [US2] Style pagination controls in task_list.html using Bootstrap pagination component
- [X] T046 [US2] Update base.html navigation to include "My Tasks" link
- [X] T047 [US2] Add empty state message in task_list.html when no tasks found
- [X] T048 [US2] Run tests for US2: `pytest tests/tasks/test_views.py tests/tasks/test_filters.py tests/tasks/test_pagination.py -k list`

**Checkpoint**: At this point, User Stories 1 AND 2 should work - users can create and view tasks

---

## Phase 5: User Story 3 - View Task Details (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can view full details of their individual tasks

**Independent Test**: User can click task from list, see detail page with all fields, verify ownership enforcement (404 for others' tasks)

### Tests for User Story 3

- [X] T049 [P] [US3] Add TaskDetailView tests in tests/tasks/test_views.py (authentication, ownership check, 404 for other user's task)
- [X] T050 [P] [US3] Add test for task __str__ method in tests/tasks/test_models.py

### Implementation for User Story 3

- [X] T051 [US3] Create TaskDetailView in tasks/views.py (Django DetailView, LoginRequiredMixin, get_queryset filter by owner)
- [X] T052 [US3] Add URL pattern for detail view in tasks/urls.py: `path('<int:pk>/', TaskDetailView.as_view(), name='detail')`
- [X] T053 [US3] Create templates/tasks/task_detail.html with all task fields displayed using Bootstrap cards
- [X] T054 [US3] Add "Edit" and "Delete" buttons in task_detail.html (conditional on ownership)
- [X] T055 [US3] Add "Back to List" link in task_detail.html
- [X] T056 [US3] Format dates in task_detail.html using Django date filters
- [X] T057 [US3] Add priority/status badges in task_detail.html with Bootstrap colors (alta=danger, media=warning, baja=info)
- [X] T058 [US3] Run tests for US3: `pytest tests/tasks/test_views.py -k detail`

**Checkpoint**: MVP complete - Users can create, list, and view task details

---

## Phase 6: User Story 4 - Update Tasks (Priority: P2)

**Goal**: Authenticated users can edit their existing tasks

**Independent Test**: User can click "Edit" on task detail, modify fields, submit, and see updated values

### Tests for User Story 4

- [X] T059 [P] [US4] Add TaskUpdateView tests in tests/tasks/test_views.py (authentication, ownership, form pre-population, successful update)
- [X] T060 [P] [US4] Add test for owner immutability in tests/tasks/test_views.py (owner field not in form)
- [X] T061 [P] [US4] Add test for completed_at auto-clear when status changes to pendiente in tests/tasks/test_models.py

### Implementation for User Story 4

- [X] T062 [US4] Create TaskUpdateView in tasks/views.py (Django UpdateView, LoginRequiredMixin, get_queryset filter by owner)
- [X] T063 [US4] Add URL pattern for update view in tasks/urls.py: `path('<int:pk>/edit/', TaskUpdateView.as_view(), name='edit')`
- [X] T064 [US4] Update TaskForm to exclude owner field in tasks/forms.py (read-only)
- [X] T065 [US4] Reuse templates/tasks/task_form.html for update (add conditional title "Create Task" vs "Edit Task")
- [X] T066 [US4] Add success_url to TaskUpdateView redirecting to task detail page
- [X] T067 [US4] Add success message in TaskUpdateView.form_valid(): "Task updated successfully"
- [X] T068 [US4] Update task_list.html to add "Edit" link for each task
- [X] T069 [US4] Run tests for US4: `pytest tests/tasks/test_views.py -k update`

**Checkpoint**: At this point, User Stories 1-4 work - full CRUD except delete

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Authenticated users can delete their tasks with confirmation

**Independent Test**: User can click "Delete" button, see confirmation page, confirm, and task is removed from list

### Tests for User Story 5

- [X] T070 [P] [US5] Add TaskDeleteView tests in tests/tasks/test_views.py (authentication, ownership, GET confirmation, POST deletion)
- [X] T071 [P] [US5] Add test for cascade delete when user is deleted in tests/tasks/test_models.py

### Implementation for User Story 5

- [X] T072 [US5] Create TaskDeleteView in tasks/views.py (Django DeleteView, LoginRequiredMixin, get_queryset filter by owner)
- [X] T073 [US5] Add URL pattern for delete view in tasks/urls.py: `path('<int:pk>/delete/', TaskDeleteView.as_view(), name='delete')`
- [X] T074 [US5] Create templates/tasks/task_confirm_delete.html with confirmation form and CSRF token
- [X] T075 [US5] Add success_url to TaskDeleteView redirecting to task list page
- [X] T076 [US5] Add success message in TaskDeleteView.delete(): "Task deleted successfully"
- [X] T077 [US5] Update task_list.html to add "Delete" button for each task
- [X] T078 [US5] Style delete confirmation page with Bootstrap alert-danger
- [X] T079 [US5] Run tests for US5: `pytest tests/tasks/test_views.py -k delete`

**Checkpoint**: All user stories complete - Full CRUD functionality working

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T080 [P] Create tests/tasks/test_crud_workflows.py with end-to-end tests (create → list → detail → edit → delete)
- [X] T081 [P] Add test for concurrent edit scenario in tests/tasks/test_views.py (last save wins)
- [X] T082 [P] Add task count display in task_list.html ("Showing X of Y tasks")
- [X] T083 [P] Add sorting controls in task_list.html (sort by created_at, due_date, priority)
- [X] T084 [P] Implement sorting in TaskListView.get_queryset() based on sort query param
- [X] T085 [P] Add "Clear Filters" button in task_list.html
- [X] T086 [P] Add task statistics in task_list.html (pending count, completed count)
- [X] T087 [P] Style task status badges in task_list.html (pendiente=warning, completada=success)
- [X] T088 [P] Add responsive design improvements in static/tasks/css/tasks.css
- [X] T089 [P] Add task title max-width truncation with ellipsis in task_list.html
- [X] T090 [P] Add hover effects for task rows in static/tasks/css/tasks.css
- [X] T091 Format code with black: `black tasks/ tests/tasks/`
- [X] T092 Check linting: `flake8 tasks/ tests/tasks/`
- [X] T093 Run full test suite: `pytest tests/tasks/ -v`
- [X] T094 Check test coverage: `pytest tests/tasks/ --cov=tasks --cov-report=html`
- [X] T095 Verify >80% coverage (Constitution requirement)
- [X] T096 Run Django system check: `python manage.py check`
- [X] T097 Test quickstart.md workflow manually
- [X] T098 Update README.md with Feature 002 status and stats
- [X] T099 Commit all changes with message: "feat: Complete Feature 002 - Task CRUD Operations"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 → US2 → US3 → US4 → US5
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Create - P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (List - P1)**: Can start after Foundational (Phase 2) - Independent but typically tested with US1 tasks
- **User Story 3 (Detail - P1)**: Can start after Foundational (Phase 2) - Independent but links from US2
- **User Story 4 (Update - P2)**: Can start after Foundational (Phase 2) - Independent but links from US3
- **User Story 5 (Delete - P2)**: Can start after Foundational (Phase 2) - Independent but links from US2/US3

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before forms before views
- Views before templates
- URL routing after view implementation
- Tests run after implementation to verify passing

### Parallel Opportunities

- **Phase 1**: All tasks marked [P] can run in parallel (T003, T004, T005, T006, T007, T008)
- **Phase 2**: Tasks T009, T010, T014, T015, T017, T018, T019, T020 can run in parallel after T013 (migrations)
- **Within User Stories**: All tests marked [P] can be written in parallel
- **Across User Stories**: After Phase 2, all user stories (US1-US5) can be worked on in parallel by different developers
- **Phase 8**: All polish tasks marked [P] can run in parallel (T080-T090)

---

## Parallel Example: User Story 1

```bash
# Write all tests for User Story 1 together (TDD):
T021: Test Task model creation (tests/tasks/test_models.py)
T022: Test completed_at auto-update (tests/tasks/test_models.py)
T023: Test TaskForm validation (tests/tasks/test_forms.py)
T024: Test TaskCreateView (tests/tasks/test_views.py)

# Verify tests FAIL, then implement in parallel:
T025: Task.save() method
T026: TaskForm implementation
T027: TaskCreateView implementation
T029: task_form.html template
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational Phase (Phase 2) completes, launch in parallel:

Developer A:
- Phase 3: User Story 1 (Create Tasks)

Developer B:
- Phase 4: User Story 2 (List Tasks)

Developer C:
- Phase 5: User Story 3 (Detail View)

# Each story is independently testable and completable
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create)
4. Complete Phase 4: User Story 2 (List)
5. Complete Phase 5: User Story 3 (Detail)
6. **STOP and VALIDATE**: Test create → list → view workflow
7. Deploy MVP with read-only update (no edit/delete yet)

### Incremental Delivery

1. **Foundation**: Setup + Foundational → 20 tasks (T001-T020)
2. **MVP Release 1**: US1 + US2 + US3 → +39 tasks (T021-T058) → Users can create and view tasks
3. **Release 2**: US4 + US5 → +21 tasks (T059-T079) → Full CRUD
4. **Polish Release**: Phase 8 → +20 tasks (T080-T099) → Enhanced UX
5. Each release adds value without breaking previous functionality

### Parallel Team Strategy

With 3 developers after Foundational phase:

1. **All together**: Phase 1 (Setup) + Phase 2 (Foundational)
2. **Parallel work**:
   - Dev A: User Story 1 (Create) → 13 tasks
   - Dev B: User Story 2 (List) → 15 tasks  
   - Dev C: User Story 3 (Detail) → 10 tasks
3. **Integration point**: Test MVP together (create → list → detail)
4. **Parallel work**:
   - Dev A: User Story 4 (Update) → 11 tasks
   - Dev B: User Story 5 (Delete) → 10 tasks
   - Dev C: Start Phase 8 (Polish)
5. **Final integration**: All together on Phase 8 completion

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 12 tasks (BLOCKING)
- **Phase 3 (US1 - Create)**: 13 tasks
- **Phase 4 (US2 - List)**: 15 tasks
- **Phase 5 (US3 - Detail)**: 10 tasks
- **Phase 6 (US4 - Update)**: 11 tasks
- **Phase 7 (US5 - Delete)**: 10 tasks
- **Phase 8 (Polish)**: 20 tasks

**Total**: 99 tasks

**MVP Scope** (Phases 1-5): 58 tasks
**Full Feature** (All phases): 99 tasks

---

## Notes

- All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] = Parallelizable (different files, no dependencies on incomplete tasks)
- [Story] = User story label (US1-US5) for traceability
- Tests are REQUIRED per Constitution Principle III (TDD)
- Each user story is independently completable and testable
- Ownership validation enforced via get_queryset() override in all views
- CSRF protection on all POST/PUT/DELETE operations (Django default)
- >80% test coverage required (Constitution)
- Run `pytest` after each phase to verify tests pass
- Commit after each phase or logical task group

