@echo off
REM Launch ONLY Aether IDE V2 - Kills all other Node processes first
echo [INFO] Stopping all Node processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [INFO] Launching Aether IDE V2...
cd ide_orchestration\prototypes\aether
call launch-v2.bat

