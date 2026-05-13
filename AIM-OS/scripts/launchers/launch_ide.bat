@echo off
echo.
echo ========================================
echo    AIM-OS IDE Launcher
echo ========================================
echo.
echo Starting IDE Chat App...
echo.

cd /d "%~dp0"

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "packages\ide_chat_app\package.json" (
    echo ERROR: IDE package.json not found
    echo Please run this script from the AIM-OS root directory
    pause
    exit /b 1
)

REM Navigate to IDE directory
cd packages\ide_chat_app

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the development server
echo Starting development server...
echo.
echo The IDE will open in your default browser.
echo Press Ctrl+C to stop the server.
echo.

npm run dev

pause
