"""
Test HHNI initialization in actual MCP server
Tests the fixes applied from Sev/Atlas investigation
"""
import sys
import json
import subprocess
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_mcp_hhni_status():
    """Test HHNI status via MCP server"""
    print("\n🧪 Testing HHNI Initialization via MCP Server")
    print("=" * 60)
    
    workspace_root = Path(__file__).parent.parent
    
    # Prepare MCP request
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    tools_list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    get_hhni_status_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_hhni_status",
            "arguments": {}
        }
    }
    
    # Start MCP server process
    print("\n1. Starting MCP Server...")
    try:
        server_process = subprocess.Popen(
            [sys.executable, str(workspace_root / "lucid_mcp_server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(workspace_root),
            env={**os.environ, "PYTHONPATH": str(workspace_root) + ";" + str(workspace_root / "packages")}
        )
        print("   ✅ MCP server process started")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to start MCP server: {e}")
        return False
    
    try:
        # Send initialize request
        print("\n2. Sending initialize request...")
        server_process.stdin.write(json.dumps(initialize_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if response.get("result"):
                print("   ✅ Initialize successful")
            else:
                print(f"   ⚠️  Initialize response: {response}")
        else:
            print("   ⚠️  No initialize response")
        
        # Send tools/list request
        print("\n3. Listing tools...")
        server_process.stdin.write(json.dumps(tools_list_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get("result", {}).get("tools", [])
            tool_names = [t.get("name") for t in tools]
            if "get_hhni_status" in tool_names:
                print(f"   ✅ Found get_hhni_status tool (total tools: {len(tools)})")
            else:
                print(f"   ⚠️  get_hhni_status not found in {len(tools)} tools")
        
        # Send get_hhni_status request
        print("\n4. Testing get_hhni_status tool...")
        server_process.stdin.write(json.dumps(get_hhni_status_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get("result", {})
            
            print("\n   HHNI Status:")
            print(f"   - Index initialized: {result.get('hhni_index_initialized', 'N/A')}")
            print(f"   - Retriever initialized: {result.get('hhni_retriever_initialized', 'N/A')}")
            print(f"   - Index nodes: {result.get('index_nodes', 'N/A')}")
            print(f"   - Index available: {result.get('index_available', 'N/A')}")
            print(f"   - Retriever available: {result.get('retriever_available', 'N/A')}")
            print(f"   - CMC atoms total: {result.get('cmc_atoms_total', 'N/A')}")
            print(f"   - CMC atoms HHNI-tagged: {result.get('cmc_atoms_hhni_tagged', 'N/A')}")
            
            if result.get('init_error'):
                print(f"   - Init error: {result.get('init_error')}")
                print(f"   - Init traceback: {result.get('init_traceback', 'N/A')[:200]}...")
            
            # Check if initialization was successful
            if result.get('hhni_index_initialized') and result.get('index_nodes', 0) > 0:
                print("\n   ✅ HHNI initialization successful!")
                return True
            else:
                print("\n   ⚠️  HHNI initialization may have issues")
                return False
        else:
            print("   ⚠️  No response from get_hhni_status")
            return False
        
    except Exception as e:
        print(f"   ❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Check stderr for any errors
        print("\n5. Checking server logs...")
        try:
            server_process.terminate()
            stderr_output = server_process.stderr.read()
            if stderr_output:
                print("   Server stderr output:")
                print(stderr_output[:500])  # First 500 chars
        except:
            pass
        server_process.wait(timeout=5)

if __name__ == "__main__":
    import os
    success = test_mcp_hhni_status()
    sys.exit(0 if success else 1)

