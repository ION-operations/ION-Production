@echo off
REM Volumetric Clouds Engine Launcher Script (Batch)
REM Launches the Volumetric Clouds Engine development server

set PROJECT_PATH=%~dp0
set DEFAULT_PORT=3002

if not exist "%PROJECT_PATH%" (
    echo Error: Project path not found: %PROJECT_PATH%
    exit /b 1
)

echo Volumetric Clouds Engine
echo ========================
echo.
echo Real-time volumetric cloud rendering with terrain, water, and atmospheric effects
echo.

cd /d "%PROJECT_PATH%"

REM Check if package.json exists
if not exist "package.json" (
    echo Error: package.json not found in %PROJECT_PATH%
    exit /b 1
)

REM Check if node_modules exists, if not, run npm install
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo Error: npm install failed
        pause
        exit /b 1
    )
    echo.
)

REM Check for Node.js/npm
where npm >nul 2>&1
if errorlevel 1 (
    echo Error: npm not found. Please install Node.js.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo Starting development server...
echo.
echo The application will open in your browser automatically.
echo Default port: %DEFAULT_PORT%
echo.
echo Controls:
echo   - Drag: Rotate camera
echo   - Shift + Drag: Pan camera
echo   - Scroll: Zoom
echo   - Presets: Select from dropdown menu
echo   - Settings: Adjust parameters in the side panel
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start Vite dev server
call npm run dev

pause
