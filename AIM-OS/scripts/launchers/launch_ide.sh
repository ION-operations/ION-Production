#!/bin/bash

echo ""
echo "========================================"
echo "    AIM-OS IDE Launcher"
echo "========================================"
echo ""
echo "Starting IDE Chat App..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "packages/ide_chat_app/package.json" ]; then
    echo "ERROR: IDE package.json not found"
    echo "Please run this script from the AIM-OS root directory"
    exit 1
fi

# Navigate to IDE directory
cd packages/ide_chat_app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Start the development server
echo "Starting development server..."
echo ""
echo "The IDE will open in your default browser."
echo "Press Ctrl+C to stop the server."
echo ""

npm run dev
