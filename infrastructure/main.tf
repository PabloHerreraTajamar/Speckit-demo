terraform {
  required_version = ">= 1.5.0"
}

# Root Terraform Configuration
# This file orchestrates all infrastructure modules

# Resource Group - Logical container for all Azure resources
resource "azurerm_resource_group" "main" {
  name     = "rg-${local.resource_prefix}-${local.location_short}"
  location = var.location
  tags     = local.common_tags
}

# Monitoring Module (must be created first for App Insights integration)
module "monitoring" {
  source              = "./modules/monitoring"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  project_name        = var.project_name
  tags                = local.common_tags
}

# Compute Module (App Service Plan and App Service)
module "compute" {
  source                                   = "./modules/compute"
  resource_group_name                      = azurerm_resource_group.main.name
  location                                 = azurerm_resource_group.main.location
  environment                              = var.environment
  project_name                             = var.project_name
  sku_name                                 = var.app_service_sku
  application_insights_connection_string   = module.monitoring.application_insights_connection_string
  application_insights_instrumentation_key = module.monitoring.application_insights_instrumentation_key
  tags                                     = local.common_tags

  depends_on = [module.monitoring]
}

# Database Module - PostgreSQL Flexible Server
module "database" {
  source              = "./modules/database"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  project_name        = var.project_name
  database_sku        = var.database_sku
  tags                = local.common_tags
}

# Storage Module (Storage Account and Blob Container)
module "storage" {
  source              = "./modules/storage"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  project_name        = var.project_name
  tags                = local.common_tags
}
