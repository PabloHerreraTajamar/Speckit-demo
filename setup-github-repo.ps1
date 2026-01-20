# GitHub Repository Setup Script
# This script helps you create and configure the GitHub repository

param(
    [string]$Username = "",
    [string]$RepoName = "taskmanager-django",
    [switch]$Private = $false
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Repository details
$description = "Django task management application with Azure deployment and CI/CD - 195 tests passing, 88% coverage"

Write-Host "📦 Repository Configuration:" -ForegroundColor Yellow
Write-Host "   Name: $RepoName"
Write-Host "   Description: $description"
Write-Host "   Visibility: $(if ($Private) { 'Private' } else { 'Public' })"
Write-Host ""

# Step 1: Open GitHub new repository page
Write-Host "Step 1: Creating repository on GitHub..." -ForegroundColor Green
Write-Host ""
Write-Host "Opening GitHub in your browser..." -ForegroundColor Cyan
Start-Process "https://github.com/new"
Write-Host ""
Write-Host "Please complete these steps in the browser:" -ForegroundColor Yellow
Write-Host "  1. Repository name: $RepoName" -ForegroundColor White
Write-Host "  2. Description: (will be copied to clipboard)" -ForegroundColor White
Write-Host "  3. Choose $(if ($Private) { 'Private' } else { 'Public' })" -ForegroundColor White
Write-Host "  4. [ ] Do NOT check 'Initialize with README'" -ForegroundColor White
Write-Host "  5. [ ] Do NOT add .gitignore" -ForegroundColor White
Write-Host "  6. [ ] Do NOT choose a license" -ForegroundColor White
Write-Host "  7. Click 'Create repository'" -ForegroundColor White
Write-Host ""

# Copy description to clipboard
Set-Clipboard -Value $description
Write-Host "✓ Description copied to clipboard - paste it in the description field!" -ForegroundColor Green
Write-Host ""

# Wait for user confirmation
Write-Host "Press Enter once you've created the repository on GitHub..." -ForegroundColor Cyan
Read-Host

# Step 2: Get GitHub username
if ([string]::IsNullOrEmpty($Username)) {
    Write-Host ""
    $Username = Read-Host "Enter your GitHub username"
}

$repoUrl = "https://github.com/$Username/$RepoName.git"

Write-Host ""
Write-Host "Step 2: Connecting local repository to GitHub..." -ForegroundColor Green
Write-Host ""

# Add remote
Write-Host "Adding remote 'origin'..." -ForegroundColor Cyan
git remote add origin $repoUrl 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Remote already exists, updating URL..." -ForegroundColor Yellow
    git remote set-url origin $repoUrl
}

# Check current branch
$currentBranch = git branch --show-current
Write-Host "   Current branch: $currentBranch" -ForegroundColor White

# Push to GitHub
Write-Host ""
Write-Host "Step 3: Pushing code to GitHub..." -ForegroundColor Green
Write-Host ""
Write-Host "Pushing to origin/$currentBranch..." -ForegroundColor Cyan
git push -u origin $currentBranch

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ Repository setup complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Your repository is now available at:" -ForegroundColor Cyan
    Write-Host "   https://github.com/$Username/$RepoName" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Configure GitHub Actions secrets" -ForegroundColor White
    Write-Host "   2. Get Azure publish profile" -ForegroundColor White
    Write-Host "   3. Add AZURE_WEBAPP_PUBLISH_PROFILE secret" -ForegroundColor White
    Write-Host ""
    Write-Host "Run the next script:" -ForegroundColor Cyan
    Write-Host "   .\setup-github-secrets.ps1 -Username $Username -RepoName $RepoName" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error pushing to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "   1. Your GitHub username is correct: $Username" -ForegroundColor White
    Write-Host "   2. You have permission to push to the repository" -ForegroundColor White
    Write-Host "   3. Your Git credentials are configured" -ForegroundColor White
    Write-Host ""
    Write-Host "Try running: git push -u origin $currentBranch" -ForegroundColor Cyan
}
