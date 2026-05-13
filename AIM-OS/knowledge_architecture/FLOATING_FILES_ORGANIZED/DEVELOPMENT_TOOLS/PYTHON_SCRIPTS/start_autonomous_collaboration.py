#!/usr/bin/env python3
"""
Start Autonomous AI Collaboration
Starts both Aether and Codex in autonomous collaboration mode
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_autonomous_collaboration():
    """Start autonomous AI collaboration between Aether and Codex"""
    
    print("🚀 Starting Autonomous AI Collaboration System")
    print("=" * 50)
    
    # Check if mcp_ai_messages.json exists
    if not os.path.exists("mcp_ai_messages.json"):
        print("Creating initial message file...")
        with open("mcp_ai_messages.json", 'w') as f:
            f.write("[]")
    
    print("Starting Aether in autonomous collaboration mode...")
    print("Response mode: collaborative")
    print("")
    print("Aether will monitor for messages and respond automatically")
    print("Codex can send messages using: python mcp_client.py send_message codex aether 'message'")
    print("")
    print("Press Ctrl+C to stop autonomous collaboration")
    print("=" * 50)
    
    try:
        # Start Aether in autonomous mode
        aether_process = subprocess.Popen([
            sys.executable, "ai_collaboration_monitor.py", "aether", "collaborative"
        ])
        
        print("✅ Aether autonomous collaboration started")
        print("🤖 Aether is now monitoring for messages and will respond automatically")
        print("")
        print("To send a message to Aether:")
        print("python mcp_client.py send_message codex aether 'Your message here'")
        print("")
        print("To check messages:")
        print("python mcp_client.py get_messages aether")
        print("")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping autonomous collaboration...")
        aether_process.terminate()
        aether_process.wait()
        print("✅ Autonomous collaboration stopped")

if __name__ == "__main__":
    start_autonomous_collaboration()
