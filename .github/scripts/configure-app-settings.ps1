# Script to configure Azure App Service settings for GitHub Actions

$APP_NAME = "app-dev-taskmanager-westeurope"
$RESOURCE_GROUP = "rg-dev-taskmanager-westeurope"

Write-Host "🔧 Configuring Azure App Service settings..." -ForegroundColor Cyan
Write-Host ""

# Generate a secure SECRET_KEY (alphanumeric only to avoid escaping issues)
Write-Host "🔑 Generating Django SECRET_KEY..." -ForegroundColor Yellow
$SECRET_KEY = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

# Read .env file for database credentials
Write-Host "📖 Reading database credentials from .env..." -ForegroundColor Yellow
if (Test-Path .env) {
    $envContent = Get-Content .env -Raw
    $dbHost = if ($envContent -match 'DB_HOST=(.+)') { $matches[1].Trim() } else { "" }
    $dbName = if ($envContent -match 'DB_NAME=(.+)') { $matches[1].Trim() } else { "" }
    $dbUser = if ($envContent -match 'DB_USER=(.+)') { $matches[1].Trim() } else { "" }
    $dbPassword = if ($envContent -match 'DB_PASSWORD=(.+)') { $matches[1].Trim() } else { "" }
    $storageConn = if ($envContent -match 'AZURE_STORAGE_CONNECTION_STRING=(.+)') { $matches[1].Trim() } else { "" }
    $appInsightsKey = if ($envContent -match 'APPINSIGHTS_INSTRUMENTATION_KEY=(.+)') { $matches[1].Trim() } else { "" }
} else {
    Write-Host "⚠️  .env file not found. Using Terraform outputs..." -ForegroundColor Yellow
    cd infrastructure
    $tfOutput = terraform output -json | ConvertFrom-Json
    $dbHost = $tfOutput.postgresql_server_fqdn.value
    $dbName = $tfOutput.postgresql_database_name.value
    $dbUser = $tfOutput.postgresql_administrator_login.value
    $dbPassword = Read-Host "Enter PostgreSQL password" -AsSecureString | ConvertFrom-SecureString -AsPlainText
    $storageConn = $tfOutput.storage_connection_string.value
    $appInsightsKey = $tfOutput.application_insights_instrumentation_key.value
    cd ..
}

Write-Host "⚙️  Setting application settings..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings `
    "SECRET_KEY=$SECRET_KEY" `
    "DEBUG=False" `
    "ALLOWED_HOSTS=$APP_NAME.azurewebsites.net" `
    "DB_HOST=$dbHost" `
    "DB_NAME=$dbName" `
    "DB_USER=$dbUser" `
    "DB_PASSWORD=$dbPassword" `
    "AZURE_STORAGE_CONNECTION_STRING=$storageConn" `
    "APPINSIGHTS_INSTRUMENTATION_KEY=$appInsightsKey" `
    "DJANGO_SETTINGS_MODULE=taskmanager.settings.production" `
    "ADMIN_EMAIL=admin@taskmanager.com" `
    "ADMIN_PASSWORD=admin123" | Out-Null

Write-Host ""
Write-Host "✅ Application settings configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 Current settings:" -ForegroundColor Cyan
az webapp config appsettings list `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --query "[?!contains(name, 'WEBSITE_')].{Name:name, Value:value}" `
  --output table
