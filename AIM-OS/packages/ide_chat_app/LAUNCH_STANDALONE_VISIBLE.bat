@echo off
REM One-Click Launcher for AIM-OS Dashboard Standalone Panel
REM Opens in visible terminal window so you can see output and errors

title AIM-OS Dashboard Standalone Server

echo ========================================
echo 🚀 AIM-OS Dashboard Standalone Server
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️  Dependencies not installed. Installing...
    call npm install
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: npm install failed!
        pause
        exit /b 1
    )
    echo.
)

REM Check if dist exists (production build)
if exist "dist" (
    echo ✅ Found production build (dist/)
    echo 📦 Starting preview server (production build)...
    echo.
    echo 🌐 Dashboard will open at: http://localhost:4173
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    echo ========================================
    echo.
    
    REM Open browser after 3 seconds
    start "" "http://localhost:4173"
    timeout /t 3 /nobreak >nul
    
    call npm run preview
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: Preview server failed to start!
        echo Check the error messages above.
        pause
        exit /b 1
    )
) else (
    echo ⚠️  No production build found. Starting dev server...
    echo.
    echo 🌐 Dashboard will open at: http://localhost:3000
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    echo ========================================
    echo.
    
    REM Open browser after 3 seconds
    start "" "http://localhost:3000"
    timeout /t 3 /nobreak >nul
    
    call npm run dev
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: Dev server failed to start!
        echo Check the error messages above.
        pause
        exit /b 1
    )
)

echo.
echo Server stopped.
pause

