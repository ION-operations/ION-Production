@echo off
REM ========================================
REM 🚀 AIM-OS Electron App - One-Click Launcher
REM ========================================
REM Kills existing instances, checks dependencies, builds if needed, launches
REM
REM Usage: Double-click this file or run from command line
REM Location: packages/ide_chat_app/LAUNCH_ELECTRON.bat

echo.
echo ========================================
echo 🚀 AIM-OS Electron App Launcher
echo ========================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Step 1: Kill existing Electron instances
echo [1/5] Checking for existing Electron instances...
tasklist /FI "IMAGENAME eq electron.exe" 2>NUL | find /I /N "electron.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo     ⚠️  Found running Electron processes. Closing them...
    taskkill /F /IM electron.exe >nul 2>&1
    timeout /t 1 /nobreak >nul
    echo     ✅ Existing instances closed
) else (
    echo     ✅ No existing instances found
)
echo.

REM Step 2: Check if node_modules exists
echo [2/5] Checking dependencies...
if not exist "node_modules" (
    echo     ⚠️  Dependencies not installed. Installing...
    echo     (This may take a few minutes...)
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

REM Step 3: Check if Electron is installed
echo [3/5] Checking Electron installation...
call npm list electron >nul 2>&1
if errorlevel 1 (
    echo     ⚠️  Electron not found. Installing...
    call npm install --save-dev electron
    if errorlevel 1 (
        echo     ❌ Failed to install Electron
        pause
        exit /b 1
    )
    echo     ✅ Electron installed
) else (
    echo     ✅ Electron found
)
echo.

REM Step 4: Check if build exists
echo [4/5] Checking build status...
if exist "dist" (
    echo     ✅ Found production build (dist/)
) else (
    echo     ⚠️  No production build found. Building now...
    echo     (This may take 1-2 minutes...)
    call npm run build
    if errorlevel 1 (
        echo     ❌ Build failed
        pause
        exit /b 1
    )
    echo     ✅ Build completed
)
echo.

REM Step 5: Launch Electron
echo [5/5] Launching Electron app...
echo.
echo ========================================
echo 🚀 Starting AIM-OS Electron App...
echo ========================================
echo.
echo     The app window should open shortly.
echo     Close this window to stop the app.
echo.

call npm run electron

REM If Electron exits, check exit code
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
