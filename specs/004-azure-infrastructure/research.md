# Phase 0: Research - Azure Infrastructure as Code

**Date**: 2026-01-19  
**Feature**: 004-azure-infrastructure  
**Branch**: `004-azure-infrastructure`

## NEEDS CLARIFICATION Review

**Status**: ✅ NO CLARIFICATIONS NEEDED

All requirements in `spec.md` are clear and implementable:
- Azure resource types explicitly defined (Resource Group, App Service Plan, App Service, Database, Storage, Application Insights)
- Multi-environment strategy specified (dev/staging/prod via tfvars)
- Technology choice mandated by constitution (Terraform per Principle II)
- Connection string outputs clearly defined
- Resource tagging requirements explicit (project, environment, owner)

## Technology Decisions

### 1. Terraform Module Strategy

**Decision**: Use local child modules rather than external registry modules

**Options Evaluated**:
- **Option A**: Monolithic `main.tf` with all resources
  - ❌ Not scalable, hard to test, violates DRY
  
- **Option B**: Azure Verified Modules from registry
  - ⚠️ Adds external dependency, potential breaking changes, learning curve
  
- **Option C**: Local child modules (SELECTED)
  - ✅ Full control, testable, reusable across environments
  - ✅ Aligns with Object Calisthenics (encapsulation, single responsibility)

**Rationale**: Local modules provide best balance of reusability and maintainability for 10-15 resources without external dependency risk.

---

### 2. Database Choice: Azure SQL vs. PostgreSQL

**Decision**: Azure Database for PostgreSQL Flexible Server

**Options Evaluated**:
- **Option A**: Azure SQL Database
  - ✅ Managed, auto-scaling
  - ❌ Higher cost for equivalent tier, SQL Server licensing
  
- **Option B**: Azure Database for PostgreSQL Flexible Server (SELECTED)
  - ✅ Lower cost, Django ORM excellent PostgreSQL support
  - ✅ Open-source, no licensing concerns
  - ✅ JSON/JSONB support for future extensibility

**Rationale**: PostgreSQL is the preferred choice for Django projects (official Django tutorial uses PostgreSQL). Cost-effective and feature-rich for this workload.

---

### 3. App Service SKU Per Environment

**Decision**: Environment-specific SKUs with clear tiers

**Mapping**:
- **dev**: B1 (Basic) - 1.75 GB RAM, 1 core, €48/month
- **staging**: B2 (Basic) - 3.5 GB RAM, 2 cores, €96/month
- **prod**: S1 (Standard) - 1.75 GB RAM, 1 core, auto-scale, backup, €67/month

**Rationale**: B1 sufficient for dev testing, S1 for prod enables auto-scaling and daily backups. Staging uses B2 for performance testing under load.

---

### 4. Terraform State Backend

**Decision**: Azure Blob Storage with state locking

**Configuration**:
- Storage Account: `tfstate<random>` (lowercase, unique)
- Container: `terraform-state`
- State locking: enabled via Azure Blob lease
- Encryption: enabled (Azure Storage encryption at rest)

**Rationale**: Azure native state backend ensures consistency, prevents concurrent modifications, and provides audit trail. Required for team collaboration.

---

### 5. Secret Management Strategy

**Decision**: Two-tier approach

**Tier 1 - Terraform Variables** (non-sensitive):
- Resource names, locations, SKUs
- Defined in `variables.tf`, supplied via `.tfvars`

**Tier 2 - Azure Key Vault** (sensitive):
- Database admin password
- Storage account access keys (post-provisioning)
- Application Insights instrumentation key

**Workflow**:
1. Terraform provisions Key Vault
2. Database password generated via `random_password` resource
3. Password stored in Key Vault secret
4. App Service reads from Key Vault via managed identity

**Rationale**: Aligns with Principle IV (Security First) - no secrets in code or state file. Managed identity eliminates credential management.

---

### 6. Resource Naming Convention

**Decision**: Predictable naming with environment prefix

**Pattern**: `<prefix>-<environment>-<resource-type>-<region>`

**Examples**:
- Resource Group: `rg-dev-taskmanager-eastus`
- App Service: `app-dev-taskmanager-eastus`
- Database: `psql-dev-taskmanager-eastus`
- Storage: `stdevtaskmgr` (no hyphens, lowercase, unique suffix)

**Rationale**: Clear identification of resource purpose, environment, and location. Enables cost tracking and automation. Complies with Azure naming rules per resource type.

---

### 7. Terraform Testing Strategy

**Decision**: Multi-layer validation

**Layers**:
1. **Syntax**: `terraform validate` (CI pipeline)
2. **Linting**: `tflint` with Azure ruleset
3. **Plan Review**: `terraform plan` on PR (GitHub Actions)
4. **Integration**: Terratest in isolated Azure subscription (optional for this project scale)

**Rationale**: Terraform validate and tflint provide 90% confidence without infrastructure cost. Full Terratest deferred to larger projects.

---

### 8. CI/CD Integration Points

**Decision**: GitHub Actions workflow for Terraform

**Workflow**:
1. PR triggers: `terraform fmt -check`, `terraform validate`, `tflint`, `terraform plan`
2. Merge to main: Manual approval → `terraform apply` for dev
3. Tag release: Manual approval → `terraform apply` for staging → prod

**Rationale**: Automated validation prevents misconfigurations. Manual approval for apply enforces review and control. Staged rollout reduces risk.

---

## Technical Constraints

1. **Terraform Version**: >=1.6.0 (required for new Azure features)
2. **Azure Provider**: >=3.80.0 (Flexible Server PostgreSQL stable)
3. **Azure Region**: East US (default), configurable via variable
4. **Resource Limits**: Free tier not supported (requires B1+ per spec)
5. **State File**: MUST be in Azure Blob Storage (no local state in prod)
6. **Idempotency**: All modules MUST support `terraform apply` without changes after first run

---

## Performance Considerations

1. **Provisioning Time**:
   - Cold start (new subscription): ~8-10 minutes
   - Incremental updates: ~1-3 minutes
   - Target: <10 minutes per constitution constraint

2. **Terraform Parallelism**: Default (-parallelism=10) sufficient for 10-15 resources

3. **Database Provisioning**: PostgreSQL Flexible Server ~4-6 minutes (longest resource)

4. **State File Size**: <100 KB for this scale (no performance impact)

---

## Security Considerations

1. **Sensitive Outputs**: Mark database connection strings and storage keys as `sensitive = true`
2. **Database Password**: 16-char random password with special chars, stored in Key Vault
3. **Storage Account**: Disable public blob access, require HTTPS
4. **App Service**: Managed identity enabled for Key Vault access
5. **Network**: Database firewall rules to allow only App Service IPs
6. **TLS**: Enforce TLS 1.2+ for database connections

---

## Cost Estimates (Monthly, East US)

### Development Environment
- Resource Group: €0
- App Service Plan (B1): €48
- App Service: included in plan
- PostgreSQL Flexible (Burstable B1ms): €12
- Storage Account (LRS, <1GB): €0.05
- Application Insights (5GB free): €0
- **Total dev**: ~€60/month

### Staging Environment
- App Service Plan (B2): €96
- PostgreSQL Flexible (GP D2s_v3): €75
- Storage Account: €0.10
- Application Insights: €0
- **Total staging**: ~€171/month

### Production Environment
- App Service Plan (S1): €67
- PostgreSQL Flexible (GP D2s_v3): €75
- Storage Account: €0.20
- Application Insights (10GB free): €0
- **Total prod**: ~€142/month

**Grand Total**: ~€373/month for 3 environments

---

## Dependencies

### External Dependencies
- Azure subscription with Contributor role
- Azure CLI or Azure PowerShell (local dev)
- Terraform CLI 1.6+
- Git for version control

### Internal Dependencies
- None (this is the foundational feature)

### Post-Implementation Dependencies
- Features 001, 002, 003 will consume outputs from this feature (App Service name, database connection, storage keys)

---

## Open Questions

**Status**: ✅ ALL RESOLVED

1. ~~Database choice: SQL vs. PostgreSQL?~~ → PostgreSQL (see Decision #2)
2. ~~State backend location?~~ → Azure Blob Storage (see Decision #4)
3. ~~Testing strategy for Terraform?~~ → Multi-layer validation (see Decision #7)
4. ~~SKU tiers per environment?~~ → Defined in Decision #3

---

## References

- [Azure Naming Conventions](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)
- [Terraform Azure Provider Docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [PostgreSQL Flexible Server Pricing](https://azure.microsoft.com/en-us/pricing/details/postgresql/flexible-server/)
- [App Service Pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)
- [Azure Storage Pricing](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/)
