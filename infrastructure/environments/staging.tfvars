# Staging Environment Configuration
# This file can be committed to version control

project_name = "taskmanager"
environment  = "staging"
location     = "East US"
owner        = "platform-team"
cost_center  = ""

# Compute configuration
app_service_sku = "B2" # Staging: B2 for testing production-like workloads

# Database configuration
database_sku = "B_Standard_B2s" # Staging: Step up from dev for load testing
