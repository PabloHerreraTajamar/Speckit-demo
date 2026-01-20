# GitHub Secrets Configuration Script
# This script helps you configure the required secrets for CI/CD

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [string]$RepoName = "taskmanager-django"
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Secrets Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get Azure Publish Profile
Write-Host "Step 1: Getting Azure Web App Publish Profile..." -ForegroundColor Green
Write-Host ""

$appName = "app-dev-taskmanager-westeurope"
$resourceGroup = "rg-dev-taskmanager-westeurope"

Write-Host "Fetching publish profile from Azure..." -ForegroundColor Cyan
Write-Host "   App Name: $appName" -ForegroundColor White
Write-Host "   Resource Group: $resourceGroup" -ForegroundColor White
Write-Host ""

$publishProfile = az webapp deployment list-publishing-profiles `
    --name $appName `
    --resource-group $resourceGroup `
    --xml 2>&1

if ($LASTEXITCODE -eq 0) {
    # Save to file
    $publishProfile | Out-File -FilePath "publish-profile.xml" -Encoding UTF8
    
    Write-Host "✓ Publish profile saved to: publish-profile.xml" -ForegroundColor Green
    Write-Host ""
    
    # Copy to clipboard
    Set-Clipboard -Value $publishProfile
    Write-Host "✓ Publish profile copied to clipboard!" -ForegroundColor Green
    Write-Host ""
    
    # Display preview
    Write-Host "Preview (first 200 characters):" -ForegroundColor Yellow
    Write-Host $publishProfile.Substring(0, [Math]::Min(200, $publishProfile.Length)) -ForegroundColor Gray
    Write-Host "..." -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "❌ Error getting publish profile" -ForegroundColor Red
    Write-Host "Make sure you're logged in to Azure: az login" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Step 2: Open GitHub Secrets page
Write-Host "Step 2: Opening GitHub Secrets page..." -ForegroundColor Green
Write-Host ""

$secretsUrl = "https://github.com/$Username/$RepoName/settings/secrets/actions"
Write-Host "Opening: $secretsUrl" -ForegroundColor Cyan
Start-Process $secretsUrl
Write-Host ""

Write-Host "Please complete these steps in the browser:" -ForegroundColor Yellow
Write-Host "  1. Click 'New repository secret'" -ForegroundColor White
Write-Host "  2. Name: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor White
Write-Host "  3. Value: Paste from clipboard (already copied!)" -ForegroundColor White
Write-Host "  4. Click 'Add secret'" -ForegroundColor White
Write-Host ""

Write-Host "Press Enter once you've added the secret..." -ForegroundColor Cyan
Read-Host

# Step 3: Verify setup
Write-Host ""
Write-Host "Step 3: Verifying CI/CD setup..." -ForegroundColor Green
Write-Host ""

# Check if workflow files exist
$workflowFiles = @(
    ".github/workflows/azure-deploy.yml",
    ".github/workflows/infrastructure.yml"
)

$allFilesExist = $true
foreach ($file in $workflowFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file (missing)" -ForegroundColor Red
        $allFilesExist = $false
    }
}

Write-Host ""

if ($allFilesExist) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Setup complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 CI/CD pipeline is now configured!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "What happens next:" -ForegroundColor Yellow
    Write-Host "   1. Any push to 'master' branch will trigger automatic deployment" -ForegroundColor White
    Write-Host "   2. Tests will run automatically" -ForegroundColor White
    Write-Host "   3. If tests pass, app deploys to Azure" -ForegroundColor White
    Write-Host "   4. You can monitor progress in GitHub Actions tab" -ForegroundColor White
    Write-Host ""
    Write-Host "View your Actions:" -ForegroundColor Cyan
    Write-Host "   https://github.com/$Username/$RepoName/actions" -ForegroundColor White
    Write-Host ""
    Write-Host "Your deployed app will be at:" -ForegroundColor Cyan
    Write-Host "   https://app-dev-taskmanager-westeurope.azurewebsites.net" -ForegroundColor White
    Write-Host ""
    Write-Host "To trigger a deployment now:" -ForegroundColor Yellow
    Write-Host "   git commit --allow-empty -m 'trigger deployment'" -ForegroundColor White
    Write-Host "   git push origin master" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Some workflow files are missing" -ForegroundColor Yellow
    Write-Host "Please make sure all CI/CD files are committed and pushed." -ForegroundColor White
    Write-Host ""
}

# Cleanup
Write-Host "Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item "publish-profile.xml" -ErrorAction SilentlyContinue
Write-Host "Done!" -ForegroundColor Green
