# Contributing to TaskManager Infrastructure

Thank you for contributing to the TaskManager Azure infrastructure! This document provides guidelines and standards for Infrastructure as Code (IaC) development.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Terraform Coding Standards](#terraform-coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Security Guidelines](#security-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Terraform** v1.5.0+ installed
2. **Azure CLI** v2.50.0+ configured
3. **Git** for version control
4. Access to a **development Azure subscription**

### Local Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd taskmanager/infrastructure

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features or modules
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

### Creating a Feature Branch

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/add-redis-cache

# Make changes, test, commit
terraform fmt -recursive
terraform validate
git add .
git commit -m "feat(cache): add Redis cache module"

# Push and create PR
git push origin feature/add-redis-cache
```

## Terraform Coding Standards

### File Organization

```
modules/
  <module-name>/
    ├── main.tf        # Resource definitions
    ├── variables.tf   # Input variables
    ├── outputs.tf     # Output values
    └── README.md      # Module documentation
```

### Naming Conventions

#### Resources

```hcl
# Pattern: <resource_type>_<purpose>
resource "azurerm_resource_group" "main" { }
resource "azurerm_storage_account" "backup" { }
resource "azurerm_app_service_plan" "primary" { }
```

#### Variables

```hcl
# Use snake_case for variable names
variable "resource_group_name" { }
variable "app_service_sku" { }
variable "enable_backup" { }
```

#### Outputs

```hcl
# Descriptive output names
output "storage_connection_string" { }
output "app_service_default_hostname" { }
```

### Code Style

#### Resource Blocks

```hcl
# ✅ GOOD: Descriptive name, proper formatting
resource "azurerm_app_service" "main" {
  name                = "app-${var.environment}-${var.project_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  app_service_plan_id = azurerm_app_service_plan.main.id
  https_only          = true
  
  site_config {
    python_version = "3.11"
  }
  
  tags = var.tags
}

# ❌ BAD: Generic name, poor formatting
resource "azurerm_app_service" "app1" {name="myapp"
location=var.location
resource_group_name=var.resource_group_name}
```

#### Variable Declarations

```hcl
# ✅ GOOD: Description, type, default, validation
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ❌ BAD: No description, no validation
variable "env" {
  type = string
}
```

#### Output Values

```hcl
# ✅ GOOD: Description, sensitive flag when needed
output "database_connection_string" {
  description = "PostgreSQL connection string for Django"
  value       = module.database.connection_string
  sensitive   = true
}

# ❌ BAD: No description, exposed sensitive value
output "db_conn" {
  value = "postgresql://user:pass@host/db"
}
```

### Documentation Requirements

Every module must have a `README.md` with:

```markdown
# Module Name

## Description
Brief description of what the module does.

## Usage

```hcl
module "example" {
  source = "./modules/example"
  
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| resource_group_name | Name of resource group | string | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| resource_id | Resource ID |
```

## Testing Requirements

### Pre-Commit Checks

Before committing, run:

```bash
# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Check formatting
terraform fmt -check -recursive

# Security scan (optional but recommended)
tfsec .
```

### Testing Workflow

1. **Local Validation**:
   ```bash
   cd infrastructure
   terraform init
   terraform validate
   ```

2. **Plan Testing**:
   ```bash
   # Test dev environment
   terraform plan -var-file=environments/dev.tfvars
   
   # Test staging environment
   terraform plan -var-file=environments/staging.tfvars
   ```

3. **Automated Tests**:
   ```bash
   # Run validation script
   ../tests/terraform/validate.sh
   
   # Run plan test for all environments
   ../tests/terraform/plan-test.sh
   ```

### Test Coverage

- [ ] Terraform validate passes
- [ ] Terraform fmt -check passes
- [ ] Plan succeeds for dev environment
- [ ] Plan succeeds for staging environment
- [ ] All outputs are defined
- [ ] No hardcoded secrets
- [ ] Tags applied to all resources

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows Terraform coding standards
- [ ] All tests pass
- [ ] Documentation updated (README, module docs)
- [ ] CHANGELOG.md updated with changes
- [ ] Security checklist reviewed
- [ ] No secrets in code or commit history
- [ ] Terraform plan output reviewed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Breaking change

## Testing
- [ ] terraform validate
- [ ] terraform plan (dev)
- [ ] terraform plan (staging)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No secrets exposed

## Screenshots (if applicable)
terraform plan output or Azure portal screenshots
```

### Review Process

1. **Automated Checks**: CI pipeline runs validation
2. **Peer Review**: At least 1 approval required
3. **Security Review**: For changes to secrets, IAM, networking
4. **Approval**: Team lead approval for production changes

## Security Guidelines

### Secret Management

```hcl
# ✅ GOOD: Use random_password resource
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# ✅ GOOD: Mark sensitive outputs
output "connection_string" {
  value     = "..."
  sensitive = true
}

# ❌ BAD: Hardcoded secrets
variable "db_password" {
  default = "MyPassword123!"
}
```

### Security Checklist

Before committing:

- [ ] No hardcoded passwords
- [ ] No API keys in code
- [ ] Sensitive outputs marked as `sensitive = true`
- [ ] `.tfvars` files in `.gitignore` (except `.example`)
- [ ] TLS/SSL enabled for all services
- [ ] Network security groups configured
- [ ] Managed identities used where possible

### Security Scanning

Run security checks:

```bash
# Install tfsec
brew install tfsec  # macOS
# or
choco install tfsec  # Windows

# Scan infrastructure code
tfsec infrastructure/

# Check for secrets in git history
git secrets --scan
```

## Best Practices

### 1. Use Modules

```hcl
# ✅ GOOD: Reusable module
module "compute" {
  source = "./modules/compute"
  # ...
}

# ❌ BAD: Duplicate resource definitions
resource "azurerm_app_service" "app1" { }
resource "azurerm_app_service" "app2" { }
```

### 2. Use Variables

```hcl
# ✅ GOOD: Parameterized
name = "rg-${var.environment}-${var.project_name}"

# ❌ BAD: Hardcoded
name = "rg-dev-myapp"
```

### 3. Use Data Sources

```hcl
# ✅ GOOD: Reference existing resource
data "azurerm_client_config" "current" {}

# ❌ BAD: Hardcode values
subscription_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### 4. Version Constraints

```hcl
# ✅ GOOD: Pin versions
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80.0"
    }
  }
}

# ❌ BAD: No version constraints
terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }
}
```

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

### Examples

```bash
feat(compute): add auto-scaling configuration

Add auto-scaling rules for App Service Plan based on CPU usage.
Scales between 1-5 instances when CPU > 70%.

Closes #123

---

fix(database): correct PostgreSQL firewall rules

Firewall rules were too restrictive, preventing Azure services access.
Updated to allow connections from Azure internal IPs.

---

docs(readme): update deployment instructions

Add multi-environment deployment workflow section with examples.
```

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a GitHub Issue
- **Security Issues**: Email security@example.com (do not create public issue)
- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs

## License

By contributing, you agree that your contributions will be licensed under the project's license.
