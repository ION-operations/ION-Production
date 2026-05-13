"""
Test MCP Server HHNI Initialization
Tests HHNI initialization in actual MCP server context
"""
import sys
import json
import subprocess
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_mcp_server():
    """Test MCP server HHNI initialization"""
    print("\n🧪 Testing MCP Server HHNI Initialization")
    print("=" * 60)
    
    workspace_root = Path(__file__).parent.parent
    
    # Prepare requests
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_hhni_status",
                "arguments": {}
            }
        }
    ]
    
    # Start server
    print("\n1. Starting MCP Server...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(workspace_root) + os.pathsep + str(workspace_root / "packages")
    
    try:
        proc = subprocess.Popen(
            [sys.executable, str(workspace_root / "lucid_mcp_server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(workspace_root),
            env=env,
            bufsize=1
        )
        print("   ✅ Server process started")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    try:
        # Send requests
        for req in requests:
            proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()
        
        # Read responses
        print("\n2. Reading responses...")
        responses = []
        for i in range(3):
            line = proc.stdout.readline()
            if line:
                try:
                    resp = json.loads(line.strip())
                    responses.append(resp)
                except:
                    pass
        
        # Check initialize
        if responses and responses[0].get("result"):
            print("   ✅ Initialize successful")
        
        # Check tools list
        if len(responses) > 1:
            tools = responses[1].get("result", {}).get("tools", [])
            tool_names = [t.get("name") for t in tools]
            if "get_hhni_status" in tool_names:
                print(f"   ✅ Found get_hhni_status tool")
            else:
                print(f"   ⚠️  get_hhni_status not found")
        
        # Check HHNI status
        if len(responses) > 2:
            result = responses[2].get("result", {})
            print("\n3. HHNI Status:")
            print(f"   - Index initialized: {result.get('hhni_index_initialized')}")
            print(f"   - Retriever initialized: {result.get('hhni_retriever_initialized')}")
            print(f"   - Index nodes: {result.get('index_nodes')}")
            print(f"   - CMC atoms total: {result.get('cmc_atoms_total')}")
            print(f"   - CMC atoms HHNI-tagged: {result.get('cmc_atoms_hhni_tagged')}")
            
            if result.get('init_error'):
                print(f"\n   ⚠️  Init error: {result.get('init_error')}")
            
            if result.get('hhni_index_initialized') and result.get('index_nodes', 0) > 0:
                print("\n   ✅ HHNI initialization successful!")
                return True
        
        # Check stderr for logs
        print("\n4. Checking server logs...")
        import select
        import time
        time.sleep(0.5)  # Give server time to log
        # Read any available stderr
        while True:
            try:
                line = proc.stderr.readline()
                if not line:
                    break
                if "HHNI" in line or "ERROR" in line or "WARNING" in line:
                    print(f"   {line.strip()}")
            except:
                break
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            pass
    
    return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)

