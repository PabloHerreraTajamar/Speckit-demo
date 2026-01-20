# TaskManager Azure Infrastructure

Terraform infrastructure as code for deploying TaskManager application to Azure.

## Prerequisites

### Required Tools

- **Terraform**: v1.5.0 or higher
  - Install: https://developer.hashicorp.com/terraform/downloads
  - Verify: `terraform version`

- **Azure CLI**: v2.50.0 or higher
  - Install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
  - Verify: `az version`

- **Azure Subscription**:
  - Active Azure subscription with Contributor role
  - Login: `az login`
  - Verify: `az account show`

### Azure Permissions

Your account or service principal must have:
- **Contributor** role on the target subscription
- Ability to create resource groups and resources
- Ability to assign managed identities (if using)

## Project Structure

```
infrastructure/
├── main.tf              # Root configuration, orchestrates modules
├── variables.tf         # Input variable declarations
├── outputs.tf           # Output definitions
├── providers.tf         # Azure RM provider configuration
├── backend.tf           # Terraform state backend (Azure Storage)
├── locals.tf            # Local values and common tags
├── environments/        # Environment-specific variable files
│   ├── dev.tfvars
│   ├── staging.tfvars
│   └── prod.tfvars.example
├── modules/             # Reusable Terraform modules
│   ├── compute/         # App Service Plan + App Service
│   ├── database/        # PostgreSQL Flexible Server
│   ├── storage/         # Storage Account + Blob Container
│   └── monitoring/      # Application Insights
└── tests/               # Validation scripts
    └── terraform/
        ├── validate.sh
        └── plan-test.sh
```

## Quick Start

### 1. Configure Azure Backend (One-time setup)

Before first use, create an Azure Storage Account for Terraform state:

```bash
# Set variables
RESOURCE_GROUP="terraform-state-rg"
STORAGE_ACCOUNT="tfstate$(openssl rand -hex 4)"  # Generates unique name
CONTAINER_NAME="tfstate"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --encryption-services blob

# Create blob container
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT
```

Update `backend.tf` with your storage account name.

### 2. Initialize Terraform

```bash
cd infrastructure
terraform init
```

### 3. Create Environment Configuration

Copy the example file and customize:

```bash
cp environments/dev.tfvars.example environments/dev.tfvars
# Edit dev.tfvars with your values
```

### 4. Plan Deployment

Preview changes before applying:

```bash
terraform plan -var-file=environments/dev.tfvars
```

### 5. Deploy Infrastructure

```bash
terraform apply -var-file=environments/dev.tfvars
```

### 6. View Outputs

After successful deployment:

```bash
terraform output
terraform output -json  # For CI/CD integration
```

## Environment Management

### Overview

This infrastructure supports three environments with isolated resources:

- **Development (dev)**: Local testing, B1 SKU, minimal cost
- **Staging (staging)**: Pre-production testing, B2 SKU, production-like
- **Production (prod)**: Live application, S1+ SKU, high availability

Each environment deploys to a separate Azure Resource Group with environment-specific naming:
- `rg-dev-taskmanager-eastus`
- `rg-staging-taskmanager-eastus`
- `rg-prod-taskmanager-eastus`

### Multi-Environment Deployment Workflow

#### 1. Deploy Development Environment

```bash
cd infrastructure

# Initialize (first time only)
terraform init

# Plan changes
terraform plan -var-file=environments/dev.tfvars

# Apply infrastructure
terraform apply -var-file=environments/dev.tfvars

# Verify deployment
terraform output app_service_url
```

#### 2. Deploy Staging Environment

```bash
# Plan staging (validates against dev code)
terraform plan -var-file=environments/staging.tfvars

# Apply to staging
terraform apply -var-file=environments/staging.tfvars

# Compare outputs with dev
diff <(terraform output -json | jq -S .) \
     <(terraform output -json | jq -S . | sed 's/dev/staging/g')
```

#### 3. Deploy Production Environment

**Prerequisites**:
- Staging deployment validated
- Change approval obtained
- Backup plan prepared

```bash
# Create prod.tfvars from template (first time only)
cp environments/prod.tfvars.example environments/prod.tfvars
# Edit prod.tfvars with production values (DO NOT COMMIT)

# Plan production changes
terraform plan -var-file=environments/prod.tfvars

# Review plan carefully - verify SKUs, regions, tags
# Get approval from team lead

# Apply to production
terraform apply -var-file=environments/prod.tfvars

# Verify critical outputs
terraform output app_service_url
terraform output postgresql_server_fqdn
```

### Environment Isolation Best Practices

1. **Separate State Files**: Use different backends or workspaces per environment
2. **Different Subscriptions**: Consider separate Azure subscriptions for prod
3. **Resource Naming**: Environment prefix ensures no collisions
4. **Tag Everything**: Environment tag enables cost tracking
5. **Access Control**: Restrict production deployments to CI/CD pipeline

### Using Terraform Workspaces (Alternative)

If using workspaces for environment isolation:

```bash
# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch and deploy
terraform workspace select dev
terraform apply -var-file=environments/dev.tfvars

terraform workspace select staging
terraform apply -var-file=environments/staging.tfvars

terraform workspace select prod
terraform apply -var-file=environments/prod.tfvars
```

### Environment Comparison

| Feature | Dev | Staging | Production |
|---------|-----|---------|------------|
| App Service SKU | B1 | B2 | S1 or P1v2 |
| Database SKU | B_Standard_B1ms | B_Standard_B2s | GP_Standard_D2s_v3 |
| Monthly Cost | ~$60 USD | ~$171 USD | ~$142 USD+ |
| Auto-scale | No | No | Optional |
| Backup Retention | 7 days | 7 days | 30 days |
| High Availability | No | No | Recommended |
| Access | Team | Team + QA | Restricted |

### Promoting Changes Across Environments

**Recommended Flow**: Dev → Staging → Production

```bash
# 1. Develop and test in dev
terraform apply -var-file=environments/dev.tfvars

# 2. Validate changes
terraform output
# Test application functionality

# 3. Promote to staging
terraform plan -var-file=environments/staging.tfvars
terraform apply -var-file=environments/staging.tfvars

# 4. Staging validation
# Run integration tests
# Performance testing
# Security scanning

# 5. Production deployment (with approval)
terraform plan -var-file=environments/prod.tfvars
# Review plan, get approval
terraform apply -var-file=environments/prod.tfvars

# 6. Post-deployment verification
terraform output app_service_url
# Smoke tests
# Monitor Application Insights
```

### Automated Environment Testing

Use the provided test script to validate all environments:

```bash
# Test all environments
../tests/terraform/plan-test.sh

# Test specific environment
../tests/terraform/plan-test.sh staging

# Expected output:
# ✅ dev: Plan succeeded
# ✅ staging: Plan succeeded
# ⚠️  prod: prod.tfvars not found (expected if using .example)
```

## Common Operations

### Format Code

```bash
terraform fmt -recursive
```

### Validate Configuration

```bash
terraform validate
```

### Refresh State

```bash
terraform refresh -var-file=environments/dev.tfvars
```

### Destroy Infrastructure

⚠️ **WARNING**: This will delete all resources!

```bash
terraform destroy -var-file=environments/dev.tfvars
```

## Configuration Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `project_name` | Project identifier | `taskmanager` |
| `environment` | Environment name | `dev`, `staging`, `prod` |
| `location` | Azure region | `eastus` |
| `db_admin_password` | Database admin password | (sensitive) |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `app_service_sku` | App Service Plan SKU | `B1` |
| `database_sku` | PostgreSQL server SKU | `B_Standard_B1ms` |
| `owner` | Resource owner tag | `platform-team` |

See `variables.tf` for complete list and descriptions.

## Outputs

After deployment, the following outputs are available:

| Output | Description | Sensitive |
|--------|-------------|-----------|
| `app_service_url` | Application URL | No |
| `app_service_name` | App Service name | No |
| `database_connection_string` | PostgreSQL connection string | Yes |
| `storage_connection_string` | Storage account connection string | Yes |
| `storage_blob_endpoint` | Blob storage endpoint | No |
| `application_insights_instrumentation_key` | App Insights key | No |
| `application_insights_connection_string` | App Insights connection string | Yes |

View sensitive outputs with:

```bash
terraform output database_connection_string
terraform output -raw storage_connection_string
```

## Disaster Recovery

### Terraform State Backup

Terraform state files contain the mapping between your infrastructure and Terraform configuration. Losing state can make infrastructure management difficult.

#### Backup Strategy

**Automated Backups** (Azure Storage Backend):

Azure Storage automatically provides:
- Soft delete (7-day retention)
- Versioning (multiple state file versions)
- Geo-redundant storage (optional)

**Manual Backups**:

```bash
# Before major changes, backup state
terraform state pull > backup-$(date +%Y%m%d-%H%M%S).tfstate

# Store backup securely
az storage blob upload \
  --account-name <storage-account> \
  --container-name tfstate-backups \
  --name backup-$(date +%Y%m%d).tfstate \
  --file backup-*.tfstate
```

#### State Recovery

**Scenario 1: Corrupted State File**

```bash
# List state file versions in Azure Storage
az storage blob list \
  --account-name <storage-account> \
  --container-name tfstate \
  --prefix terraform.tfstate

# Download previous version
az storage blob download \
  --account-name <storage-account> \
  --container-name tfstate \
  --name terraform.tfstate \
  --version-id <version-id> \
  --file terraform.tfstate.backup

# Restore state
terraform state push terraform.tfstate.backup
```

**Scenario 2: Accidentally Deleted State**

```bash
# Recover from soft delete (within 7 days)
az storage blob undelete \
  --account-name <storage-account> \
  --container-name tfstate \
  --name terraform.tfstate

# Verify state
terraform state list
```

**Scenario 3: State File Lost (No Backup)**

```bash
# Import existing resources into new state
terraform import azurerm_resource_group.main /subscriptions/{id}/resourceGroups/rg-dev-taskmanager-eastus
terraform import module.compute.azurerm_service_plan.main /subscriptions/{id}/resourceGroups/{rg}/providers/Microsoft.Web/serverfarms/{name}
terraform import module.compute.azurerm_linux_web_app.main /subscriptions/{id}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{name}

# Continue importing all resources...
# Then run terraform plan to verify
```

### Infrastructure Recovery

#### Complete Environment Rebuild

If infrastructure is accidentally destroyed:

```bash
# 1. Ensure state file is intact
terraform state list

# 2. Review plan
terraform plan -var-file=environments/prod.tfvars

# 3. Re-create infrastructure
terraform apply -var-file=environments/prod.tfvars

# 4. Verify outputs
terraform output

# 5. Restore application data
# - Database: Restore from automated backup
# - Storage: Blobs are retained per retention policy
```

#### Database Recovery

PostgreSQL Flexible Server provides automated backups:

```bash
# List available backups
az postgres flexible-server backup list \
  --resource-group rg-prod-taskmanager-eastus \
  --name psql-prod-taskmanager-eastus

# Restore to point in time
az postgres flexible-server restore \
  --resource-group rg-prod-taskmanager-eastus \
  --name psql-prod-taskmanager-restored \
  --source-server psql-prod-taskmanager-eastus \
  --restore-time "2026-01-19T14:30:00Z"
```

#### Storage Account Recovery

Blob soft delete retains deleted blobs for 7 days:

```bash
# List deleted blobs
az storage blob list \
  --account-name stprodtaskmanagereastus \
  --container-name task-attachments \
  --include d

# Undelete blob
az storage blob undelete \
  --account-name stprodtaskmanagereastus \
  --container-name task-attachments \
  --name <blob-name>
```

### Disaster Recovery Checklist

**Prevention**:
- [ ] State stored in Azure Storage with versioning enabled
- [ ] Regular state backups (automated via CI/CD)
- [ ] Multiple people have access to state storage
- [ ] State storage has geo-redundancy enabled
- [ ] `.terraform` directory in `.gitignore`

**Recovery Preparation**:
- [ ] Document all Azure resource IDs
- [ ] Maintain inventory of deployed resources
- [ ] Test restore procedures quarterly
- [ ] Keep backup of terraform.tfstate off-system
- [ ] Document dependencies between resources

**Recovery Process**:
1. Assess damage (what was lost/changed)
2. Check state file integrity
3. Restore state from backup if needed
4. Run `terraform plan` to see drift
5. Apply changes to restore infrastructure
6. Verify outputs and connectivity
7. Restore data from backups
8. Run application smoke tests
9. Document incident and improvements

### Emergency Contacts

In case of infrastructure emergency:

1. **State File Issues**: Check Azure Storage, restore from version history
2. **Resource Deletion**: Review Activity Log, restore from Terraform
3. **Permission Issues**: Contact Azure subscription admin
4. **Terraform Bugs**: Check GitHub issues, Terraform community forum

### Monthly DR Drills

Recommended monthly tasks:

```bash
# 1. Backup current state
./scripts/backup-state.sh

# 2. Test state recovery
terraform state pull > test-recovery.tfstate
terraform state push test-recovery.tfstate

# 3. Verify plan matches reality
terraform plan -var-file=environments/prod.tfvars

# 4. Document any drift
terraform show > current-state-$(date +%Y%m).txt

# 5. Update recovery documentation if needed
```

## Troubleshooting

### terraform init fails

- Verify Azure CLI is logged in: `az account show`
- Check backend.tf storage account name is correct
- Ensure storage account exists and is accessible

### terraform plan shows unexpected changes

- Run `terraform refresh` to sync state
- Check if resources were modified outside Terraform
- Verify variable values in .tfvars file

### Resource already exists error

- Check if resources exist in Azure portal
- Import existing resource: `terraform import <resource_type>.<name> <azure_resource_id>`
- Or delete conflicting resource manually

### Permission denied errors

- Verify account has Contributor role
- Check subscription is correct: `az account show`
- Ensure no Azure Policy blocking resource creation

## Security Best Practices

1. **Never commit secrets**: Keep *.tfvars files (except .example) out of git
2. **Use sensitive outputs**: Mark all passwords/keys as sensitive
3. **State file security**: Store state in Azure Storage with encryption
4. **Access control**: Use RBAC to limit who can apply changes
5. **Network security**: Configure firewall rules on database and storage

## Cost Estimation

### Development Environment (~€60/month)
- App Service Plan B1: €48
- PostgreSQL Burstable B1ms: €12
- Storage Account: €0.05
- Application Insights: €0 (5GB free tier)

### Staging Environment (~€171/month)
- App Service Plan B2: €96
- PostgreSQL General Purpose D2s_v3: €75
- Storage Account: €0.10
- Application Insights: €0

### Production Environment (~€142/month)
- App Service Plan S1: €67
- PostgreSQL General Purpose D2s_v3: €75
- Storage Account: €0.20
- Application Insights: €0

*Prices subject to change. Use Azure Pricing Calculator for current estimates.*

## Support and Contribution

See `CONTRIBUTING.md` for development guidelines and coding standards.

## License

This infrastructure code is part of the TaskManager project.
