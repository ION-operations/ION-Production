@echo off
REM IDE Prototype Launcher - Max
REM One-click launcher for the Panel-First Design prototype

echo 🚀 Launching IDE Prototype - Max (Panel-First Design)
echo.

REM Check if node_modules exists
if not exist "node_modules" (
  echo 📦 Installing dependencies...
  call npm install
  echo.
)

echo 🎨 Starting development server...
echo 📍 Prototype will be available at: http://localhost:3002
echo.

call npm run dev

