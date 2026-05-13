#!/bin/bash
# AIM-OS IDE One-Click Launcher
# Automatically finds an open port and launches the IDE

echo ""
echo "========================================"
echo "  AIM-OS IDE Launcher"
echo "  Finding open port and starting..."
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

if [ ! -f "package.json" ]; then
    echo "[ERROR] package.json not found! Make sure you're in the ide_chat_app directory."
    exit 1
fi

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

# Function to check if port is available
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Find an open port starting from 5173
PORT=5173
MAX_PORT=6000

echo "[INFO] Finding an open port..."

while [ $PORT -le $MAX_PORT ]; do
    if ! check_port $PORT; then
        echo "[SUCCESS] Found open port: $PORT"
        break
    else
        echo "[INFO] Port $PORT is in use, trying next port..."
        PORT=$((PORT + 1))
    fi
done

if [ $PORT -gt $MAX_PORT ]; then
    echo "[ERROR] Could not find an open port between 5173-6000!"
    exit 1
fi

echo ""
echo "[INFO] Starting IDE on port $PORT..."
echo "[INFO] Server will open automatically at http://localhost:$PORT"
echo "[INFO] Press Ctrl+C to stop the server"
echo ""

# Start vite with the found port
PORT=$PORT npm run dev -- --port $PORT --host

