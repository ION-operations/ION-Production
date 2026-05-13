@echo off
REM AIM-OS IDE One-Click Launcher
REM Automatically finds an open port and launches the IDE

echo.
echo ========================================
echo   AIM-OS IDE Launcher
echo   Finding open port and starting...
echo ========================================
echo.

REM Change to the ide_chat_app directory
cd /d "%~dp0"
if not exist "package.json" (
    echo [ERROR] package.json not found! Make sure you're in the ide_chat_app directory.
    pause
    exit /b 1
)

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

REM Function to check if port is available
echo [INFO] Finding an open port...
set PORT=5173
set FOUND=0

:CHECK_PORT
netstat -an | findstr ":%PORT%" >nul
if errorlevel 1 (
    set FOUND=1
    echo [SUCCESS] Found open port: %PORT%
    goto :START_SERVER
) else (
    echo [INFO] Port %PORT% is in use, trying next port...
    set /a PORT+=1
    if %PORT% GTR 6000 (
        echo [ERROR] Could not find an open port between 5173-6000!
        pause
        exit /b 1
    )
    goto :CHECK_PORT
)

:START_SERVER
echo.
echo [INFO] Starting IDE on port %PORT%...
echo [INFO] Server will open automatically at http://localhost:%PORT%
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Set the port environment variable and start vite
set PORT=%PORT%
call npm run dev -- --port %PORT% --host

pause

