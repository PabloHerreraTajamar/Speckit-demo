# Compute Module - App Service Plan and App Service

locals {
  resource_prefix = "${var.environment}-${var.project_name}"
  location_short  = replace(lower(var.location), " ", "")
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "asp-${local.resource_prefix}-${local.location_short}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = var.sku_name
  tags                = var.tags
}

# App Service (Linux Web App)
resource "azurerm_linux_web_app" "main" {
  name                = "app-${local.resource_prefix}-${local.location_short}"
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true
  tags                = var.tags

  site_config {
    application_stack {
      python_version = "3.11"
    }

    always_on           = var.sku_name != "F1" && var.sku_name != "D1" # Always on not available on Free tier
    http2_enabled       = true
    ftps_state          = "Disabled"
    minimum_tls_version = "1.2"
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = var.application_insights_connection_string != "" ? {
    "APPLICATIONINSIGHTS_CONNECTION_STRING"      = var.application_insights_connection_string
    "ApplicationInsightsAgent_EXTENSION_VERSION" = "~3"
    "XDT_MicrosoftApplicationInsights_Mode"      = "recommended"
  } : {}

  lifecycle {
    ignore_changes = [
      app_settings["WEBSITE_ENABLE_SYNC_UPDATE_SITE"],
    ]
  }
}
