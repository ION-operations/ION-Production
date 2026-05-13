#!/bin/bash
# Aether IDE Prototype Launcher
# One-click launcher for Unix/Linux/Mac

echo ""
echo "========================================"
echo "  Aether IDE Prototype Launcher"
echo "  System Architecture & Deep AIM-OS Integration"
echo "========================================"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "[INFO] Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
    echo "[SUCCESS] Dependencies installed!"
    echo ""
fi

# Start the dev server
echo "[INFO] Starting Aether IDE Prototype..."
echo "[INFO] Server will open automatically at http://localhost:5173"
echo "[INFO] Press Ctrl+C to stop the server"
echo ""

npm run dev
