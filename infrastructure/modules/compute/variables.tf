# Compute Module Variables

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "sku_name" {
  description = "App Service Plan SKU (B1, B2, S1, P1v2)"
  type        = string
  default     = "B1"

  validation {
    condition     = contains(["B1", "B2", "S1", "P1v2"], var.sku_name)
    error_message = "SKU must be one of: B1, B2, S1, P1v2."
  }
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "application_insights_connection_string" {
  description = "Application Insights connection string for monitoring"
  type        = string
  default     = ""
  sensitive   = true
}

variable "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  type        = string
  default     = ""
  sensitive   = true
}
