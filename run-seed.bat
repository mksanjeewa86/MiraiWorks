@echo off
REM MiraiWorks Seed Data Runner (Batch Version)
title MiraiWorks Seed Data Runner

echo ========================================
echo    MiraiWorks Seed Data Runner
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "backend\app\seed_data.py" (
    echo ERROR: Please run this script from the MiraiWorks project root directory
    echo Expected file: backend\app\seed_data.py
    pause
    exit /b 1
)

echo Navigating to backend directory...
cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python and add it to PATH
    pause
    exit /b 1
)

echo.
echo Running seed data script...
echo WARNING: This will DELETE all existing seed data and create fresh data!
echo.

REM Ask for confirmation
set /p confirmation="Do you want to continue? (y/N): "
if /i not "%confirmation%"=="y" (
    echo Cancelled by user.
    pause
    exit /b 0
)

echo.
echo Starting seed data creation...

REM Set PYTHONPATH and run the script
set PYTHONPATH=.
python app\seed_data.py

if errorlevel 1 (
    echo.
    echo ERROR: Seed script failed
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo    Seed data created successfully!
    echo ========================================
    echo.
    echo You can now use these credentials:
    echo   Super Admin: superadmin@miraiworks.com / password
    echo   All users have password: 'password'
)

echo.
pause