@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  J.A.R.V.I.S. — Joint AI Research & Visualization Intelligence System
REM  One-click launcher for the AIM-OS command surface
REM ═══════════════════════════════════════════════════════════════════

title J.A.R.V.I.S. v2.0 — AIM-OS Command Surface

echo.
echo.
echo       ____. _____  __________  ____   ____.___.  _________
echo      ^|    ^|/  _  \ \______   \ \   \ /   /^|   ^|/   _____/
echo      ^|    /  /_\  \ ^|       _/  \   Y   / ^|   ^|\_____  \
echo  ^|   ^|   /    ^|    \^|    ^|   \   \     /  ^|   ^|/        \
echo  ^|___^|___\____^|__  /^|____^|   /    \___/   ^|___/_______  /
echo                  \/        \/                         \/
echo.
echo   ╔═══════════════════════════════════════════════════════════╗
echo   ║  Joint AI Research ^& Visualization Intelligence System   ║
echo   ║  AIM-OS Command Surface v2.0                             ║
echo   ║                                                           ║
echo   ║  Powering: 14 Subsystems ^| 92 MCP Tools ^| 6 Agents       ║
echo   ╚═══════════════════════════════════════════════════════════╝
echo.

REM Navigate to JOC package
cd /d "%~dp0..\..\packages\joc"

echo   [1/3] Checking dependencies...
if not exist "node_modules" (
    echo          Installing dependencies...
    call npm install
) else (
    echo          Dependencies OK
)

echo.
echo   ──────────────────────────────────────────────────────────────
echo   To stop this app: press Ctrl+C in this window, then close it.
echo   Do NOT close with X alone or the app keeps running.
echo   If PC is slow later: run apps\KILL_ORPHAN_DEV_APPS.bat
echo   ──────────────────────────────────────────────────────────────
echo.
echo   [2/3] Launching J.A.R.V.I.S. surface...
echo.
echo   Mode: %1
if "%1"=="electron" (
    echo   Starting Electron desktop shell...
    call npm run electron:dev
) else if "%1"=="build" (
    echo   Building production bundle...
    call npm run build
) else (
    echo   Starting Vite dev server on http://localhost:5011
    call npm run dev
)

echo.
echo   [3/3] J.A.R.V.I.S. terminated.
pause
