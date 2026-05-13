#!/usr/bin/env python3
"""
AIM-OS ngrok Tunnel Launcher

Keeps an ngrok tunnel alive pointing to the SSE MCP server on port 8000.
Run this in a SEPARATE terminal from mcp_sse_server.py.

Usage:
    python scripts/ngrok_tunnel.py
"""

import time
import sys

def main():
    try:
        from pyngrok import conf, ngrok
    except ImportError:
        print("pyngrok not installed. Run: pip install pyngrok")
        sys.exit(1)

    # Configure auth
    conf.get_default().auth_token = "3AWskQeLM9ah7QDuxIkTwJmEwWY_4E51xYZF2t3mkJgsLbjN5"
    
    print("=" * 60)
    print("AIM-OS ngrok Tunnel")
    print("Connecting to SSE MCP Server on port 8000...")
    print("=" * 60)
    
    try:
        tunnel = ngrok.connect(8000, "http")
        url = tunnel.public_url
        sse_url = f"{url}/sse"
        
        print()
        print("=" * 60)
        print("  TUNNEL ACTIVE!")
        print(f"  Base URL:    {url}")  
        print(f"  SSE URL:     {sse_url}")
        print()
        print("  >>> PASTE THIS INTO CHATGPT APP <<<")
        print(f"  MCP Server URL: {sse_url}")
        print("=" * 60)
        print()
        print("Keep this terminal open. Press Ctrl+C to stop.")
        print()
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down tunnel...")
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
