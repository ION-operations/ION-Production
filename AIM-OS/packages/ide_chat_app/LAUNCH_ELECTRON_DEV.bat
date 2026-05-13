@echo off
REM ========================================
REM 🚀 AIM-OS Electron App - DEV MODE Launcher (No Build Required)
REM ========================================
REM Launches Electron in dev mode - uses Vite dev server (no build needed)
REM Much faster than production build!

echo.
echo ========================================
echo 🚀 AIM-OS Electron App - DEV MODE
echo ========================================
echo.
echo     Starting in DEV MODE (no build required)
echo     This will start Vite dev server automatically
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Kill existing Electron instances
echo [1/3] Closing existing Electron instances...
tasklist /FI "IMAGENAME eq electron.exe" 2>NUL | find /I /N "electron.exe">NUL
if "%ERRORLEVEL%"=="0" (
    taskkill /F /IM electron.exe >nul 2>&1
    timeout /t 1 /nobreak >nul
    echo     ✅ Closed existing instances
) else (
    echo     ✅ No existing instances
)
echo.

REM Check dependencies
echo [2/3] Checking dependencies...
if not exist "node_modules" (
    echo     ⚠️  Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo     ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo     ✅ Dependencies installed
) else (
    echo     ✅ Dependencies found
)
echo.

REM Launch in dev mode
echo [3/3] Launching Electron in DEV MODE...
echo.
echo ========================================
echo 🚀 Starting AIM-OS Electron App...
echo ========================================
echo.
echo     DevTools will open automatically
echo     Close this window to stop the app
echo.

call npm run electron:dev

if errorlevel 1 (
    echo.
    echo ❌ Electron app exited with an error
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Electron app closed normally
)

