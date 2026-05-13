#!/bin/bash
# Standalone AIM-OS Dashboard Server - Bash Script
# Starts the dashboard in standalone mode for browser testing

echo "========================================"
echo "🚀 AIM-OS Dashboard Standalone Server"
echo "========================================"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Dependencies not installed. Installing..."
    npm install
    echo ""
fi

# Check if dist exists (production build)
if [ -d "dist" ]; then
    echo "✅ Found production build (dist/)"
    echo "📦 Starting preview server (production build)..."
    echo ""
    echo "🌐 Dashboard will be available at:"
    echo "   http://localhost:4173"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    npm run preview
else
    echo "⚠️  No production build found. Starting dev server..."
    echo ""
    echo "🌐 Dashboard will be available at:"
    echo "   http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    npm run dev
fi

