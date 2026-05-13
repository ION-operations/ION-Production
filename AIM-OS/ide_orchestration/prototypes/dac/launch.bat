@echo off
REM DAC IDE Prototype V2 - Launcher Script (Windows Batch)
echo.
echo 🚀 Launching DAC IDE Prototype V2...
echo.

REM Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js version: %NODE_VERSION%

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️  node_modules not found. Installing dependencies...
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to install dependencies. Please run 'npm install' manually.
        pause
        exit /b 1
    )
    echo.
)

echo ✅ Dependencies ready
echo.

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    goto :check_backend
)
where python3 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python3
    goto :check_backend
)
echo ⚠️  Python not found. Backend server will not start.
echo    Install Python 3.8+ from https://www.python.org/
echo.
goto :start_frontend

:check_backend
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%

REM Check if backend is already running
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Backend server already running on port 8000
    goto :start_frontend
)

echo 🚀 Starting backend server (port 8000)...

REM Get repo root (go up from ide_orchestration/prototypes/dac)
set REPO_ROOT=%~dp0..\..\..
if not exist "%REPO_ROOT%\packages\cmc_service\api.py" (
    set REPO_ROOT=%~dp0..\..\..\..
)
set BACKEND_DIR=%REPO_ROOT%\packages\cmc_service
set IDE_BACKEND=%REPO_ROOT%\ide_orchestration\prototypes\dac\backend_server.py

if exist "%IDE_BACKEND%" (
    REM Start standalone IDE backend (run from repo root so it can find knowledge_architecture)
    cd /d "%REPO_ROOT%"
    start /B "" %PYTHON_CMD% "%IDE_BACKEND%"
) else if exist "%BACKEND_DIR%\api.py" (
    REM Fallback to CMC service API (may have dependency issues)
    start /B "" %PYTHON_CMD% -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
    REM Wait a moment for backend to start
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:8000/health >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo ✅ Backend server started successfully
    ) else (
        echo ⚠️  Backend server may not have started properly
    )
) else (
    echo ⚠️  Backend server files not found at %BACKEND_DIR%
)
echo.

:start_frontend
echo Starting development server...
echo 📍 The IDE will automatically open at http://localhost:3002
echo ⏹️  Press Ctrl+C to stop all servers
echo.

REM Start the dev server (Vite will auto-open browser)
call npm run dev

pause

