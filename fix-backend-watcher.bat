@echo off
REM Quick fix for watchfiles I/O error on Windows Docker
REM Run this if you see "Input/output error (os error 5)" when starting Docker

echo Restarting backend container to fix file watcher...
docker-compose restart backend

echo.
echo Waiting for backend to be healthy...
timeout /t 5 /nobreak > nul

echo.
echo Checking backend logs...
docker-compose logs --tail=20 backend

echo.
echo Done! Backend should be running now.
echo If you still see errors, try: docker-compose down ^&^& docker-compose up -d
