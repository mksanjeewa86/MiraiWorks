# MiraiWorks Seed Data Runner
# This script runs the seed data creation script with proper environment setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MiraiWorks Seed Data Runner" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "backend\app\seed_data.py")) {
    Write-Host "ERROR: Please run this script from the MiraiWorks project root directory" -ForegroundColor Red
    Write-Host "Expected file: backend\app\seed_data.py" -ForegroundColor Red
    exit 1
}

# Change to backend directory
Write-Host "Navigating to backend directory..." -ForegroundColor Green
Set-Location backend

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Using Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python and add it to PATH" -ForegroundColor Red
    exit 1
}

# Run the seed script
Write-Host ""
Write-Host "Running seed data script..." -ForegroundColor Yellow
Write-Host "This will DELETE all existing seed data and create fresh data!" -ForegroundColor Red
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to continue? (y/N)"
if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "Cancelled by user." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting seed data creation..." -ForegroundColor Green

# Set PYTHONPATH and run the script
$env:PYTHONPATH = "."
try {
    python app\seed_data.py
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   Seed data created successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now use these credentials:" -ForegroundColor Cyan
        Write-Host "  Super Admin: superadmin@miraiworks.com / password" -ForegroundColor White
        Write-Host "  All users have password: 'password'" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "ERROR: Seed script failed with exit code $exitCode" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Failed to run seed script: $_" -ForegroundColor Red
    exit 1
} finally {
    # Return to original directory
    Set-Location ..
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")