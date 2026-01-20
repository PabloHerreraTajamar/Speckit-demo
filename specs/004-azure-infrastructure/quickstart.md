# Quickstart: Azure Infrastructure Provisioning

**Feature**: 004-azure-infrastructure  
**Branch**: `004-azure-infrastructure`  
**Estimated Time**: 15 minutes (first run), 5 minutes (subsequent)

## Prerequisites

Before provisioning infrastructure, ensure you have:

### 1. Required Tools

```powershell
# Check Terraform version (must be 1.6.0+)
terraform version

# Check Azure CLI (must be 2.50.0+)
az version

# Check Git
git --version
```

**Install if missing**:
- [Terraform](https://developer.hashicorp.com/terraform/downloads) (1.6.0+)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (2.50.0+)
- [Git](https://git-scm.com/downloads)

---

### 2. Azure Access

```powershell
# Login to Azure
az login

# Set active subscription (if you have multiple)
az account set --subscription "<your-subscription-id>"

# Verify current context
az account show
```

**Required Permissions**:
- **Contributor** role on the subscription (to create Resource Groups and resources)
- **User Access Administrator** role (to assign managed identities, optional for MVP)

---

### 3. State Storage Preparation (One-Time Setup)

Terraform state must be stored in Azure Blob Storage for team collaboration.

```powershell
# Variables
$LOCATION = "East US"
$STATE_RG = "rg-terraform-state"
$STATE_STORAGE = "tfstate$(Get-Random -Minimum 1000 -Maximum 9999)"
$STATE_CONTAINER = "terraform-state"

# Create Resource Group for state
az group create --name $STATE_RG --location $LOCATION

# Create Storage Account for state
az storage account create `
  --name $STATE_STORAGE `
  --resource-group $STATE_RG `
  --location $LOCATION `
  --sku Standard_LRS `
  --encryption-services blob `
  --https-only true `
  --min-tls-version TLS1_2

# Create Blob Container
az storage container create `
  --name $STATE_CONTAINER `
  --account-name $STATE_STORAGE `
  --auth-mode login

Write-Host "State storage created: $STATE_STORAGE" -ForegroundColor Green
```

**⚠️ IMPORTANT**: Save `$STATE_STORAGE` value - you'll need it in step 4.

---

## Step 1: Clone Repository & Checkout Branch

```powershell
# Clone (if not already cloned)
git clone <repository-url>
cd taskmanager

# Checkout infrastructure branch
git checkout 004-azure-infrastructure

# Navigate to Terraform directory
cd terraform
```

---

## Step 2: Configure Backend

Edit `backend.tf` with your state storage account name from Prerequisites step 3:

**File**: `terraform/backend.tf`

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstateXXXX"  # <-- Replace XXXX with your value
    container_name       = "terraform-state"
    key                  = "taskmanager-dev.tfstate"
    use_azuread_auth     = true
  }
}
```

**Alternative**: Use environment-specific backend config files (recommended for CI/CD):

**File**: `terraform/backend-config/dev.tfbackend`

```hcl
resource_group_name  = "rg-terraform-state"
storage_account_name = "tfstateXXXX"
container_name       = "terraform-state"
key                  = "taskmanager-dev.tfstate"
use_azuread_auth     = true
```

Then initialize with:
```powershell
terraform init -backend-config=backend-config/dev.tfbackend
```

---

## Step 3: Initialize Terraform

```powershell
# Initialize Terraform (downloads providers, configures backend)
terraform init

# Expected output:
# Terraform has been successfully initialized!
```

**Troubleshooting**:
- **Error: "access denied to state blob"** → Run `az login` again, ensure you have Storage Blob Data Contributor role
- **Error: "invalid backend configuration"** → Verify `storage_account_name` in `backend.tf` matches your state storage

---

## Step 4: Configure Environment Variables

Choose your target environment and configure variables:

### Option A: Development Environment (Quick Start)

**File**: `terraform/environments/dev.tfvars`

```hcl
# Required
environment  = "dev"
location     = "East US"
project_name = "taskmanager"
owner        = "your-team-name"  # <-- CHANGE THIS

# Optional (uses defaults if omitted)
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

### Option B: Production Environment

**File**: `terraform/environments/prod.tfvars`

```hcl
# Required
environment  = "prod"
location     = "East US"
project_name = "taskmanager"
owner        = "platform-team"

# Production-grade settings
app_service_sku                 = "S1"
database_sku                    = "GP_Standard_D2s_v3"
database_storage_mb             = 65536
database_backup_retention_days  = 30
storage_replication_type        = "GRS"
enable_application_insights     = true
application_insights_retention_days = 90

tags = {
  cost_center = "engineering"
  compliance  = "gdpr"
  sla         = "99.9"
}
```

---

## Step 5: Plan Infrastructure Changes

Preview what Terraform will create:

```powershell
# Development
terraform plan -var-file=environments/dev.tfvars -out=tfplan

# Production
terraform plan -var-file=environments/prod.tfvars -out=tfplan
```

**Review the output**:
- ✅ `Plan: X to add, 0 to change, 0 to destroy` (first run)
- ✅ Resource names match convention: `rg-dev-taskmanager-eastus`, `app-dev-taskmanager-eastus`
- ✅ All resources tagged with `environment`, `project`, `owner`

---

## Step 6: Apply Infrastructure

Provision the resources:

```powershell
# Apply the plan
terraform apply tfplan

# Or combine plan and apply (auto-approve for automation)
terraform apply -var-file=environments/dev.tfvars -auto-approve
```

**Expected Timeline**:
1. Resource Group creation: ~10 seconds
2. Storage Account creation: ~30 seconds
3. App Service Plan creation: ~30 seconds
4. **PostgreSQL Flexible Server: ~5-7 minutes** (longest step)
5. App Service creation: ~1 minute
6. Application Insights: ~20 seconds

**Total**: ~8-10 minutes for first run

---

## Step 7: Verify Outputs

After successful apply, Terraform outputs connection details:

```powershell
# List all outputs
terraform output

# Example output:
# app_service_name = "app-dev-taskmanager-eastus"
# app_service_url = "https://app-dev-taskmanager-eastus.azurewebsites.net"
# database_fqdn = "psql-dev-taskmanager-eastus.postgres.database.azure.com"
# storage_account_name = "stdevtaskmgr7a3f"
```

**Get specific output**:
```powershell
# Non-sensitive
terraform output app_service_url

# Sensitive (requires -raw flag)
terraform output -raw database_admin_password
terraform output -raw storage_account_primary_key
```

---

## Step 8: Configure Application

Export Terraform outputs as environment variables for local Django development:

**PowerShell Script**: `terraform/set-env-vars.ps1`

```powershell
# Load Terraform outputs into environment
$outputs = terraform output -json | ConvertFrom-Json

# Database
$env:DATABASE_HOST = $outputs.database_fqdn.value
$env:DATABASE_NAME = $outputs.database_name.value
$env:DATABASE_USER = $outputs.database_admin_username.value
$env:DATABASE_PASSWORD = $outputs.database_admin_password.value
$env:DATABASE_PORT = "5432"
$env:DATABASE_SSLMODE = "require"

# Storage
$env:AZURE_STORAGE_ACCOUNT_NAME = $outputs.storage_account_name.value
$env:AZURE_STORAGE_ACCOUNT_KEY = $outputs.storage_account_primary_key.value
$env:AZURE_STORAGE_CONTAINER = $outputs.storage_container_name.value

# Monitoring
$env:APPLICATIONINSIGHTS_CONNECTION_STRING = $outputs.application_insights_connection_string.value

# Application
$env:ALLOWED_HOSTS = $outputs.app_service_url.value -replace 'https://', ''
$env:DJANGO_SETTINGS_MODULE = "taskmanager.settings.production"

Write-Host "✅ Environment variables configured" -ForegroundColor Green
Write-Host "App URL: $($outputs.app_service_url.value)" -ForegroundColor Cyan
```

**Run**:
```powershell
cd terraform
.\set-env-vars.ps1
```

---

## Step 9: Verify Infrastructure in Azure Portal

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to Resource Groups → `rg-dev-taskmanager-eastus`
3. Verify resources:
   - ✅ App Service Plan (`asp-dev-taskmanager-eastus`)
   - ✅ App Service (`app-dev-taskmanager-eastus`)
   - ✅ PostgreSQL Flexible Server (`psql-dev-taskmanager-eastus`)
   - ✅ Storage Account (`stdevtaskmgrXXXX`)
   - ✅ Application Insights (`appi-dev-taskmanager-eastus`)
4. Check resource tags: `environment=dev`, `project=taskmanager`, `managed_by=terraform`

---

## Step 10: Test Connectivity

### Database Connection Test

```powershell
# Using psql CLI (install from https://www.postgresql.org/download/)
$DB_HOST = terraform output -raw database_fqdn
$DB_USER = terraform output -raw database_admin_username
$DB_PASS = terraform output -raw database_admin_password
$DB_NAME = terraform output -raw database_name

psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER password=$DB_PASS sslmode=require"

# If successful, you'll see PostgreSQL prompt:
# psql (15.x)
# SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256)
# Type "help" for help.
# taskmanager=>
```

### Storage Access Test

```powershell
# Using Azure CLI
$STORAGE_ACCOUNT = terraform output -raw storage_account_name
$STORAGE_KEY = terraform output -raw storage_account_primary_key

# List containers
az storage container list --account-name $STORAGE_ACCOUNT --account-key $STORAGE_KEY --output table

# Expected output:
# Name               Lease Status    Last Modified
# -----------------  --------------  -------------------------
# task-attachments   unlocked        2026-01-19T10:30:00+00:00
```

### App Service Health Check

```powershell
$APP_URL = terraform output -raw app_service_url

# Check App Service is running (returns 404 until Django is deployed, but proves service is up)
Invoke-WebRequest -Uri $APP_URL -Method HEAD

# Expected: HTTP 404 (no app deployed yet) or 503 (app service initializing)
# Not expected: Timeout or connection refused
```

---

## Common Operations

### Update Infrastructure

When changing Terraform configuration:

```powershell
# Re-run plan to see changes
terraform plan -var-file=environments/dev.tfvars

# Apply changes
terraform apply -var-file=environments/dev.tfvars
```

### Deploy to Another Environment

```powershell
# Staging
terraform plan -var-file=environments/staging.tfvars -out=tfplan-staging
terraform apply tfplan-staging

# Production (requires manual approval in CI/CD)
terraform plan -var-file=environments/prod.tfvars -out=tfplan-prod
terraform apply tfplan-prod
```

### Destroy Infrastructure (Cleanup)

```powershell
# Development (careful!)
terraform destroy -var-file=environments/dev.tfvars

# Confirm by typing "yes" when prompted
```

**⚠️ WARNING**: Destroy is irreversible. Database data will be lost unless backups exist.

---

## Troubleshooting

### Issue: "Resource group already exists"

**Cause**: Previous deployment not cleaned up

**Solution**:
```powershell
# Import existing resource group into state
terraform import azurerm_resource_group.main /subscriptions/<subscription-id>/resourceGroups/rg-dev-taskmanager-eastus

# Then apply
terraform apply -var-file=environments/dev.tfvars
```

### Issue: "Database provisioning timeout"

**Cause**: PostgreSQL Flexible Server can take 5-10 minutes

**Solution**: Wait for provisioning to complete. Check Azure Portal → Resource Group → Deployments for progress.

### Issue: "Insufficient quota for App Service Plan"

**Cause**: Azure subscription quota limit

**Solution**:
```powershell
# Check current quota
az vm list-usage --location "East US" --output table

# Request quota increase via Azure Portal → Subscriptions → Usage + quotas
```

### Issue: "Storage account name already taken"

**Cause**: Storage account names are globally unique

**Solution**: Terraform uses random suffix by default. If using custom name in `main.tf`, change it:
```hcl
resource "random_string" "storage_suffix" {
  length  = 4
  special = false
  upper   = false
}

locals {
  storage_account_name = "st${var.environment}${var.project_name}${random_string.storage_suffix.result}"
}
```

---

## Next Steps

After infrastructure is provisioned:

1. **Deploy Django Application**: Feature 001 (User Authentication) will deploy code to App Service
2. **Run Migrations**: Django database migrations will create tables in PostgreSQL
3. **Configure CI/CD**: GitHub Actions will use these Terraform outputs for automated deployments
4. **Enable Monitoring**: Application Insights will collect telemetry from deployed app

---

## Cost Monitoring

Track infrastructure costs:

```powershell
# View cost analysis for Resource Group
az consumption usage list --start-date 2026-01-01 --end-date 2026-01-31 | ConvertFrom-Json | Where-Object { $_.resourceGroup -eq "rg-dev-taskmanager-eastus" }
```

**Expected Monthly Costs** (East US):
- **Development**: ~€60/month (B1 App Service + B1ms PostgreSQL)
- **Staging**: ~€171/month (B2 App Service + GP D2s_v3 PostgreSQL)
- **Production**: ~€142/month (S1 App Service + GP D2s_v3 PostgreSQL)

---

## References

- [Terraform Azure Provider Docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/)
- [PostgreSQL Flexible Server Documentation](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/)
- [Azure Storage Documentation](https://learn.microsoft.com/en-us/azure/storage/)
- [Application Insights Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
