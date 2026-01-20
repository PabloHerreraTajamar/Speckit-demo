#!/bin/bash

# Script to get Azure App Service Publish Profile for GitHub Actions

APP_NAME="app-dev-taskmanager-westeurope"
RESOURCE_GROUP="rg-dev-taskmanager-westeurope"

echo "🔍 Getting publish profile for $APP_NAME..."
echo ""

az webapp deployment list-publishing-profiles \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --xml

echo ""
echo "✅ Copy the entire XML output above and add it as a secret in GitHub:"
echo ""
echo "1. Go to your GitHub repository"
echo "2. Settings → Secrets and variables → Actions"
echo "3. Click 'New repository secret'"
echo "4. Name: AZURE_WEBAPP_PUBLISH_PROFILE"
echo "5. Value: Paste the XML from above"
echo "6. Click 'Add secret'"
