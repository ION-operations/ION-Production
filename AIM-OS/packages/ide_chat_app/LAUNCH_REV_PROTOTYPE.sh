#!/bin/bash
# Port Cleanup & Rev's IDE Launcher
# Checks and kills processes on ports 3000 and 5180 before launching

echo ""
echo "========================================"
echo "  Port Cleanup & Rev's IDE Launcher"
echo "========================================"
echo ""

# Function to kill process on a port
kill_port_process() {
    local port=$1
    local name=$2
    
    echo "Port $port ($name):"
    
    # Find processes using the port
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pids" ]; then
            echo "  Killing processes on port $port: $pids"
            kill -9 $pids 2>/dev/null
            sleep 1
            echo "  Port $port cleared"
        else
            echo "  Port $port is free"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        local pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pids" ]; then
            echo "  Killing processes on port $port: $pids"
            kill -9 $pids 2>/dev/null
            sleep 1
            echo "  Port $port cleared"
        else
            echo "  Port $port is free"
        fi
    else
        echo "  Port check not supported on this OS"
    fi
}

# Check and clean ports
echo "Checking ports..."
echo ""

kill_port_process 3000 "Sam's IDE"
echo ""
kill_port_process 5180 "Rev's IDE"

echo ""
echo "Waiting 2 seconds for ports to release..."
sleep 2

# Change to script directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "Starting Rev's IDE Prototype on port 5180..."
echo "URL: http://localhost:5180/indexRev.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Vite dev server
npm run dev:rev
