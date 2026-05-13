@echo off
echo ========================================
echo   AIM-OS IDE with Lucid Orchestrator
echo ========================================
echo.

echo Starting Lucid Orchestrator daemon...
start "Lucid Daemon" cmd /k "cd packages\lucid_orchestrator\daemon && python http_daemon.py"

echo Waiting for daemon to start...
timeout /t 3 /nobreak > nul

echo Starting IDE with Lucid integration...
cd packages\ide_chat_app

echo Installing dependencies if needed...
call npm install

echo Building and starting IDE...
call npm run dev

echo.
echo ========================================
echo   Lucid IDE is now running!
echo ========================================
echo.
echo IDE: http://localhost:5173
echo Daemon: http://localhost:5000
echo.
echo Press any key to stop both services...
pause > nul

echo Stopping services...
taskkill /f /im "python.exe" 2>nul
taskkill /f /im "node.exe" 2>nul

echo Done!
