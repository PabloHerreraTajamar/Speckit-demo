# Security & Secrets Management Checklist

This checklist ensures that sensitive data is properly managed and never exposed in version control or Terraform outputs.

## Pre-Commit Checklist

Before committing any Terraform code changes, verify:

- [ ] **No Hardcoded Secrets**: Search all `.tf` files for passwords, connection strings, API keys, or tokens
  ```bash
  # Run this command to scan for potential secrets
  grep -r "password\s*=\s*\"" infrastructure/ --include="*.tf"
  grep -r "secret\s*=\s*\"" infrastructure/ --include="*.tf"
  grep -r "api_key\s*=\s*\"" infrastructure/ --include="*.tf"
  ```

- [ ] **Sensitive Variables Marked**: All variables containing secrets have `sensitive = true`
  - Database passwords
  - Storage access keys
  - API keys and tokens
  - Connection strings

- [ ] **Sensitive Outputs Marked**: All outputs exposing secrets have `sensitive = true`
  - Connection strings (database, storage, monitoring)
  - Access keys and passwords
  - Instrumentation keys

- [ ] **Random Password Resources**: Use `random_password` for generating secure passwords
  - Minimum 16 characters (32 recommended)
  - Include special characters, numbers, upper and lowercase

- [ ] **Gitignore Updated**: Ensure `.gitignore` excludes sensitive files
  - `*.tfvars` (except `*.tfvars.example`)
  - `.terraform/*`
  - `*.tfstate*`

- [ ] **Example Files Only**: Committed `.tfvars.example` files contain NO actual secrets
  - Use placeholders like `"REPLACE_WITH_YOUR_PASSWORD"`
  - Include comments explaining what values are needed

## Terraform Plan Review

Before applying infrastructure changes:

- [ ] **Masked Outputs**: Run `terraform plan` and verify sensitive outputs show as `(sensitive value)`
  ```bash
  terraform plan -var-file=environments/dev.tfvars
  # Look for: (sensitive value) instead of actual secrets
  ```

- [ ] **No Plain Text Secrets**: Check plan output for exposed passwords or keys
  - Connection strings should be masked
  - Admin passwords should be masked
  - Access keys should be masked

## State File Security

- [ ] **Remote Backend**: Configure Azure Storage backend for state files (see `backend.tf`)
- [ ] **Encryption Enabled**: State files stored in encrypted storage
- [ ] **Access Restricted**: Only authorized team members can access state storage
- [ ] **Never Commit State**: `.tfstate` files are in `.gitignore`

## Runtime Security

- [ ] **Environment Variables**: Sensitive values passed via environment variables when possible
  ```bash
  export TF_VAR_db_password="secure-password"
  ```

- [ ] **Managed Identities**: Use Azure Managed Identity instead of service principal credentials where possible
- [ ] **Key Vault Integration**: Consider Azure Key Vault for production secrets management
- [ ] **Least Privilege**: Service principals and identities have minimum required permissions

## Code Review Checklist

When reviewing Terraform PRs:

- [ ] No secrets in code or comments
- [ ] All sensitive variables/outputs properly marked
- [ ] `.tfvars` files not committed (only `.tfvars.example`)
- [ ] Random password generators used for credentials
- [ ] Terraform plan shows masked sensitive values

## Incident Response

If secrets are accidentally committed:

1. **Rotate immediately**: Change all exposed credentials in Azure portal
2. **Revoke access**: Invalidate compromised keys/passwords
3. **Remove from history**: Use `git filter-branch` or BFG Repo-Cleaner
4. **Audit access**: Check Azure activity logs for unauthorized access
5. **Update documentation**: Document incident and prevention steps

## References

- [Terraform Sensitive Data Best Practices](https://www.terraform.io/docs/language/values/outputs.html#sensitive-suppressing-values-in-cli-output)
- [Azure Key Vault Integration](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/key_vault_secret)
- [Git Secrets Prevention Tools](https://github.com/awslabs/git-secrets)
