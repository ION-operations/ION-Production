#!/usr/bin/env python3
"""
Launch script for Lucid Orchestrator Daemon
"""

import sys
import os
import subprocess
import time

def main():
    """Launch the Lucid Daemon with proper setup."""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    daemon_script = os.path.join(script_dir, 'lucid_daemon.py')
    
    # Check if the daemon script exists
    if not os.path.exists(daemon_script):
        print(f"Error: Daemon script not found at {daemon_script}")
        sys.exit(1)
    
    # Check if required packages are installed
    try:
        import websockets
        print("✓ websockets package found")
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'websockets'])
        print("✓ Required packages installed")
    
    print("Starting Lucid Orchestrator Daemon...")
    print("WebSocket URL: ws://localhost:8765")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Run the daemon
        subprocess.run([sys.executable, daemon_script], check=True)
    except KeyboardInterrupt:
        print("\nDaemon stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Daemon exited with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
