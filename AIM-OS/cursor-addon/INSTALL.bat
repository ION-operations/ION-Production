@echo off
echo ========================================
echo Installing AIM-OS Extension v1.2.0
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Building extension...
call npm run build
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Packaging extension...
call npm run package
if errorlevel 1 (
    echo Package failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Checking extension file...
if exist "aimos-cursor-addon.vsix" (
    echo Extension file found!
    echo.
    echo ========================================
    echo INSTALLATION OPTIONS:
    echo ========================================
    echo.
    echo Option 1: Manual Installation (Recommended)
    echo   1. Open Cursor
    echo   2. Press Ctrl+Shift+X
    echo   3. Click ... menu ^(top right^)
    echo   4. Select "Install from VSIX..."
    echo   5. Navigate to: %CD%\aimos-cursor-addon.vsix
    echo   6. Select file and install
    echo   7. Restart Cursor
    echo.
    echo Option 2: Command Line (if code command works)
    echo   code --install-extension "%CD%\aimos-cursor-addon.vsix" --force
    echo.
    echo ========================================
    pause
) else (
    echo Extension file not found!
    pause
    exit /b 1
)

