@echo off
REM Electron App Restart Script
REM Closes existing Electron instances and launches fresh

echo Restarting Electron app...

REM Kill any existing Electron processes
taskkill /F /IM electron.exe 2>nul
timeout /t 1 /nobreak >nul

REM Navigate to app directory
cd /d "%~dp0"

REM Launch Electron
echo Launching Electron app...
call npm run electron

pause

