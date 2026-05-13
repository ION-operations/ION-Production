#!/bin/bash
# DAC IDE Prototype V2 - Launcher Script (Unix/Mac)

echo "🚀 Launching DAC IDE Prototype V2..."
echo ""

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js version: $NODE_VERSION"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please run 'npm install' manually."
        exit 1
    fi
    echo ""
fi

echo "✅ Dependencies ready"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "⚠️  Python not found. Backend server will not start."
    echo "   Install Python 3.8+ from https://www.python.org/"
    echo ""
    PYTHON_CMD=""
fi

if [ -n "$PYTHON_CMD" ]; then
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo "✅ Python found: $PYTHON_VERSION"
    
    # Check if backend is already running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend server already running on port 8000"
    else
        echo "🚀 Starting backend server (port 8000)..."
        
        # Get repo root (go up from ide_orchestration/prototypes/dac)
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
        REPO_ROOT="$SCRIPT_DIR/../../.."
        
        # Check if we're in the right place
        if [ ! -f "$REPO_ROOT/packages/cmc_service/api.py" ]; then
            REPO_ROOT="$SCRIPT_DIR/../../../.."
        fi
        
        BACKEND_DIR="$REPO_ROOT/packages/cmc_service"
        IDE_BACKEND="$REPO_ROOT/ide_orchestration/prototypes/dac/backend_server.py"
        
        if [ -f "$IDE_BACKEND" ]; then
            # Start standalone IDE backend (run from repo root so it can find knowledge_architecture)
            cd "$REPO_ROOT"
            $PYTHON_CMD "$IDE_BACKEND" > /dev/null 2>&1 &
            BACKEND_PID=$!
        elif [ -f "$BACKEND_DIR/api.py" ]; then
            # Fallback to CMC service API (may have dependency issues)
            cd "$BACKEND_DIR"
            $PYTHON_CMD -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 &
            BACKEND_PID=$!
            
            # Wait for backend to start
            MAX_WAIT=10
            WAITED=0
            while [ $WAITED -lt $MAX_WAIT ]; do
                sleep 1
                WAITED=$((WAITED + 1))
                if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                    echo "✅ Backend server started successfully"
                    break
                fi
            done
            
            if [ $WAITED -ge $MAX_WAIT ]; then
                echo "⚠️  Backend server may not have started properly"
            fi
            
            cd "$SCRIPT_DIR"
        else
            echo "⚠️  Backend server files not found at $BACKEND_DIR"
        fi
    fi
    echo ""
fi

echo "Starting development server..."
echo "📍 The IDE will automatically open at http://localhost:3002"
echo "⏹️  Press Ctrl+C to stop all servers"
echo ""

# Trap to cleanup backend on exit
cleanup() {
    if [ -n "$BACKEND_PID" ]; then
        echo ""
        echo "Stopping backend server..."
        kill $BACKEND_PID 2>/dev/null
    fi
    exit
}
trap cleanup INT TERM

# Start the dev server (Vite will auto-open browser)
npm run dev

# Cleanup on exit
cleanup

