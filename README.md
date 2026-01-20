# TaskManager

A secure task management application built with Django, deployed on Azure with automated CI/CD.

[![Deploy to Azure](https://github.com/yourusername/taskmanager/actions/workflows/azure-deploy.yml/badge.svg)](https://github.com/yourusername/taskmanager/actions/workflows/azure-deploy.yml)
[![Tests](https://img.shields.io/badge/tests-195%20passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-green)](tests/)

## 🚀 Features

### ✅ Feature 001: User Authentication (Completed)

Complete user authentication system with security best practices:

- **User Registration**: Email-based signup with strong password validation
- **User Login/Logout**: Secure session management with CSRF protection
- **Profile Management**: Update user information (name, email)
- **Password Change**: Secure password updates with current password verification
- **Authentication Logging**: Comprehensive audit trail of all auth events
- **Security Features**:
  - bcrypt password hashing
  - Case-insensitive email lookup
  - Anti-enumeration protection
  - Django messages framework for user feedback
  - CSRF protection on all forms
  - Login required decorators

**Stats**: 119/119 tasks completed | 50 tests passing | 92% code coverage

### ✅ Feature 002: Task CRUD Operations (Completed)

Full task management with filtering, sorting, and pagination:

- **Create Tasks**: Add tasks with title, description, due date, priority
- **View Tasks**: List all user tasks with pagination (20 per page)
- **Update Tasks**: Edit task details and mark as completed
- **Delete Tasks**: Remove tasks with confirmation
- **Filtering**: By status (pending/completed) and priority (high/medium/low)
- **Sorting**: By due date, priority, creation date
- **Task Details**: View complete task information

**Stats**: 99/99 tasks completed | 49 tests passing | 96% code coverage

### ✅ Feature 003: Task File Attachments (Completed)

File attachment system for tasks with Azure Blob Storage integration:

- **File Upload**: Upload files to tasks (max 10MB, max 5 per task)
- **File Download**: Secure download via signed URLs (1-hour expiration)
- **File Deletion**: Remove attachments with cascade cleanup
- **Supported Formats**: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG
- **Security Features**:
  - Ownership validation on all operations
  - File size and type validation
  - MIME type content inspection
  - Filename sanitization
  - Azure Blob Storage with SAS tokens

**Stats**: 81/81 tasks completed | 96 tests passing | Azure Blob Storage integration

### ✅ Feature 004: Azure Infrastructure (Completed)

Production-ready infrastructure deployed on Azure:

- **Azure App Service**: Linux-based web app with Python 3.13
- **PostgreSQL 15**: Flexible Server for production database
- **Blob Storage**: File storage for task attachments
- **Application Insights**: Monitoring and diagnostics
- **CI/CD Pipeline**: Automated deployment with GitHub Actions
- **Security**: HTTPS only, TLS 1.2+, firewall rules

**Stats**: 95/95 tasks completed | Terraform-managed infrastructure

## 🏗️ Tech Stack

### Backend
- **Framework**: Django 5.0.4
- **Language**: Python 3.13
- **Database**: PostgreSQL 15 (Azure Flexible Server)
- **Storage**: Azure Blob Storage
- **Authentication**: Django built-in auth with bcrypt
- **Testing**: pytest 9.0.2, pytest-django, factory-boy
- **Production Server**: Gunicorn 21.2.0
- **Code Quality**: pytest-cov (88% coverage)

### Infrastructure
- **Cloud Provider**: Microsoft Azure
- **Compute**: Azure App Service (Linux, Python 3.13)
- **Database**: PostgreSQL 15 Flexible Server (North Europe)
- **Storage**: Azure Blob Storage (West Europe)
- **Monitoring**: Application Insights + Log Analytics
- **IaC**: Terraform 1.5+
- **CI/CD**: GitHub Actions

## 📋 Quick Start

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git
- Azure subscription (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Spec kit"
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   # Copy from .env.example or create manually
   SECRET_KEY=your-secret-key
   DEBUG=True
   DB_HOST=localhost
   DB_NAME=taskmanager_db
   DB_USER=postgres
   DB_PASSWORD=yourpassword
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Application: http://127.0.0.1:8000
   - Admin interface: http://127.0.0.1:8000/admin

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov --cov-report=term-missing

# Run specific app tests
pytest tests/accounts/ -v
pytest tests/tasks/ -v
pytest tests/attachments/ -v

# Run with quiet mode
pytest -q
```

**Current Status**: 195 tests passing, 3 skipped, 88% coverage

## 🚀 Deployment

### Automated CI/CD

El proyecto incluye pipelines automáticos de GitHub Actions:

1. **Despliegue de Aplicación** (`.github/workflows/azure-deploy.yml`)
   - Trigger: Push a `master` o manual
   - Tests automáticos con pytest
   - Build de la aplicación
   - Despliegue a Azure App Service
   - Ejecución de migraciones

2. **Despliegue de Infraestructura** (`.github/workflows/infrastructure.yml`)
   - Trigger: Manual dispatch
   - Terraform plan/apply/destroy
   - Outputs de recursos creados

### Configuración Rápida

```bash
# 1. Configurar app settings en Azure
.\.github\scripts\configure-app-settings.ps1

# 2. Obtener publish profile para GitHub
bash .github/scripts/get-publish-profile.sh

# 3. Agregar secret AZURE_WEBAPP_PUBLISH_PROFILE en GitHub

# 4. Push a master para desplegar automáticamente
git push origin master
```

Ver [CICD.md](CICD.md) para documentación completa del pipeline.

### Despliegue Manual con Terraform

```bash
cd infrastructure

# Inicializar Terraform
terraform init

# Ver plan de despliegue
terraform plan -var-file=environments/dev.tfvars

# Aplicar infraestructura
terraform apply -var-file=environments/dev.tfvars

# Ver outputs (conexiones, URLs)
terraform output
```

## 📁 Project Structure

```
Spec kit/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   │   ├── azure-deploy.yml       # App deployment
│   │   └── infrastructure.yml     # Terraform deployment
│   └── scripts/             # Deployment helper scripts
├── accounts/                # User authentication app
│   ├── migrations/          # Database migrations
│   ├── models.py            # User & AuthenticationLog models
│   ├── forms.py             # Registration, Login, Profile forms
│   ├── views.py             # Authentication views
│   ├── signals.py           # Auth event logging
│   ├── validators.py        # Custom validators
│   └── admin.py             # Admin interface configuration
├── tasks/                   # Task management app (Feature 002)
│   ├── migrations/          # Database migrations
│   ├── models.py            # Task model
│   ├── forms.py             # Task form
│   ├── views.py             # CRUD views
│   ├── managers.py          # Custom querysets
│   └── validators.py        # Task validators
├── attachments/             # File attachment app (Feature 003)
│   ├── migrations/          # Database migrations
│   ├── models.py            # Attachment model
│   ├── forms.py             # File upload form
│   ├── views.py             # Upload, download, delete views
│   ├── storage.py           # Azure Blob Storage backend
│   ├── validators.py        # File validation
│   └── signals.py           # Cascade deletion
├── infrastructure/           # Terraform IaC
│   ├── main.tf             # Root module orchestration
│   ├── variables.tf        # Input variables
│   ├── outputs.tf          # Output values
│   ├── providers.tf        # Azure provider config
│   ├── locals.tf           # Local values
│   ├── backend.tf          # State backend config
│   ├── environments/       # Environment-specific configs
│   │   ├── dev.tfvars
│   │   └── prod.tfvars.example
│   └── modules/            # Reusable modules
│       ├── compute/        # App Service
│       ├── database/       # PostgreSQL
│       ├── storage/        # Blob Storage
│       └── monitoring/     # Application Insights
├── taskmanager/            # Django project settings
│   └── settings/
│       ├── base.py         # Shared settings
│       ├── development.py  # Local development
│       ├── testing.py      # Test configuration
│       └── production.py   # Production settings
├── startup.sh              # Azure App Service startup script
├── .deployment             # Azure deployment config
├── manage.py               # Django management script
├── pytest.ini              # pytest configuration
├── requirements.txt        # Python dependencies
├── CICD.md                 # CI/CD documentation
└── .gitignore              # Git ignore rules
```

## 🔗 Available URLs

### Authentication (Feature 001)
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/profile/` - User profile management
- `/accounts/profile/password/` - Password change

### Tasks (Feature 002)
- `/tasks/` - List all user tasks
- `/tasks/create/` - Create new task
- `/tasks/<id>/` - View task details
- `/tasks/<id>/update/` - Update task
- `/tasks/<id>/delete/` - Delete task

### Attachments (Feature 003)
- `/tasks/<task_id>/attachments/upload/` - Upload file to task
- `/tasks/<task_id>/attachments/` - List task attachments
- `/attachments/<id>/download/` - Download attachment (signed URL)
- `/attachments/<id>/delete/` - Delete attachment

### Admin
- `/admin/` - Django admin interface (superuser only)

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# Django Core
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_HOST=your-postgres-host.postgres.database.azure.com
DB_NAME=taskmanager_db
DB_USER=taskadmin
DB_PASSWORD=your-db-password

# Azure Storage (Feature 003)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccountname;AccountKey=yourkey;EndpointSuffix=core.windows.net

# Application Insights (Monitoring)
APPINSIGHTS_INSTRUMENTATION_KEY=your-instrumentation-key
APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string

# Admin User (for startup.sh)
ADMIN_EMAIL=admin@taskmanager.com
ADMIN_PASSWORD=secure-password-here
```
AZURE_STORAGE_CONTAINER_NAME=taskmanager-attachments-prod
## 🔄 Development Workflow

### Git Branch Strategy
- `master` - Production-ready code
- `001-user-authentication` - Feature 001 (Merged ✅)
- `002-task-crud` - Feature 002 (Merged ✅)
- `003-task-attachments` - Feature 003 (Merged ✅)
- `004-azure-infrastructure` - Feature 004 (Merged ✅)

### Commit Convention
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Test additions/updates
- `refactor:` - Code refactoring
- `docs:` - Documentation updates
- `chore:` - Maintenance tasks

## 🧪 Testing Strategy

- **TDD Approach**: Tests written before implementation
- **Coverage**: 88% overall (195 tests passing)
  - accounts: 92% coverage (50 tests)
  - tasks: 96% coverage (49 tests)
  - attachments: 90% coverage (96 tests)
- **Test Types**:
  - Unit tests for models, forms, validators
  - Integration tests for views
  - End-to-end tests for complete user flows
  - Mocked Azure Blob Storage for isolation

## 🔒 Security Features

### Implemented ✅
- bcrypt password hashing (Django default)
- CSRF protection on all forms
- @login_required decorators on protected views
- Authentication event logging (AuthenticationLog model)
- Anti-enumeration on login/registration
- Strong password validation (8+ chars, alphanumeric)
- Case-insensitive email handling
- File upload validation (size, type, MIME)
- Azure Blob Storage with SAS tokens (1-hour expiration)
- HTTPS enforcement (production only)
- Session security settings (production only)
- Secure SSL redirect in production
- HSTS headers (1 year)
- Secure cookie flags

### Database Security
- PostgreSQL with SSL connection
- Firewall rules limiting IP access
- Strong password requirements
- Separate admin user

## 📊 Monitoring & Observability

- **Application Insights**: Request tracking, exceptions, performance
- **Log Analytics**: Centralized logging
- **Availability Tests**: Uptime monitoring
- **Custom Metrics**: Business KPIs

## 🤝 Contributing

1. Create a feature branch from `master`
2. Follow TDD approach (write tests first)
3. Ensure all tests pass: `pytest`
4. Run with coverage: `pytest --cov`
5. Create a pull request to `master`

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/taskmanager/issues)
- Documentation: See [CICD.md](CICD.md) for deployment guide

---

**Project Status**: ✅ All features complete and deployed to Azure

**Stats Summary**:
- 4/4 features complete (394/394 tasks)
- 195 tests passing, 88% coverage
- Infrastructure deployed on Azure
- CI/CD pipeline configured and ready

**Live URLs**:
- Production: `https://app-dev-taskmanager-northeurope.azurewebsites.net`
- Application Insights: Azure Portal → taskmanager-appinsights-dev
