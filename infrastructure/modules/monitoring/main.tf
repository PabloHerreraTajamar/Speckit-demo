# Monitoring Module - Application Insights

locals {
  resource_prefix = "${var.environment}-${var.project_name}"
  location_short  = replace(lower(var.location), " ", "")
}

# Log Analytics Workspace (required for Application Insights)
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${local.resource_prefix}-${local.location_short}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_in_days
  tags                = var.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "appi-${local.resource_prefix}-${local.location_short}"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = var.application_type
  workspace_id        = azurerm_log_analytics_workspace.main.id
  retention_in_days   = var.retention_in_days
  tags                = var.tags
}
