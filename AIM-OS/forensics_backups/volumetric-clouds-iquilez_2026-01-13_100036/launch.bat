@echo off
REM Inigo Quilez Volumetric Clouds Launcher Script (Batch)
REM Launches the Inigo Quilez volumetric clouds harness development server

set PROJECT_PATH=%~dp0
set PORT=5174

if not exist "%PROJECT_PATH%" (
    echo Error: Project path not found: %PROJECT_PATH%
    exit /b 1
)

echo Inigo Quilez Volumetric Clouds
echo ==============================
echo.
echo WebGL2 harness for Inigo Quilez volumetric cloud shader
echo.

cd /d "%PROJECT_PATH%"

REM Check if index.html exists
if not exist "index.html" (
    echo Error: index.html not found in %PROJECT_PATH%
    exit /b 1
)

REM Check if main.js exists
if not exist "main.js" (
    echo Error: main.js not found in %PROJECT_PATH%
    exit /b 1
)

REM Check if shaders directory exists
if not exist "shaders" (
    echo Error: shaders directory not found in %PROJECT_PATH%
    exit /b 1
)

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Python not found. Trying python3...
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python not found. Please install Python to run this server.
        echo Alternatively, use any HTTP server that serves files from this directory.
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Try to find available port
set PREFERRED_PORT=5174
set ACTUAL_PORT=%PREFERRED_PORT%
set MAX_ATTEMPTS=10
set ATTEMPT=0

:TRY_PORT
netstat -an | find ":%ACTUAL_PORT% " | find "LISTENING" >nul 2>&1
if errorlevel 1 (
    REM Port is available (not in LISTENING state)
    goto START_SERVER
) else (
    REM Port is in use, try next port
    set /a ATTEMPT+=1
    set /a ACTUAL_PORT=%PREFERRED_PORT%+%ATTEMPT%
    if %ATTEMPT% LSS %MAX_ATTEMPTS% (
        echo Port %PREFERRED_PORT% is in use. Trying port %ACTUAL_PORT%...
        goto TRY_PORT
    ) else (
        echo Error: Could not find available port starting from %PREFERRED_PORT%
        pause
        exit /b 1
    )
)

:START_SERVER
echo Starting HTTP server on port %ACTUAL_PORT%...
echo Open http://localhost:%ACTUAL_PORT% in your browser
echo.
echo Note: Requires WebGL2
echo Drag mouse to rotate camera view.
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start HTTP server
echo Starting server...
%PYTHON_CMD% -m http.server %ACTUAL_PORT%
