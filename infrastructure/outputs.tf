# Infrastructure Outputs
#
# These outputs provide connection strings and endpoints needed for application deployment.
# Sensitive outputs are marked and masked in terraform plan/apply output.

# Resource Group outputs
output "resource_group_id" {
  description = "Resource Group ID"
  value       = azurerm_resource_group.main.id
}

output "resource_group_name" {
  description = "Resource Group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource Group location"
  value       = azurerm_resource_group.main.location
}

# Compute Outputs
output "app_service_name" {
  description = "App Service name"
  value       = module.compute.app_service_name
}

output "app_service_default_hostname" {
  description = "App Service default hostname"
  value       = module.compute.app_service_default_hostname
}

output "app_service_url" {
  description = "App Service URL"
  value       = "https://${module.compute.app_service_default_hostname}"
}

# Database Outputs
output "postgresql_server_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = module.database.postgresql_server_fqdn
}

output "postgresql_database_name" {
  description = "PostgreSQL database name"
  value       = module.database.postgresql_database_name
}

output "postgresql_administrator_login" {
  description = "PostgreSQL administrator login"
  value       = module.database.postgresql_administrator_login
  sensitive   = true
}

output "postgresql_connection_string" {
  description = "PostgreSQL connection string (sensitive)"
  value       = module.database.postgresql_connection_string
  sensitive   = true
}

# Storage Outputs
output "storage_account_name" {
  description = "Storage account name"
  value       = module.storage.storage_account_name
}

output "storage_container_name" {
  description = "Blob container name"
  value       = module.storage.storage_container_name
}

output "storage_blob_endpoint" {
  description = "Storage account primary blob endpoint"
  value       = module.storage.storage_account_primary_blob_endpoint
}

output "storage_connection_string" {
  description = "Storage connection string (sensitive)"
  value       = module.storage.storage_connection_string
  sensitive   = true
}

# Monitoring Outputs
output "application_insights_name" {
  description = "Application Insights name"
  value       = module.monitoring.application_insights_name
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key (sensitive)"
  value       = module.monitoring.application_insights_instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Application Insights connection string (sensitive)"
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}
