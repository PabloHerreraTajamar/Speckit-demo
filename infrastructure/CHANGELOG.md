# Changelog

All notable changes to the TaskManager Azure Infrastructure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial infrastructure implementation for TaskManager application
- Multi-environment support (dev, staging, production)
- Comprehensive tagging strategy for cost tracking and governance

## [1.0.0] - 2026-01-19

### Added

#### Infrastructure Modules
- **Compute Module**: Azure App Service Plan + App Service
  - Linux-based hosting with Python 3.11 runtime
  - HTTPS-only with TLS 1.2 minimum
  - SystemAssigned managed identity
  - Configurable SKU (B1, B2, S1, P1v2)

- **Database Module**: PostgreSQL Flexible Server
  - PostgreSQL 14 with UTF-8 charset
  - Secure password generation (random_password resource)
  - Azure services firewall rule
  - Configurable SKU (B_Standard_B1ms default)
  - Backup retention: 7 days

- **Storage Module**: Azure Blob Storage
  - LRS replication, Hot access tier
  - Blob versioning enabled
  - 7-day delete retention policy
  - Private blob container for task attachments

- **Monitoring Module**: Application Insights + Log Analytics
  - Web application type monitoring
  - 90-day data retention
  - Automatic integration with App Service
  - Connection string and instrumentation key outputs

#### Environments
- **Development (dev.tfvars)**: B1 SKU, minimal cost (~$60/month)
- **Staging (staging.tfvars)**: B2 SKU, production-like (~$171/month)
- **Production (prod.tfvars.example)**: S1 SKU template (~$142/month)

#### Security Features
- Random password generation for database credentials
- All sensitive outputs marked as `sensitive = true`
- .gitignore configured to exclude `.tfvars` files
- Security checklist (SECURITY_CHECKLIST.md)
- No hardcoded secrets in codebase

#### Outputs
- 16 total outputs covering all infrastructure resources
- Connection strings (PostgreSQL, Storage, Application Insights)
- Resource endpoints and hostnames
- JSON output support for CI/CD integration
- Comprehensive documentation (OUTPUTS.md)

#### Tagging
- Centralized tag management via `locals.common_tags`
- Required tags: project, environment, owner, managed_by
- Optional tag: cost_center
- Tag propagation to all resources
- Tagging strategy documentation (TAGGING_STRATEGY.md)

#### Documentation
- README.md: Complete setup and usage guide
- OUTPUTS.md: Output reference with examples
- SECURITY_CHECKLIST.md: Security best practices
- TAGGING_STRATEGY.md: Tag schema and governance
- CONTRIBUTING.md: Development guidelines
- Multi-environment deployment workflow

#### Testing & Validation
- terraform validate script (tests/terraform/validate.sh)
- terraform plan test script (tests/terraform/plan-test.sh)
- Environment validation across dev, staging, prod
- Automated tag verification

#### Configuration
- Provider configuration: Azure RM v3.80.0, Random v3.5.0
- Backend configuration for Azure Storage (commented template)
- Variable validation (environment, SKUs, naming)
- Location normalization for resource naming

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Skip provider registration flag added due to limited Azure permissions
- All passwords generated using `random_password` resource
- Connection strings marked as sensitive outputs
- TLS 1.2 minimum for all services
- HTTPS-only for App Service

## [0.1.0] - 2026-01-18

### Added
- Initial project structure
- Basic Terraform configuration
- Provider setup (Azure RM)

---

## Version Numbering

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backward-compatible
- **PATCH** (0.0.X): Bug fixes, backward-compatible

## Release Process

1. Update CHANGELOG.md with new version and changes
2. Tag commit: `git tag -a v1.0.0 -m "Release v1.0.0"`
3. Push tag: `git push origin v1.0.0`
4. Create GitHub Release with changelog excerpt
5. Deploy to environments: dev → staging → prod

## Links

- [Repository](https://github.com/org/taskmanager)
- [Issues](https://github.com/org/taskmanager/issues)
- [Terraform Registry](https://registry.terraform.io/providers/hashicorp/azurerm/latest)
