@echo off
REM One-Click Launcher for AIM-OS Dashboard Standalone Panel
REM Launches the dashboard in your default browser

echo ========================================
echo 🚀 AIM-OS Dashboard Standalone Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️  Dependencies not installed. Installing...
    call npm install
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
    
    REM Start preview server and open browser after 3 seconds
    start "" "http://localhost:4173"
    timeout /t 3 /nobreak >nul
    call npm run preview
) else (
    echo ⚠️  No production build found. Starting dev server...
    echo.
    echo 🌐 Dashboard will open at: http://localhost:3000
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    
    REM Start dev server and open browser after 3 seconds
    start "" "http://localhost:3000"
    timeout /t 3 /nobreak >nul
    call npm run dev
)

