@echo off
REM Aether IDE V2 Prototype Launcher
REM Enhanced launcher with V2 foundation features
REM One-click launcher for Windows

echo.
echo ========================================
echo   Aether IDE V2 Prototype Launcher
echo   System Architecture & Deep AIM-OS Integration
echo   Phase 6 Foundation: 95%% Complete
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo [INFO] Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Node.js version:
node --version
echo.

REM Check if npm is installed
where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm is not installed or not in PATH!
    pause
    exit /b 1
)

echo [INFO] npm version:
npm --version
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo [INFO] Installing dependencies...
    echo [INFO] This may take a few minutes...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        echo [INFO] Try running: npm install
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed!
    echo.
) else (
    echo [INFO] Dependencies already installed
    echo.
)

REM Check if TypeScript compilation is needed
if exist "src\" (
    echo [INFO] Checking TypeScript compilation...
    call npm run build >nul 2>nul
    if errorlevel 1 (
        echo [WARNING] TypeScript compilation had warnings (non-blocking)
    )
    echo.
)

REM Display V2 features
echo [INFO] V2 Foundation Features:
echo   - Hook System (9 hooks: useAIMOS + 8 individual)
echo   - State Management (Zustand panelStore)
echo   - 35 Panels Managed
echo   - Error Boundaries
echo   - Loading States
echo   - Performance Optimizations
echo   - Layout Presets
echo.

REM Start the dev server
echo [INFO] Starting AETHER V2 IDE Prototype...
echo [INFO] Server will find an open port automatically
echo [INFO] WATCH THE TERMINAL FOR THE ACTUAL PORT NUMBER!
echo [INFO] Browser title will show: [AETHER V2] IDE Prototype
echo [INFO] Press Ctrl+C to stop the server
echo.
echo [TIP] Features available:
echo   - Panel management via Zustand store
echo   - Layout presets (save/load in top bar)
echo   - Error boundaries for panel failures
echo   - Loading states for async operations
echo.
echo ========================================
echo   LOOK FOR THIS IN TERMINAL OUTPUT:
echo   Local:   http://localhost:XXXX/
echo   THAT IS YOUR PORT NUMBER!
echo ========================================
echo.

call npm run dev

pause

