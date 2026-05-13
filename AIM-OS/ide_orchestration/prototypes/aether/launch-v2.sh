#!/bin/bash
# Aether IDE V2 Prototype Launcher
# Enhanced launcher with V2 foundation features
# One-click launcher for Linux/Mac

echo ""
echo "========================================"
echo "  Aether IDE V2 Prototype Launcher"
echo "  System Architecture & Deep AIM-OS Integration"
echo "  Phase 6 Foundation: 95% Complete"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed or not in PATH!"
    echo "[INFO] Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "[INFO] Node.js version:"
node --version
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm is not installed or not in PATH!"
    exit 1
fi

echo "[INFO] npm version:"
npm --version
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "[INFO] Installing dependencies..."
    echo "[INFO] This may take a few minutes..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        echo "[INFO] Try running: npm install"
        exit 1
    fi
    echo "[SUCCESS] Dependencies installed!"
    echo ""
else
    echo "[INFO] Dependencies already installed"
    echo ""
fi

# Check if TypeScript compilation is needed
if [ -d "src" ]; then
    echo "[INFO] Checking TypeScript compilation..."
    npm run build > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "[WARNING] TypeScript compilation had warnings (non-blocking)"
    fi
    echo ""
fi

# Display V2 features
echo "[INFO] V2 Foundation Features:"
echo "  - Hook System (9 hooks: useAIMOS + 8 individual)"
echo "  - State Management (Zustand panelStore)"
echo "  - 35 Panels Managed"
echo "  - Error Boundaries"
echo "  - Loading States"
echo "  - Performance Optimizations"
echo "  - Layout Presets"
echo ""

# Start the dev server
echo "[INFO] Starting AETHER V2 IDE Prototype..."
echo "[INFO] Server will find an open port automatically"
echo "[INFO] WATCH THE TERMINAL FOR THE ACTUAL PORT NUMBER!"
echo "[INFO] Browser title will show: [AETHER V2] IDE Prototype"
echo "[INFO] Press Ctrl+C to stop the server"
echo ""
echo "[TIP] Features available:"
echo "  - Panel management via Zustand store"
echo "  - Layout presets (save/load in top bar)"
echo "  - Error boundaries for panel failures"
echo "  - Loading states for async operations"
echo ""
echo "========================================"
echo "  LOOK FOR THIS IN TERMINAL OUTPUT:"
echo "  Local:   http://localhost:XXXX/"
echo "  THAT IS YOUR PORT NUMBER!"
echo "========================================"
echo ""

npm run dev

