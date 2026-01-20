# Common Variables

variable "project_name" {
  description = "Name of the project (used in resource naming)"
  type        = string
  default     = "taskmanager"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"

  validation {
    condition     = contains(["East US", "East US 2", "West US", "West Europe", "North Europe"], var.location)
    error_message = "Location must be a valid Azure region."
  }
}

variable "owner" {
  description = "Owner tag for resources (team or individual)"
  type        = string
  default     = "platform-team"
}

variable "cost_center" {
  description = "Cost center tag for billing allocation (optional)"
  type        = string
  default     = ""
}

# Compute Module Variables
variable "app_service_sku" {
  description = "App Service Plan SKU (B1, B2, S1, P1v2)"
  type        = string
  default     = "B1"

  validation {
    condition     = contains(["B1", "B2", "S1", "P1v2"], var.app_service_sku)
    error_message = "App Service SKU must be one of: B1, B2, S1, P1v2."
  }
}

# Database Module Variables
variable "database_sku" {
  description = "PostgreSQL SKU (e.g., B_Standard_B1ms, GP_Standard_D2s_v3)"
  type        = string
  default     = "B_Standard_B1ms"
}
