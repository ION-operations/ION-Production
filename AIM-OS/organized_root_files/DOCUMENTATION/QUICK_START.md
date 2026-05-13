# Quick Electron Dev Launcher
# Copy and paste this into PowerShell terminal

cd packages\ide_chat_app
taskkill /F /IM electron.exe 2>$null
npm run electron:dev

