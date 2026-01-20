# Database Module - PostgreSQL Flexible Server

locals {
  resource_prefix = "${var.environment}-${var.project_name}"
  location_short  = replace(lower(var.location), " ", "")
}

# Random password for PostgreSQL admin
resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
  min_lower        = 1
  min_upper        = 1
  min_numeric      = 1
  min_special      = 1
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                         = "psql-${local.resource_prefix}-${local.location_short}"
  location                     = var.location
  resource_group_name          = var.resource_group_name
  version                      = var.database_version
  administrator_login          = var.administrator_login
  administrator_password       = random_password.db_password.result
  sku_name                     = var.database_sku
  storage_mb                   = var.database_storage_gb * 1024
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  tags                         = var.tags

  lifecycle {
    ignore_changes = [
      zone,
      high_availability,
    ]
  }
}

# Firewall rule to allow Azure services
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name             = "AllowAllAzureServicesAndResourcesWithinAzureIps"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Database
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "taskmanager"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}
