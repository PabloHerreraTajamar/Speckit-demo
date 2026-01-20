# Terraform Output Values Contract

**Version**: 1.0.0  
**Feature**: 004-azure-infrastructure  
**File**: `terraform/outputs.tf`

## Overview

This contract defines all output values exported by Terraform after infrastructure provisioning. These outputs are consumed by:
- Django application (via environment variables)
- CI/CD pipelines (deployment automation)
- Other features (dependency injection)

---

## Output Catalog

### 1. `resource_group_name`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Name of the provisioned Resource Group.

**Example Value**: `"rg-dev-taskmanager-eastus"`

**Terraform Expression**:
```hcl
output "resource_group_name" {
  description = "Name of the Resource Group"
  value       = azurerm_resource_group.main.name
}
```

**Usage**:
- CI/CD: Scope Azure CLI commands to specific RG
- Monitoring: Filter Azure Monitor by resource group

---

### 2. `app_service_name`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Name of the App Service (web app).

**Example Value**: `"app-dev-taskmanager-eastus"`

**Terraform Expression**:
```hcl
output "app_service_name" {
  description = "Name of the App Service"
  value       = azurerm_linux_web_app.main.name
}
```

**Usage**:
- CI/CD: Target for `az webapp deployment` commands
- Django: Self-reference for ALLOWED_HOSTS configuration

---

### 3. `app_service_url`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Public HTTPS URL of the App Service.

**Example Value**: `"https://app-dev-taskmanager-eastus.azurewebsites.net"`

**Terraform Expression**:
```hcl
output "app_service_url" {
  description = "Public URL of the App Service"
  value       = "https://${azurerm_linux_web_app.main.default_hostname}"
}
```

**Usage**:
- End users: Access deployed application
- Testing: Automated E2E test target
- Django: ALLOWED_HOSTS value

---

### 4. `app_service_identity_principal_id`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Managed identity principal ID for the App Service.

**Example Value**: `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`

**Terraform Expression**:
```hcl
output "app_service_identity_principal_id" {
  description = "Managed identity principal ID for Key Vault access"
  value       = azurerm_linux_web_app.main.identity[0].principal_id
}
```

**Usage**:
- Key Vault: Grant access policy to managed identity
- Azure RBAC: Assign roles to App Service identity

---

### 5. `database_fqdn`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Fully Qualified Domain Name of PostgreSQL server.

**Example Value**: `"psql-dev-taskmanager-eastus.postgres.database.azure.com"`

**Terraform Expression**:
```hcl
output "database_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}
```

**Usage**:
- Django: `DATABASE_HOST` environment variable
- Connection string construction

---

### 6. `database_name`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Name of the provisioned database.

**Example Value**: `"taskmanager"`

**Terraform Expression**:
```hcl
output "database_name" {
  description = "PostgreSQL database name"
  value       = azurerm_postgresql_flexible_server_database.main.name
}
```

**Usage**:
- Django: `DATABASE_NAME` environment variable

---

### 7. `database_admin_username`

**Type**: `string`

**Sensitivity**: Sensitive (optional, can be non-sensitive if standardized)

**Description**: Database administrator username.

**Example Value**: `"psqladmin"`

**Terraform Expression**:
```hcl
output "database_admin_username" {
  description = "PostgreSQL administrator username"
  value       = azurerm_postgresql_flexible_server.main.administrator_login
  sensitive   = false  # Username is not highly sensitive
}
```

**Usage**:
- Django: `DATABASE_USER` environment variable

---

### 8. `database_admin_password`

**Type**: `string`

**Sensitivity**: **SENSITIVE** (masked in logs)

**Description**: Database administrator password.

**Example Value**: `"aB3$xY9!mN2@qW7z"` (never logged)

**Terraform Expression**:
```hcl
output "database_admin_password" {
  description = "PostgreSQL administrator password"
  value       = azurerm_postgresql_flexible_server.main.administrator_password
  sensitive   = true
}
```

**Usage**:
- Django: `DATABASE_PASSWORD` environment variable
- **Security Note**: Rotate password via Key Vault in production

**Access**:
```powershell
# View sensitive output (requires explicit flag)
terraform output -raw database_admin_password
```

---

### 9. `database_connection_string`

**Type**: `string`

**Sensitivity**: **SENSITIVE**

**Description**: Complete PostgreSQL connection string.

**Example Value**: `"postgresql://psqladmin:aB3$xY9!mN2@qW7z@psql-dev-taskmanager-eastus.postgres.database.azure.com:5432/taskmanager?sslmode=require"`

**Terraform Expression**:
```hcl
output "database_connection_string" {
  description = "PostgreSQL connection string (Django-compatible)"
  value       = "postgresql://${azurerm_postgresql_flexible_server.main.administrator_login}:${azurerm_postgresql_flexible_server.main.administrator_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${azurerm_postgresql_flexible_server_database.main.name}?sslmode=require"
  sensitive   = true
}
```

**Usage**:
- Django: Alternative to individual DATABASE_* variables
- Quick connection for debugging (not recommended for prod)

---

### 10. `storage_account_name`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Name of the Storage Account.

**Example Value**: `"stdevtaskmgr7a3f"`

**Terraform Expression**:
```hcl
output "storage_account_name" {
  description = "Storage Account name"
  value       = azurerm_storage_account.main.name
}
```

**Usage**:
- Django: `AZURE_STORAGE_ACCOUNT_NAME` environment variable
- File upload SDK configuration

---

### 11. `storage_account_primary_key`

**Type**: `string`

**Sensitivity**: **SENSITIVE**

**Description**: Primary access key for Storage Account.

**Example Value**: `"xY9zAb3$mN2qW7!..."` (64-char base64 string, never logged)

**Terraform Expression**:
```hcl
output "storage_account_primary_key" {
  description = "Storage Account primary access key"
  value       = azurerm_storage_account.main.primary_access_key
  sensitive   = true
}
```

**Usage**:
- Django: `AZURE_STORAGE_ACCOUNT_KEY` environment variable
- **Security Note**: Rotate keys periodically, migrate to managed identity in Phase 2

---

### 12. `storage_account_primary_connection_string`

**Type**: `string`

**Sensitivity**: **SENSITIVE**

**Description**: Complete connection string for Storage Account.

**Example Value**: `"DefaultEndpointsProtocol=https;AccountName=stdevtaskmgr7a3f;AccountKey=xY9zAb3$mN2qW7!...;EndpointSuffix=core.windows.net"`

**Terraform Expression**:
```hcl
output "storage_account_primary_connection_string" {
  description = "Storage Account connection string"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}
```

**Usage**:
- Django: Alternative SDK initialization method
- Azure Storage Explorer connection

---

### 13. `storage_container_name`

**Type**: `string`

**Sensitivity**: Non-sensitive

**Description**: Name of the Blob Storage container for attachments.

**Example Value**: `"task-attachments"`

**Terraform Expression**:
```hcl
output "storage_container_name" {
  description = "Blob Storage container name for task attachments"
  value       = azurerm_storage_container.attachments.name
}
```

**Usage**:
- Django: `AZURE_STORAGE_CONTAINER` environment variable
- File upload destination path

---

### 14. `application_insights_instrumentation_key`

**Type**: `string`

**Sensitivity**: **SENSITIVE** (optional, low-risk but good practice)

**Description**: Application Insights instrumentation key.

**Example Value**: `"12345678-abcd-ef90-1234-567890abcdef"`

**Terraform Expression**:
```hcl
output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}
```

**Usage**:
- Django: `APPINSIGHTS_INSTRUMENTATIONKEY` environment variable
- Telemetry SDK configuration

---

### 15. `application_insights_connection_string`

**Type**: `string`

**Sensitivity**: **SENSITIVE**

**Description**: Application Insights connection string (preferred over instrumentation key).

**Example Value**: `"InstrumentationKey=12345678-abcd-ef90-1234-567890abcdef;IngestionEndpoint=https://eastus-0.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"`

**Terraform Expression**:
```hcl
output "application_insights_connection_string" {
  description = "Application Insights connection string (recommended)"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}
```

**Usage**:
- Django: `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
- Modern Azure Monitor SDK initialization

---

## Output Groups (Logical Organization)

### Group A: Resource Identifiers (Non-Sensitive)
- `resource_group_name`
- `app_service_name`
- `app_service_url`
- `database_name`
- `storage_account_name`
- `storage_container_name`

### Group B: Authentication/Secrets (Sensitive)
- `database_admin_password`
- `database_connection_string`
- `storage_account_primary_key`
- `storage_account_primary_connection_string`
- `application_insights_instrumentation_key`
- `application_insights_connection_string`

### Group C: Identity/Networking
- `app_service_identity_principal_id`
- `database_fqdn`

---

## Consumption Pattern

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
- name: Provision Infrastructure
  run: |
    cd terraform
    terraform init
    terraform apply -var-file=environments/${{ env.ENVIRONMENT }}.tfvars -auto-approve

- name: Set App Service Environment Variables
  run: |
    # Extract outputs
    APP_NAME=$(terraform output -raw app_service_name)
    DB_HOST=$(terraform output -raw database_fqdn)
    DB_PASSWORD=$(terraform output -raw database_admin_password)
    STORAGE_KEY=$(terraform output -raw storage_account_primary_key)
    APPI_CONN=$(terraform output -raw application_insights_connection_string)
    
    # Configure App Service
    az webapp config appsettings set --name $APP_NAME \
      --resource-group $(terraform output -raw resource_group_name) \
      --settings \
        DATABASE_HOST=$DB_HOST \
        DATABASE_PASSWORD=$DB_PASSWORD \
        AZURE_STORAGE_ACCOUNT_KEY=$STORAGE_KEY \
        APPLICATIONINSIGHTS_CONNECTION_STRING=$APPI_CONN
```

### Local Development

```powershell
# terraform/set-env-vars.ps1
$outputs = terraform output -json | ConvertFrom-Json

$env:DATABASE_HOST = $outputs.database_fqdn.value
$env:DATABASE_NAME = $outputs.database_name.value
$env:DATABASE_USER = $outputs.database_admin_username.value
$env:DATABASE_PASSWORD = $outputs.database_admin_password.value
$env:AZURE_STORAGE_ACCOUNT_NAME = $outputs.storage_account_name.value
$env:AZURE_STORAGE_ACCOUNT_KEY = $outputs.storage_account_primary_key.value
$env:AZURE_STORAGE_CONTAINER = $outputs.storage_container_name.value
$env:APPLICATIONINSIGHTS_CONNECTION_STRING = $outputs.application_insights_connection_string.value

Write-Host "Environment variables set from Terraform outputs"
```

---

## Security Best Practices

1. **Sensitive Marking**: All secrets marked `sensitive = true` to prevent console leakage
2. **Output Access**: Use `terraform output -raw <name>` for secure retrieval
3. **State Security**: Remote state file encrypted at rest in Azure Blob Storage
4. **Key Rotation**: Database and storage keys rotated quarterly via automation
5. **Managed Identity**: Phase 2 migration to eliminate access keys entirely

---

## Validation

Outputs are validated in CI/CD:
```hcl
# terraform/tests/outputs_test.go (Terratest)
func TestOutputsExist(t *testing.T) {
    terraformOptions := &terraform.Options{TerraformDir: "../"}
    
    // Verify non-sensitive outputs
    appServiceName := terraform.Output(t, terraformOptions, "app_service_name")
    assert.Contains(t, appServiceName, "app-")
    
    // Verify sensitive outputs exist (without exposing values)
    terraform.OutputRequired(t, terraformOptions, "database_admin_password")
    terraform.OutputRequired(t, terraformOptions, "storage_account_primary_key")
}
```

---

## Versioning

Output contract changes follow Semantic Versioning:
- **Major**: Output removed or type changed (breaking)
- **Minor**: New output added (backward compatible)
- **Patch**: Description or sensitivity flag updated

**Current Version**: 1.0.0 (initial release)

---

## References

- [Terraform Outputs](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Sensitive Output Values](https://developer.hashicorp.com/terraform/language/values/outputs#sensitive-output-values)
- [Azure App Service Configuration](https://learn.microsoft.com/en-us/azure/app-service/configure-common)
- [Django Database Configuration](https://docs.djangoproject.com/en/5.0/ref/settings/#databases)
