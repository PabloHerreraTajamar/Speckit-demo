# Terraform State Backend Configuration
# 
# IMPORTANT: Before uncommenting, create Azure Storage Account for state:
#
#   RESOURCE_GROUP="terraform-state-rg"
#   STORAGE_ACCOUNT="tfstate$(openssl rand -hex 4)"
#   CONTAINER_NAME="tfstate"
#   LOCATION="eastus"
#
#   az group create --name $RESOURCE_GROUP --location $LOCATION
#   az storage account create --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP \
#     --location $LOCATION --sku Standard_LRS --encryption-services blob
#   az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT
#
# Then uncomment the block below and replace <STORAGE_ACCOUNT_NAME>

# terraform {
#   backend "azurerm" {
#     resource_group_name  = "terraform-state-rg"
#     storage_account_name = "<STORAGE_ACCOUNT_NAME>"  # Replace with your storage account name
#     container_name       = "tfstate"
#     key                  = "taskmanager.terraform.tfstate"
#   }
# }
