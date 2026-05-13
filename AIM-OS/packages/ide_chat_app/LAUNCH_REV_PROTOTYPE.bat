@echo off
REM Port Cleanup & Rev's IDE Launcher
REM Checks and kills processes on ports 3000 and 5180 before launching

echo.
echo ========================================
echo   Port Cleanup ^& Rev's IDE Launcher
echo ========================================
echo.

REM Function to kill process on a port (Windows)
echo Checking ports...
echo.

echo Port 3000 (Sam's IDE):
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000"') do (
    echo   Killing process on port 3000: PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo Port 5180 (Rev's IDE):
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5180"') do (
    echo   Killing process on port 5180: PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo Waiting 2 seconds for ports to release...
timeout /t 2 /nobreak >nul

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Rev's IDE Prototype on port 5180...
echo URL: http://localhost:5180/indexRev.html
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Vite dev server
call npm run dev:rev

pause
