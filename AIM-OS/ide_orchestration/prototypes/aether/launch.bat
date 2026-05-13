@echo off
REM Aether IDE Prototype Launcher
REM One-click launcher for Windows

echo.
echo ========================================
echo   Aether IDE Prototype Launcher
echo   System Architecture & Deep AIM-OS Integration
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo [INFO] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed!
    echo.
)

REM Start the dev server
echo [INFO] Starting Aether IDE Prototype...
echo [INFO] Server will open automatically at http://localhost:5173
echo [INFO] Press Ctrl+C to stop the server
echo.

call npm run dev

pause
