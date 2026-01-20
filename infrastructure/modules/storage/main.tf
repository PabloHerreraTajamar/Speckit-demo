# Storage Module - Storage Account and Blob Container

locals {
  resource_prefix = "${var.environment}-${var.project_name}"
  location_short  = replace(lower(var.location), " ", "")
  # Storage account names must be globally unique and can only contain lowercase letters and numbers (3-24 chars)
  storage_account_name = "st${var.environment}${replace(var.project_name, "-", "")}${substr(replace(local.location_short, "-", ""), 0, 6)}"
}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                      = substr(local.storage_account_name, 0, 24)
  location                  = var.location
  resource_group_name       = var.resource_group_name
  account_tier              = var.account_tier
  account_replication_type  = var.account_replication_type
  access_tier               = var.access_tier
  min_tls_version           = "TLS1_2"
  enable_https_traffic_only = true

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

# Blob Container for task attachments
resource "azurerm_storage_container" "attachments" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}
