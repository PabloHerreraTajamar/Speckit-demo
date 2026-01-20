# Terraform Contracts

This directory defines the **inputs** and **outputs** for the Terraform infrastructure configuration, serving as the contract between infrastructure provisioning and application deployment.

## Purpose

Terraform contracts ensure that:
1. **Inputs** are validated and documented (what infrastructure needs to be configured)
2. **Outputs** are predictable and consumable (what infrastructure provides to the application)
3. **Interfaces** are stable across environments (dev/staging/prod use same contract)

---

## Contract Files

### 1. [inputs.md](inputs.md)
Defines all Terraform input variables, their types, validation rules, and default values.

**Corresponds to**: `terraform/variables.tf`

**Purpose**: Documents what parameters must be provided when provisioning infrastructure (e.g., environment, region, SKU tiers).

---

### 2. [outputs.md](outputs.md)
Defines all Terraform output values that downstream consumers need.

**Corresponds to**: `terraform/outputs.tf`

**Purpose**: Documents what connection strings, URLs, and identifiers are exported for application configuration.

**Consumers**:
- Django application (via environment variables)
- CI/CD pipelines (for deployment automation)
- Other features (Feature 001, 002, 003 depend on these outputs)

---

## Contract Guarantees

### Stability
- Input variable names and types MUST NOT change without major version bump
- Output value formats MUST remain consistent across environments
- Breaking changes require migration guide

### Validation
- All inputs have validation rules (regex, enums, ranges)
- All outputs are tested in `terraform plan` review
- Contract conformance checked in CI/CD

### Documentation
- Every input has description and example
- Every output has description and usage notes
- Sensitive outputs clearly marked

---

## Usage Example

**Infrastructure Provisioning**:
```powershell
# Developer provides inputs via tfvars file
terraform apply -var-file=environments/dev.tfvars

# Terraform validates inputs against contract (inputs.md)
# Terraform provisions resources
# Terraform exports outputs defined in contract (outputs.md)
```

**Application Configuration**:
```python
# Django reads outputs via environment variables
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DATABASE_HOST'),        # From Terraform output
        'NAME': os.getenv('DATABASE_NAME'),        # From Terraform output
        'USER': os.getenv('DATABASE_USER'),        # From Terraform output
        'PASSWORD': os.getenv('DATABASE_PASSWORD'), # From Terraform output
        'PORT': '5432',
    }
}
```

---

## Versioning

Contracts follow Semantic Versioning:
- **Major**: Breaking changes (input/output removed or type changed)
- **Minor**: New inputs/outputs added (backward compatible)
- **Patch**: Documentation or validation rule updates

**Current Version**: 1.0.0 (initial contract for Feature 004)

---

## References

- [Terraform Input Variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Terraform Output Values](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Azure Naming Conventions](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)
