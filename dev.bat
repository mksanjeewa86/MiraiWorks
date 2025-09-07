@echo off
echo MiraiWorks Development Helper
echo ==============================
echo.

if "%1"=="" (
    echo Usage: dev.bat [command]
    echo.
    echo Commands:
    echo   up      - Start all services in development mode
    echo   down    - Stop all services
    echo   restart - Restart all services
    echo   logs    - Show logs for all services
    echo   backend - Show backend logs only
    echo   frontend- Show frontend logs only
    echo   rebuild - Rebuild and restart services
    echo   status  - Show container status
    echo.
    goto :eof
)

if "%1"=="up" (
    echo Starting development environment...
    docker compose up -d
    goto :eof
)

if "%1"=="down" (
    echo Stopping development environment...
    docker compose down
    goto :eof
)

if "%1"=="restart" (
    echo Restarting development environment...
    docker compose restart
    goto :eof
)

if "%1"=="logs" (
    echo Showing logs for all services...
    docker compose logs -f
    goto :eof
)

if "%1"=="backend" (
    echo Showing backend logs...
    docker compose logs -f backend
    goto :eof
)

if "%1"=="frontend" (
    echo Showing frontend logs...
    docker compose logs -f frontend
    goto :eof
)

if "%1"=="rebuild" (
    echo Rebuilding and restarting...
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    goto :eof
)

if "%1"=="status" (
    echo Checking container status...
    docker compose ps
    goto :eof
)

echo Unknown command: %1
echo Run "dev.bat" to see available commands.