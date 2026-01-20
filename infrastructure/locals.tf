# Local Values
#
# Common values used across multiple resources

locals {
  # Resource naming convention: <type>-<env>-<project>-<region>
  resource_prefix = "${var.environment}-${var.project_name}"

  # Common tags applied to all resources
  common_tags = {
    project     = var.project_name
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
    cost_center = var.cost_center != "" ? var.cost_center : null
  }

  # Location normalized (remove spaces for resource names)
  location_short = replace(lower(var.location), " ", "")
}
