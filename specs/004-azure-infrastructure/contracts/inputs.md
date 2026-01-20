# Terraform Input Variables Contract

**Version**: 1.0.0  
**Feature**: 004-azure-infrastructure  
**File**: `terraform/variables.tf`

## Overview

This contract defines all input variables required to provision Azure infrastructure for TaskManager. Variables are supplied via environment-specific `.tfvars` files (`dev.tfvars`, `staging.tfvars`, `prod.tfvars`).

---

## Required Variables

### 1. `environment`

**Type**: `string`

**Description**: Deployment environment identifier. Used for resource naming, tagging, and SKU selection.

**Validation**:
```hcl
validation {
  condition     = contains(["dev", "staging", "prod"], var.environment)
  error_message = "Environment must be one of: dev, staging, prod"
}
```

**Default**: None (must be explicitly provided)

**Examples**:
- `"dev"` - Development environment
- `"staging"` - Pre-production testing
- `"prod"` - Production environment

**Used In**:
- Resource naming: `rg-${var.environment}-taskmanager-eastus`
- Tags: `environment = var.environment`
- Conditional logic: SKU selection, backup retention

---

### 2. `location`

**Type**: `string`

**Description**: Azure region where resources will be deployed.

**Validation**:
```hcl
validation {
  condition     = can(regex("^[A-Za-z ]+$", var.location))
  error_message = "Location must be a valid Azure region name (e.g., 'East US', 'West Europe')"
}
```

**Default**: `"East US"`

**Examples**:
- `"East US"` - Primary region
- `"West Europe"` - European data residency
- `"Southeast Asia"` - APAC deployment

**Used In**:
- All resource `location` attributes
- Resource naming suffix (normalized)
- DR/geo-replication configuration

---

### 3. `project_name`

**Type**: `string`

**Description**: Project identifier for resource naming and tagging.

**Validation**:
```hcl
validation {
  condition     = can(regex("^[a-zA-Z0-9-]{3,20}$", var.project_name))
  error_message = "Project name must be 3-20 alphanumeric characters or hyphens"
}
```

**Default**: `"taskmanager"`

**Examples**:
- `"taskmanager"` - This project
- `"todoapp"` - Alternative project

**Used In**:
- Resource naming: `rg-dev-${var.project_name}-eastus`
- Tags: `project = var.project_name`

---

### 4. `owner`

**Type**: `string`

**Description**: Team or individual responsible for resources (for tagging and cost allocation).

**Default**: `"platform-team"`

**Examples**:
- `"platform-team"` - Infrastructure team
- `"dev-team-a"` - Application development team
- `"john.doe@example.com"` - Individual owner

**Used In**:
- Tags: `owner = var.owner`
- Cost tracking and chargeback

---

## Optional Variables (with Defaults)

### 5. `app_service_sku`

**Type**: `string`

**Description**: App Service Plan SKU tier. Overrides default environment-based selection.

**Default**: Environment-dependent via local:
```hcl
locals {
  default_app_sku = {
    dev     = "B1"
    staging = "B2"
    prod    = "S1"
  }
  app_service_sku = var.app_service_sku != "" ? var.app_service_sku : local.default_app_sku[var.environment]
}
```

**Validation**:
```hcl
validation {
  condition     = can(regex("^(B1|B2|B3|S1|S2|S3|P1v2|P2v2|P3v2)$", var.app_service_sku))
  error_message = "SKU must be one of: B1, B2, B3, S1, S2, S3, P1v2, P2v2, P3v2"
}
```

**Examples**:
- `"B1"` - Basic tier (dev)
- `"S1"` - Standard tier with auto-scale (prod)

**Used In**:
- `azurerm_service_plan.sku_name`

---

### 6. `database_sku`

**Type**: `string`

**Description**: PostgreSQL Flexible Server SKU.

**Default**: Environment-dependent:
```hcl
locals {
  default_db_sku = {
    dev     = "B_Standard_B1ms"       # Burstable, 1 vCore, 2 GB RAM
    staging = "GP_Standard_D2s_v3"    # General Purpose, 2 vCores, 8 GB RAM
    prod    = "GP_Standard_D2s_v3"
  }
  database_sku = var.database_sku != "" ? var.database_sku : local.default_db_sku[var.environment]
}
```

**Examples**:
- `"B_Standard_B1ms"` - Burstable (dev/test)
- `"GP_Standard_D2s_v3"` - General Purpose (prod)

**Used In**:
- `azurerm_postgresql_flexible_server.sku_name`

---

### 7. `database_storage_mb`

**Type**: `number`

**Description**: PostgreSQL database storage in megabytes.

**Default**: `32768` (32 GB)

**Validation**:
```hcl
validation {
  condition     = var.database_storage_mb >= 32768 && var.database_storage_mb <= 16777216
  error_message = "Storage must be between 32 GB and 16 TB (32768-16777216 MB)"
}
```

**Examples**:
- `32768` - 32 GB (minimum)
- `65536` - 64 GB
- `131072` - 128 GB

**Used In**:
- `azurerm_postgresql_flexible_server.storage_mb`

---

### 8. `database_backup_retention_days`

**Type**: `number`

**Description**: Database backup retention period.

**Default**: Environment-dependent:
```hcl
locals {
  default_backup_retention = {
    dev     = 7
    staging = 14
    prod    = 30
  }
  backup_retention = var.database_backup_retention_days != 0 ? var.database_backup_retention_days : local.default_backup_retention[var.environment]
}
```

**Validation**:
```hcl
validation {
  condition     = var.database_backup_retention_days >= 7 && var.database_backup_retention_days <= 35
  error_message = "Backup retention must be between 7 and 35 days"
}
```

**Examples**:
- `7` - Minimum (dev)
- `30` - Recommended (prod)

**Used In**:
- `azurerm_postgresql_flexible_server.backup_retention_days`

---

### 9. `storage_replication_type`

**Type**: `string`

**Description**: Storage Account replication strategy.

**Default**: Environment-dependent:
```hcl
locals {
  default_storage_replication = {
    dev     = "LRS"  # Locally Redundant
    staging = "LRS"
    prod    = "GRS"  # Geo-Redundant
  }
  storage_replication = var.storage_replication_type != "" ? var.storage_replication_type : local.default_storage_replication[var.environment]
}
```

**Validation**:
```hcl
validation {
  condition     = contains(["LRS", "GRS", "RAGRS", "ZRS"], var.storage_replication_type)
  error_message = "Replication type must be one of: LRS, GRS, RAGRS, ZRS"
}
```

**Examples**:
- `"LRS"` - Locally Redundant (dev)
- `"GRS"` - Geo-Redundant (prod)

**Used In**:
- `azurerm_storage_account.account_replication_type`

---

### 10. `enable_application_insights`

**Type**: `bool`

**Description**: Enable Application Insights monitoring.

**Default**: `true`

**Examples**:
- `true` - Enable monitoring (recommended)
- `false` - Disable (cost savings for dev)

**Used In**:
- Conditional resource creation: `count = var.enable_application_insights ? 1 : 0`

---

### 11. `application_insights_retention_days`

**Type**: `number`

**Description**: Log retention period for Application Insights.

**Default**: Environment-dependent:
```hcl
locals {
  default_appi_retention = {
    dev     = 30
    staging = 60
    prod    = 90
  }
  appi_retention = var.application_insights_retention_days != 0 ? var.application_insights_retention_days : local.default_appi_retention[var.environment]
}
```

**Validation**:
```hcl
validation {
  condition     = var.application_insights_retention_days >= 30 && var.application_insights_retention_days <= 730
  error_message = "Retention must be between 30 and 730 days"
}
```

**Examples**:
- `30` - Minimum (dev)
- `90` - Recommended (prod)

**Used In**:
- `azurerm_application_insights.retention_in_days`

---

### 12. `tags`

**Type**: `map(string)`

**Description**: Additional custom tags to apply to all resources.

**Default**: `{}`

**Examples**:
```hcl
tags = {
  cost_center = "engineering"
  compliance  = "gdpr"
  dr_tier     = "gold"
}
```

**Used In**:
- Merged with default tags:
  ```hcl
  local.common_tags = merge(
    {
      project     = var.project_name
      environment = var.environment
      owner       = var.owner
      managed_by  = "terraform"
    },
    var.tags
  )
  ```

---

## Variable File Example

**File**: `terraform/environments/dev.tfvars`

```hcl
# Required
environment  = "dev"
location     = "East US"
project_name = "taskmanager"
owner        = "platform-team"

# Optional (overrides defaults)
app_service_sku                 = "B1"
database_sku                    = "B_Standard_B1ms"
database_storage_mb             = 32768
database_backup_retention_days  = 7
storage_replication_type        = "LRS"
enable_application_insights     = true
application_insights_retention_days = 30

# Custom tags
tags = {
  cost_center = "engineering"
  department  = "platform"
}
```

---

## Validation Strategy

1. **Type Validation**: Terraform enforces variable types (string, number, bool, map)
2. **Constraint Validation**: `validation` blocks enforce business rules (enums, ranges, regex)
3. **Default Logic**: `locals` provide environment-aware defaults
4. **Pre-commit Hook**: `terraform validate` runs on every commit
5. **CI/CD Check**: GitHub Actions runs `terraform plan` on PR to validate inputs

---

## References

- [Terraform Variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Variable Validation](https://developer.hashicorp.com/terraform/language/values/variables#custom-validation-rules)
- [Azure Naming Best Practices](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)
