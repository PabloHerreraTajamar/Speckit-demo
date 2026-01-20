# Terraform Outputs Reference

This document describes all outputs provided by the infrastructure and how to use them for application deployment.

## Output Overview

After running `terraform apply`, you can access all output values using:

```bash
# View all outputs
terraform output

# View a specific output
terraform output app_service_url

# View all outputs in JSON format (useful for CI/CD)
terraform output -json

# View sensitive output (will prompt for confirmation)
terraform output postgresql_connection_string
```

## Available Outputs

### Compute Outputs

#### `app_service_name`
- **Description**: Name of the Azure App Service
- **Sensitive**: No
- **Example**: `app-dev-taskmanager-eastus`
- **Usage**: Reference for Azure CLI commands or portal navigation

#### `app_service_default_hostname`
- **Description**: Default hostname assigned by Azure
- **Sensitive**: No
- **Example**: `app-dev-taskmanager-eastus.azurewebsites.net`
- **Usage**: Base hostname for the application

#### `app_service_url`
- **Description**: Full HTTPS URL for the application
- **Sensitive**: No
- **Example**: `https://app-dev-taskmanager-eastus.azurewebsites.net`
- **Usage**: Direct access to the deployed application

### Database Outputs

#### `postgresql_server_fqdn`
- **Description**: Fully qualified domain name of the PostgreSQL server
- **Sensitive**: No
- **Example**: `psql-dev-taskmanager-eastus.postgres.database.azure.com`
- **Usage**: Connection hostname for database clients

#### `postgresql_database_name`
- **Description**: Name of the PostgreSQL database
- **Sensitive**: No
- **Example**: `taskmanager`
- **Usage**: Database name for connection strings

#### `postgresql_connection_string` ⚠️
- **Description**: Complete PostgreSQL connection string for Django
- **Sensitive**: **YES** - Contains admin password
- **Format**: `postgresql://[user]:[password]@[host]:5432/[database]?sslmode=require`
- **Usage**: 
  ```bash
  # Export to environment variable
  export DATABASE_URL=$(terraform output -raw postgresql_connection_string)
  
  # Use in Django settings.py
  # DATABASES['default'] = dj_database_url.config(conn_max_age=600)
  ```
- **Security**: Never log or commit this value. Use Azure Key Vault for production.

### Storage Outputs

#### `storage_account_name`
- **Description**: Name of the Azure Storage Account
- **Sensitive**: No
- **Example**: `stdevtaskmanagereastus`
- **Usage**: Reference for Azure CLI or SDK operations

#### `storage_container_name`
- **Description**: Name of the blob container for task attachments
- **Sensitive**: No
- **Example**: `task-attachments`
- **Usage**: Container name for file upload operations

#### `storage_blob_endpoint`
- **Description**: Primary blob storage endpoint URL
- **Sensitive**: No
- **Example**: `https://stdevtaskmanagereastus.blob.core.windows.net/`
- **Usage**: Base URL for blob operations

#### `storage_connection_string` ⚠️
- **Description**: Complete storage account connection string
- **Sensitive**: **YES** - Contains account key
- **Format**: `DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net`
- **Usage**:
  ```bash
  # Export to environment variable
  export AZURE_STORAGE_CONNECTION_STRING=$(terraform output -raw storage_connection_string)
  
  # Use in Django settings.py with django-storages
  # DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
  # AZURE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
  ```
- **Security**: Never log or commit this value. Use Managed Identity for production.

### Monitoring Outputs

#### `application_insights_name`
- **Description**: Name of the Application Insights resource
- **Sensitive**: No
- **Example**: `appi-dev-taskmanager-eastus`
- **Usage**: Reference for Azure portal or monitoring queries

#### `application_insights_instrumentation_key` ⚠️
- **Description**: Instrumentation key for Application Insights
- **Sensitive**: **YES** - Authentication credential
- **Format**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (GUID)
- **Usage**:
  ```bash
  # Already configured in App Service app_settings automatically
  # For local development:
  export APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=$(terraform output -raw application_insights_instrumentation_key)
  ```
- **Note**: Connection string is preferred over instrumentation key in modern applications

#### `application_insights_connection_string` ⚠️
- **Description**: Application Insights connection string (recommended)
- **Sensitive**: **YES** - Contains instrumentation key
- **Format**: `InstrumentationKey=...;IngestionEndpoint=...;LiveEndpoint=...`
- **Usage**:
  ```bash
  # Already configured in App Service app_settings automatically
  # For local development:
  export APPLICATIONINSIGHTS_CONNECTION_STRING=$(terraform output -raw application_insights_connection_string)
  
  # Use in Django with opencensus-ext-azure
  # OPENCENSUS_TRACE_EXPORTER_CONNECTION_STRING = os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
  ```

### Resource Group Outputs

#### `resource_group_id`
- **Description**: Azure Resource Manager ID of the resource group
- **Sensitive**: No
- **Example**: `/subscriptions/xxx/resourceGroups/rg-dev-taskmanager-eastus`
- **Usage**: Reference for Azure Resource Manager operations

#### `resource_group_name`
- **Description**: Name of the resource group
- **Sensitive**: No
- **Example**: `rg-dev-taskmanager-eastus`
- **Usage**: Reference for Azure CLI commands

#### `resource_group_location`
- **Description**: Azure region where resources are deployed
- **Sensitive**: No
- **Example**: `eastus`
- **Usage**: Region reference for additional resource deployments

## Using Outputs in CI/CD Pipelines

### GitHub Actions Example

```yaml
- name: Deploy to Azure App Service
  env:
    DATABASE_URL: ${{ steps.terraform.outputs.postgresql_connection_string }}
    AZURE_STORAGE_CONNECTION_STRING: ${{ steps.terraform.outputs.storage_connection_string }}
  run: |
    # Deploy application using connection strings
    az webapp deployment source config-zip \
      --resource-group ${{ steps.terraform.outputs.resource_group_name }} \
      --name ${{ steps.terraform.outputs.app_service_name }} \
      --src app.zip
```

### Azure DevOps Example

```yaml
- script: |
    echo "##vso[task.setvariable variable=APP_URL]$(terraform output -raw app_service_url)"
    echo "##vso[task.setvariable variable=DATABASE_URL;issecret=true]$(terraform output -raw postgresql_connection_string)"
  displayName: 'Extract Terraform Outputs'
```

### Shell Script Example

```bash
#!/bin/bash
# extract-outputs.sh - Export all Terraform outputs as environment variables

cd infrastructure

export APP_SERVICE_URL=$(terraform output -raw app_service_url)
export DATABASE_URL=$(terraform output -raw postgresql_connection_string)
export AZURE_STORAGE_CONNECTION_STRING=$(terraform output -raw storage_connection_string)
export APPLICATIONINSIGHTS_CONNECTION_STRING=$(terraform output -raw application_insights_connection_string)

echo "✅ Outputs extracted and exported as environment variables"
echo "App Service URL: $APP_SERVICE_URL"
echo "Other sensitive values are hidden for security"
```

## Output Validation

Run the following checks to ensure outputs are correctly configured:

```bash
# 1. Verify all outputs are defined
terraform output

# 2. Check sensitive outputs are masked in plan
terraform plan -var-file=environments/dev.tfvars | grep "sensitive value"

# 3. Validate JSON output structure
terraform output -json | jq 'keys'

# 4. Test specific output extraction
terraform output -raw app_service_url

# 5. Verify PostgreSQL connection string format
terraform output -raw postgresql_connection_string | grep "postgresql://"
```

## Security Best Practices

1. **Never commit outputs to version control**: Especially sensitive values
2. **Use Azure Key Vault**: Store sensitive outputs in Key Vault for production
3. **Rotate credentials regularly**: Database passwords and storage keys
4. **Use Managed Identity**: Prefer managed identity over connection strings in production
5. **Audit access**: Monitor who accesses sensitive outputs via Terraform state
6. **Encrypt state files**: Use encrypted backend storage (Azure Storage with encryption)

## Troubleshooting

### "No outputs found"
**Solution**: Run `terraform apply` first to create infrastructure

### "Output value is null"
**Cause**: Resource hasn't been created yet or module output is missing
**Solution**: Check `terraform plan` for errors, verify module outputs are defined

### "Error: Output not found"
**Cause**: Output name typo or output not defined
**Solution**: Run `terraform output` to see available outputs

### Sensitive outputs not masking
**Cause**: Missing `sensitive = true` attribute
**Solution**: Add `sensitive = true` to output block in `outputs.tf`

## References

- [Terraform Output Values](https://www.terraform.io/language/values/outputs)
- [Django Database Configuration](https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes)
- [Azure Storage with Django](https://django-storages.readthedocs.io/en/latest/backends/azure.html)
- [Application Insights for Python](https://docs.microsoft.com/azure/azure-monitor/app/opencensus-python)
