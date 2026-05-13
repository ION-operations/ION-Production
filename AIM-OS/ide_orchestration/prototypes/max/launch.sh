#!/bin/bash
# IDE Prototype Launcher - Max
# One-click launcher for the Panel-First Design prototype

echo "🚀 Launching IDE Prototype - Max (Panel-First Design)"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
  echo ""
fi

echo "🎨 Starting development server..."
echo "📍 Prototype will be available at: http://localhost:3002"
echo ""

npm run dev

