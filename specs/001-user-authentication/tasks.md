# Tasks: User Authentication System

**Feature**: 001-user-authentication  
**Branch**: `001-user-authentication`  
**Input**: Design documents from `/specs/001-user-authentication/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: ✅ INCLUDED - TDD approach mandated by Constitution Principle III (Test-First)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Django project initialization and accounts app structure

- [X] T001 Create Django project structure: taskmanager/ directory with manage.py
- [X] T002 Create accounts app using `python manage.py startapp accounts`
- [X] T003 [P] Configure git repository with .gitignore for Python/Django
- [X] T004 [P] Create virtual environment and install dependencies (django==5.0, psycopg2-binary, bcrypt, pytest-django, pytest-cov)
- [X] T005 [P] Setup Django settings split: taskmanager/settings/base.py, development.py, production.py
- [X] T006 [P] Configure INSTALLED_APPS to include accounts app in taskmanager/settings/base.py
- [X] T007 [P] Configure AUTH_USER_MODEL = 'accounts.User' in taskmanager/settings/base.py
- [X] T008 [P] Configure PASSWORD_HASHERS with BCryptSHA256PasswordHasher first in taskmanager/settings/base.py
- [X] T009 [P] Configure DATABASES with PostgreSQL connection from env vars in taskmanager/settings/base.py
- [X] T010 [P] Configure session settings (HttpOnly, Secure, SameSite=Lax) in taskmanager/settings/base.py
- [X] T011 [P] Create templates directory: templates/accounts/
- [X] T012 [P] Create tests directory structure: tests/accounts/
- [X] T013 [P] Configure pytest in pytest.ini with Django settings module
- [X] T014 [P] Create .env.example with DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T015 Create UserManager custom manager in accounts/managers.py with normalize_email and create_user methods
- [X] T016 Create custom User model extending AbstractUser in accounts/models.py (email, username, objects=UserManager)
- [X] T017 Create AuthenticationLog model in accounts/models.py (user, event_type, ip_address, user_agent, timestamp, success, metadata)
- [X] T018 Create database migration for User and AuthenticationLog: `python manage.py makemigrations accounts`
- [X] T019 Apply migrations to create database tables: `python manage.py migrate` (Using SQLite for local development)
- [X] T020 [P] Create password validator in accounts/validators.py (min 8 chars, complexity rules)
- [X] T021 [P] Create username validator in accounts/validators.py (3-30 alphanumeric)
- [X] T022 [P] Configure URL routing in accounts/urls.py with app_name='accounts'
- [X] T023 Include accounts URLs in taskmanager/urls.py: `path('accounts/', include('accounts.urls'))`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel (T019 will be completed when database is available)

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Allow new users to create accounts with email/username/password

**Independent Test**: Navigate to /accounts/register/, submit valid data, verify user created in database with bcrypt-hashed password

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T024 [P] [US1] Unit test for User.objects.create_user in tests/accounts/test_models.py
- [X] T025 [P] [US1] Unit test for password hashing (bcrypt) in tests/accounts/test_models.py
- [X] T026 [P] [US1] Unit test for email normalization (lowercase) in tests/accounts/test_models.py
- [X] T027 [P] [US1] Unit test for RegistrationForm validation in tests/accounts/test_forms.py
- [X] T028 [P] [US1] Unit test for RegistrationForm password matching in tests/accounts/test_forms.py
- [X] T029 [P] [US1] Unit test for RegistrationForm duplicate email rejection in tests/accounts/test_forms.py
- [X] T030 [P] [US1] Integration test for registration view GET request in tests/accounts/test_views.py
- [X] T031 [P] [US1] Integration test for registration view POST success in tests/accounts/test_views.py
- [X] T032 [P] [US1] Integration test for registration with duplicate email in tests/accounts/test_views.py
- [X] T033 [P] [US1] Integration test for registration with weak password in tests/accounts/test_views.py

### Implementation for User Story 1

- [X] T034 [P] [US1] Create RegistrationForm in accounts/forms.py with email, username, password, password_confirm fields
- [X] T035 [US1] Implement RegistrationForm.clean_email() to check uniqueness and normalize to lowercase
- [X] T036 [US1] Implement RegistrationForm.clean() to validate password match
- [X] T037 [US1] Implement RegistrationForm.save() to hash password using set_password()
- [X] T038 [US1] Create register view function in accounts/views.py handling GET/POST
- [X] T039 [US1] Add CSRF protection to register view
- [X] T040 [US1] Add URL route for register: path('register/', views.register, name='register') in accounts/urls.py
- [X] T041 [P] [US1] Create register.html template in templates/accounts/ with form and CSRF token
- [X] T042 [US1] Implement registration success redirect to login page (redirects to register with success message for now)
- [X] T043 [P] [US1] Create Django signal receiver for registration logging in accounts/signals.py
- [X] T044 [US1] Connect registration signal in accounts/apps.py ready() method
- [X] T045 [US1] Run tests for User Story 1: `pytest tests/accounts/test_models.py tests/accounts/test_forms.py tests/accounts/test_views.py -v`

**Checkpoint**: User registration fully functional - users can create accounts (22/22 tests passing, 92% coverage)

---

## Phase 4: User Story 2 - User Login & Logout (Priority: P1) 🎯 MVP

**Goal**: Allow registered users to log in with credentials and log out securely

**Independent Test**: Create test user, log in with correct credentials, verify session created, access protected page, log out, verify session destroyed

### Tests for User Story 2 (TDD - Write First)

- [X] T046 [P] [US2] Unit test for LoginForm validation in tests/accounts/test_forms.py
- [X] T047 [P] [US2] Integration test for login view GET request in tests/accounts/test_views.py
- [X] T048 [P] [US2] Integration test for login with valid credentials in tests/accounts/test_views.py
- [X] T049 [P] [US2] Integration test for login with incorrect password in tests/accounts/test_views.py
- [X] T050 [P] [US2] Integration test for login with non-existent email in tests/accounts/test_views.py
- [X] T051 [P] [US2] Integration test for login redirect to 'next' parameter in tests/accounts/test_views.py
- [X] T052 [P] [US2] Integration test for logout POST request in tests/accounts/test_views.py
- [X] T053 [P] [US2] Integration test for logout session destruction in tests/accounts/test_views.py
- [X] T054 [P] [US2] Integration test for unauthenticated redirect to login in tests/accounts/test_views.py
- [X] T055 [P] [US2] E2E test for complete login-logout cycle in tests/accounts/test_authentication.py

### Implementation for User Story 2

- [X] T056 [P] [US2] Create LoginForm in accounts/forms.py with email and password fields
- [X] T057 [US2] Create login_view function in accounts/views.py with Django authenticate() and login()
- [X] T058 [US2] Implement generic error message "Invalid credentials" (don't leak user existence)
- [X] T059 [US2] Add session creation and last_login update in login_view
- [X] T060 [US2] Add URL route for login: path('login/', views.login_view, name='login') in accounts/urls.py
- [X] T061 [P] [US2] Create login.html template in templates/accounts/ with form and CSRF token
- [X] T062 [US2] Implement login redirect to 'next' parameter or /dashboard/
- [X] T063 [P] [US2] Create Django signal receiver for login logging in accounts/signals.py
- [X] T064 [US2] Create Django signal receiver for failed login logging in accounts/signals.py
- [X] T065 [US2] Create logout_view function in accounts/views.py with Django logout()
- [X] T066 [US2] Add URL route for logout: path('logout/', views.logout_view, name='logout') in accounts/urls.py
- [X] T067 [P] [US2] Create Django signal receiver for logout logging in accounts/signals.py
- [X] T068 [US2] Run tests for User Story 2: `pytest tests/accounts/test_authentication.py -v`

**Checkpoint**: Login/logout fully functional - users can authenticate and access protected resources ✅

---

## Phase 5: User Story 3 - Profile Management (Priority: P2)

**Goal**: Allow logged-in users to view and update their profile information

**Independent Test**: Log in, navigate to profile page, update first/last name, verify changes persist and display

### Tests for User Story 3 (TDD - Write First)

- [X] T069 [P] [US3] Unit test for ProfileForm validation in tests/accounts/test_forms.py
- [X] T070 [P] [US3] Unit test for ProfileForm email uniqueness check in tests/accounts/test_forms.py
- [X] T071 [P] [US3] Integration test for profile view GET request (authenticated) in tests/accounts/test_views.py
- [X] T072 [P] [US3] Integration test for profile view GET request (unauthenticated redirect) in tests/accounts/test_views.py
- [X] T073 [P] [US3] Integration test for profile update POST success in tests/accounts/test_views.py
- [X] T074 [P] [US3] Integration test for profile update with duplicate email in tests/accounts/test_views.py
- [X] T075 [P] [US3] Integration test for authorization (user can only edit own profile) in tests/accounts/test_views.py

### Implementation for User Story 3

- [X] T076 [P] [US3] Create ProfileForm in accounts/forms.py with first_name, last_name, email fields
- [X] T077 [US3] Implement ProfileForm.clean_email() to check uniqueness (excluding current user)
- [X] T078 [US3] Create profile_view function in accounts/views.py with @login_required decorator
- [X] T079 [US3] Implement profile view GET to display current user data
- [X] T080 [US3] Implement profile view POST to update user data
- [X] T081 [US3] Add URL route for profile: path('profile/', views.profile_view, name='profile') in accounts/urls.py
- [X] T082 [P] [US3] Create profile.html template in templates/accounts/ with form pre-filled
- [X] T083 [US3] Add success message "Profile updated" to profile view
- [X] T084 [US3] Run tests for User Story 3: `pytest tests/accounts/test_forms.py::TestProfileForm tests/accounts/test_views.py::TestProfileView -v`

**Checkpoint**: Profile management complete - users can view and update their information ✅

---

## Phase 6: User Story 4 - Password Change (Priority: P2)

**Goal**: Allow logged-in users to change their password securely

**Independent Test**: Log in, navigate to password change page, submit old and new passwords, log out, verify login with new password works

### Tests for User Story 4 (TDD - Write First)

- [X] T085 [P] [US4] Unit test for ChangePasswordForm validation in tests/accounts/test_forms.py
- [X] T086 [P] [US4] Unit test for ChangePasswordForm password matching in tests/accounts/test_forms.py
- [X] T087 [P] [US4] Integration test for password change view GET request in tests/accounts/test_views.py
- [X] T088 [P] [US4] Integration test for password change POST success in tests/accounts/test_views.py
- [X] T089 [P] [US4] Integration test for password change with incorrect current password in tests/accounts/test_views.py
- [X] T090 [P] [US4] Integration test for password change with weak new password in tests/accounts/test_views.py
- [X] T091 [P] [US4] E2E test for password change then login with new password in tests/accounts/test_authentication.py

### Implementation for User Story 4

- [X] T092 [P] [US4] Create ChangePasswordForm in accounts/forms.py with current_password, new_password, new_password_confirm
- [X] T093 [US4] Implement ChangePasswordForm.clean_current_password() to validate against user's current password
- [X] T094 [US4] Implement ChangePasswordForm.clean() to validate new password match
- [X] T095 [US4] Implement ChangePasswordForm.save() to update password with set_password()
- [X] T096 [US4] Create change_password_view function in accounts/views.py with @login_required decorator
- [X] T097 [US4] Add URL route for password change: path('profile/password/', views.change_password_view, name='change_password') in accounts/urls.py
- [X] T098 [P] [US4] Create change_password.html template in templates/accounts/ with form
- [X] T099 [US4] Implement redirect to profile page with success message after password change
- [X] T100 [P] [US4] Create Django signal receiver for password change logging in accounts/signals.py
- [X] T101 [US4] Run tests for User Story 4: `pytest tests/accounts/test_authentication.py::test_password_change -v`

**Checkpoint**: Password change complete - users can securely update their passwords

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, final validation, and documentation

- [X] T102 [P] Add custom CSS styling to templates/accounts/*.html (optional, basic styling)
- [X] T103 [P] Create base.html template with common header/footer for inheritance
- [X] T104 [P] Update all templates to extend base.html for consistency
- [X] T105 [P] Add Django messages framework to display success/error notifications
- [X] T106 [P] Create custom 403.html, 404.html, 500.html error templates
- [X] T107 Run full test suite: `pytest tests/accounts/ -v --cov=accounts --cov-report=term-missing`
- [X] T108 Verify test coverage exceeds 80% threshold (TDD requirement)
- [X] T109 Run Django system checks: `python manage.py check`
- [X] T110 [P] Create Django admin registration for User and AuthenticationLog models in accounts/admin.py
- [X] T111 [P] Add docstrings to all models, forms, views (Google style)
- [X] T112 Run code formatting: `black accounts/ tests/accounts/`
- [X] T113 Run linting: `flake8 accounts/ tests/accounts/`
- [X] T114 Validate quickstart.md guide by following steps 1-11
- [X] T115 Create superuser account: `python manage.py createsuperuser`
- [X] T116 Manual testing: Complete end-to-end user journey (register → login → profile → password change → logout)
- [X] T117 Verify all authentication events logged in AuthenticationLog table
- [X] T118 [P] Update README.md with feature 001 completion and usage instructions
- [X] T119 Commit all changes: `git add -A && git commit -m "feat(auth): complete user authentication system (119 tasks)"`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Registration) - P1 Priority, no dependencies on other stories
  - User Story 2 (Login/Logout) - P1 Priority, no dependencies (but registration needed for test users)
  - User Story 3 (Profile) - P2 Priority, depends on login (must be authenticated)
  - User Story 4 (Password Change) - P2 Priority, depends on login (must be authenticated)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Registration)**: Can start immediately after Foundational (Phase 2)
- **User Story 2 (P1 - Login/Logout)**: Can start immediately after Foundational (Phase 2) - technically independent but needs US1 for test users
- **User Story 3 (P2 - Profile)**: Depends on US2 (must login to access profile)
- **User Story 4 (P2 - Password Change)**: Depends on US2 (must login to change password)

### Suggested Implementation Strategy

**MVP Delivery (Priority: P1)**:
1. Phase 1 (Setup)
2. Phase 2 (Foundational)
3. Phase 3 (User Story 1 - Registration) 
4. Phase 4 (User Story 2 - Login/Logout)
5. Basic polish (T107-T109 for validation)

**Full Feature (Priority: P2)**:
6. Phase 5 (User Story 3 - Profile)
7. Phase 6 (User Story 4 - Password Change)
8. Phase 7 (Complete polish and documentation)

### Within Each User Story

**TDD Workflow** (mandated by Constitution):
1. Write tests FIRST (all test tasks for the story)
2. Run tests and verify they FAIL
3. Implement functionality (implementation tasks)
4. Run tests again and verify they PASS
5. Refactor code while keeping tests green

**Task Order Within Story**:
- Tests before implementation
- Models before forms
- Forms before views
- Views before templates
- URL routing after views
- Signals after core implementation
- Run tests to verify story complete

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T003-T014 can all run in parallel (different files)

**Within Foundational (Phase 2)**:
- T020-T023 can run in parallel after T015-T019 complete

**Within User Story 1 (Phase 3)**:
- T024-T033 (all tests) can run in parallel
- T034, T041, T043 can run in parallel (form, template, signals - different files)

**Within User Story 2 (Phase 4)**:
- T046-T055 (all tests) can run in parallel
- T056, T061, T063-T064, T067 can run in parallel (form, template, signals)

**Within User Story 3 (Phase 5)**:
- T069-T075 (all tests) can run in parallel
- T076, T082 can run in parallel (form, template)

**Within User Story 4 (Phase 6)**:
- T085-T091 (all tests) can run in parallel
- T092, T098, T100 can run in parallel (form, template, signal)

**Within Polish (Phase 7)**:
- T102-T106, T110-T111, T118 can all run in parallel

**Across User Stories** (if team capacity allows):
- After Foundational complete, User Stories 1 and 2 can start in parallel
- After US2 complete, User Stories 3 and 4 can start in parallel

---

## Parallel Example: User Story 1 (Registration)

```bash
# Terminal 1: Write all tests in parallel (use separate files)
pytest tests/accounts/test_models.py::test_create_user  # Should FAIL
pytest tests/accounts/test_forms.py::TestRegistrationForm  # Should FAIL
pytest tests/accounts/test_views.py::test_registration_view  # Should FAIL

# Terminal 2: Implement form (can work while tests are being written)
# Edit accounts/forms.py - RegistrationForm

# Terminal 3: Implement template (independent of form logic)
# Create templates/accounts/register.html

# Terminal 4: Implement signal (independent of view)
# Create accounts/signals.py - registration_logger

# Sequential after parallel work:
# Edit accounts/views.py - register view (depends on form being done)
# Edit accounts/urls.py - URL routing (depends on view being done)
# Run all tests - should PASS

# Total time saved: ~40% by parallelizing independent tasks
```

---

## Implementation Strategy

### MVP First (Deliver Value Fast)

**Recommended MVP Scope** (Minimum Viable Product):
- Phase 1: Setup
- Phase 2: Foundational 
- Phase 3: User Story 1 (Registration)
- Phase 4: User Story 2 (Login/Logout)
- Basic validation (T107-T109)

**Result**: Users can create accounts and log in - sufficient for Features 002-003 to begin

**Time Estimate**: ~8-12 hours for MVP

### Incremental Delivery

After MVP, deliver remaining features incrementally:

**Increment 2** (Profile Management):
- Phase 5: User Story 3
- Adds user profile viewing/editing

**Increment 3** (Password Security):
- Phase 6: User Story 4  
- Adds password change capability

**Increment 4** (Polish):
- Phase 7: Complete polish and documentation
- Production-ready quality

### Testing Strategy

**TDD Approach** (Constitution Principle III):
1. Write failing test
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Repeat

**Coverage Target**: >80% (enforced in T108)

**Test Types**:
- Unit tests: Models, forms, validators
- Integration tests: Views, URL routing
- E2E tests: Complete user journeys

---

## Total Task Count

- **Setup (Phase 1)**: 14 tasks
- **Foundational (Phase 2)**: 9 tasks
- **User Story 1 (Phase 3)**: 22 tasks (10 tests + 12 implementation)
- **User Story 2 (Phase 4)**: 23 tasks (10 tests + 13 implementation)
- **User Story 3 (Phase 5)**: 16 tasks (7 tests + 9 implementation)
- **User Story 4 (Phase 6)**: 17 tasks (7 tests + 10 implementation)
- **Polish (Phase 7)**: 18 tasks

**Total**: 119 tasks

**MVP Subset**: 48 tasks (Phases 1-4 + basic validation)

---

## Next Steps

1. **Review this task breakdown** with team/stakeholders
2. **Execute Phase 1** (Setup) to initialize project structure
3. **Execute Phase 2** (Foundational) to create core models
4. **Begin User Story 1** (Registration) with TDD approach
5. **Follow `/speckit.implement.prompt.md` instructions** for phase-by-phase execution

**Ready to implement**: All prerequisites met, design complete, tasks defined ✅
