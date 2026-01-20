# Tagging Strategy

## Overview

All Azure resources deployed by this Terraform configuration are tagged with a consistent set of metadata to enable cost tracking, resource organization, governance, and automation.

## Tag Schema

### Required Tags

All resources MUST have these tags:

| Tag Name | Type | Description | Example |
|----------|------|-------------|---------|
| `project` | String | Project identifier | `taskmanager` |
| `environment` | String | Environment name | `dev`, `staging`, `prod` |
| `owner` | String | Team or individual responsible | `platform-team` |
| `managed_by` | String | Management tool identifier | `terraform` |

### Optional Tags

These tags are optional but recommended:

| Tag Name | Type | Description | Example |
|----------|------|-------------|---------|
| `cost_center` | String | Billing/cost allocation code | `CC-12345` |

## Tag Implementation

### Centralized Tag Management

Tags are defined once in `locals.tf` and applied to all resources:

```hcl
locals {
  common_tags = {
    project     = var.project_name
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
    cost_center = var.cost_center != "" ? var.cost_center : null
  }
}
```

### Tag Application

All resources receive tags via module parameters:

```hcl
module "compute" {
  source = "./modules/compute"
  # ... other parameters
  tags   = local.common_tags
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.environment}-${var.project_name}"
  location = var.location
  tags     = local.common_tags
}
```

### Tag Inheritance

Azure automatically propagates tags from Resource Groups to child resources in some services. However, we explicitly apply tags to ensure consistency across all resource types.

## Tag Usage

### Cost Tracking

Use tags to filter and group costs in Azure Cost Management:

```bash
# View costs by environment
az consumption usage list \
  --query "[?tags.environment=='prod'].{Name:instanceName,Cost:pretaxCost}" \
  --output table

# View costs by project
az consumption usage list \
  --query "[?tags.project=='taskmanager'].{Name:instanceName,Cost:pretaxCost}" \
  --output table
```

### Resource Discovery

Find all resources for a specific environment:

```bash
# List all resources in dev environment
az resource list \
  --tag environment=dev \
  --query "[].{Name:name,Type:type,Location:location}" \
  --output table

# Find all Terraform-managed resources
az resource list \
  --tag managed_by=terraform \
  --output table
```

### Governance Policies

Azure Policy can enforce tagging requirements:

```json
{
  "if": {
    "allOf": [
      {
        "field": "type",
        "equals": "Microsoft.Resources/subscriptions/resourceGroups"
      },
      {
        "field": "tags['environment']",
        "notIn": ["dev", "staging", "prod"]
      }
    ]
  },
  "then": {
    "effect": "deny"
  }
}
```

## Tag Validation

### Pre-Deployment Validation

Before applying infrastructure changes, verify tags are correct:

```bash
# Check tags in plan output
terraform plan -var-file=environments/dev.tfvars | grep "tags"

# Verify all required tags are present
terraform plan -var-file=environments/dev.tfvars -no-color | \
  grep -A 5 "tags.*{" | \
  grep -E "project|environment|owner|managed_by"
```

### Post-Deployment Verification

After deployment, verify tags in Azure:

```bash
# Check Resource Group tags
az group show \
  --name rg-dev-taskmanager-eastus \
  --query tags

# Check App Service tags
az webapp show \
  --name app-dev-taskmanager-eastus \
  --resource-group rg-dev-taskmanager-eastus \
  --query tags
```

### Automated Tag Compliance

Use the provided validation script:

```bash
# Validate tags across all environments
cd tests/terraform
./plan-test.sh

# Expected output includes tag verification:
# ✅ dev: Checking environment tags... ✅
```

## Tag Best Practices

### 1. Consistency

- Use lowercase for tag names: `environment` not `Environment`
- Use consistent separators: `cost_center` not `cost-center` or `costCenter`
- Define tag values as variables, not hardcoded strings

### 2. Avoid Sensitive Data

- **Never** include passwords, secrets, or PII in tags
- Tags are visible to all users with Reader access
- Use Azure Key Vault for sensitive metadata

### 3. Keep Tags Up-to-Date

- Review tags quarterly
- Remove obsolete tags
- Update owner when team changes

### 4. Document Tag Purpose

- Maintain this document as the source of truth
- Include tag descriptions in PR reviews
- Train team on tagging standards

## Tag Reporting

### Monthly Cost Report by Environment

```bash
#!/bin/bash
# Generate monthly cost breakdown by environment

for env in dev staging prod; do
  echo "=== $env Environment ==="
  az consumption usage list \
    --start-date $(date -d "1 month ago" +%Y-%m-%d) \
    --end-date $(date +%Y-%m-%d) \
    --query "[?tags.environment=='$env'].{Resource:instanceName,Cost:pretaxCost}" \
    --output table
done
```

### Resource Inventory by Tag

```bash
# Export resource inventory to CSV
az resource list \
  --tag project=taskmanager \
  --query "[].{Name:name,Type:type,Environment:tags.environment,Owner:tags.owner,Location:location}" \
  --output json | jq -r '.[] | [.Name,.Type,.Environment,.Owner,.Location] | @csv' > resource-inventory.csv
```

## Tag Governance

### Tag Policies

Consider implementing Azure Policy to enforce:

1. **Required Tags**: All resources must have project, environment, owner
2. **Allowed Values**: Environment must be dev, staging, or prod
3. **Inherited Tags**: Child resources inherit tags from Resource Group
4. **Tag Format**: Tags must follow naming conventions

### Tag Auditing

Regular audits should check:

- [ ] All resources have required tags
- [ ] Tag values match approved list
- [ ] No orphaned resources without tags
- [ ] Cost center tags align with finance system
- [ ] Owner tags reference active team members

### Tag Maintenance

Schedule quarterly:

1. Review tag usage and compliance
2. Update owner tags for team changes
3. Remove deprecated tags
4. Add new tags for emerging requirements
5. Align tags with organizational standards

## Troubleshooting

### Tags Not Appearing

**Symptoms**: Tags defined in Terraform but not visible in Azure Portal

**Solutions**:
1. Check `tags = local.common_tags` is present in resource definition
2. Verify `terraform apply` completed successfully
3. Refresh Azure Portal (Ctrl+F5)
4. Some resources take time to display tags - wait 5 minutes

### Tag Limit Exceeded

**Symptoms**: Error: "Tag limit exceeded (50 tags per resource)"

**Solutions**:
1. Consolidate similar tags (e.g., combine `team` and `owner`)
2. Move detailed metadata to resource properties instead of tags
3. Use tag name prefixes to organize: `billing:cost_center`, `billing:project_code`

### Tag Value Constraints

Azure tag constraints:
- Tag name: 512 characters max
- Tag value: 256 characters max
- 50 tags per resource
- Tag names are case-insensitive
- Tag values are case-sensitive

## References

- [Azure Resource Tagging Best Practices](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging)
- [Azure Cost Management + Billing](https://learn.microsoft.com/en-us/azure/cost-management-billing/)
- [Terraform Azure Provider - Tags](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/tagging)
- [Azure Policy for Tag Governance](https://learn.microsoft.com/en-us/azure/governance/policy/samples/built-in-policies#tags)
