@echo off
cd /d "%~dp0packages\ide_chat_app"
echo Current directory: %CD%
echo.
echo Killing existing Electron processes...
taskkill /F /IM electron.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo.
echo Starting Electron in DEV MODE...
echo.
call npm run electron:dev
pause
