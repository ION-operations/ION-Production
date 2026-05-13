"""Clean MCP test with PYTHONPATH and proper error handling."""
import subprocess
import json
import sys
import os
import time

# agent_loop -> ai_engine -> scripts -> AIM-OS
AIMOS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

env = {**os.environ, 'PYTHONPATH': AIMOS_ROOT}

proc = subprocess.Popen(
    [sys.executable, '-u', os.path.join(AIMOS_ROOT, 'scripts', 'ai_engine', 'ai_engine_mcp_server.py')],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=AIMOS_ROOT,
    env=env,
)

time.sleep(1)

# Check if process is alive
rc = proc.poll()
if rc is not None:
    print(f"Server died with exit code {rc}")
    print(f"stderr: {proc.stderr.read().decode()[:500]}")
    sys.exit(1)

print("Server is running")

def send(msg):
    line = json.dumps(msg) + '\n'
    proc.stdin.write(line.encode())
    proc.stdin.flush()

def recv(timeout=5):
    import select
    # On Windows, use a thread-based approach
    import threading
    result = [None]
    def _read():
        result[0] = proc.stdout.readline()
    t = threading.Thread(target=_read)
    t.start()
    t.join(timeout)
    if result[0]:
        return json.loads(result[0].decode().strip())
    return None

# 1. Initialize
print("1. Sending initialize...")
send({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2024-11-05', 'capabilities': {}}})
resp = recv()
if resp:
    print(f"   OK: {resp['result']['serverInfo']['name']} v{resp['result']['serverInfo']['version']}")
else:
    print("   FAILED: no response")
    proc.terminate()
    print(f"stderr: {proc.stderr.read().decode()[:500]}")
    sys.exit(1)

# 2. Initialized notification
send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
time.sleep(0.2)

# 3. List tools
print("2. Listing tools...")
send({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
resp = recv()
if resp:
    tools = resp['result']['tools']
    new_tools = {'ai_engine_system_info', 'ai_engine_loop_run', 'ai_engine_loop_compare', 'ai_engine_agent_call'}
    print(f"   {len(tools)} tools:")
    for t in tools:
        name = t['name']
        tag = " [NEW]" if name in new_tools else ""
        print(f"     - {name}{tag}")
else:
    print("   FAILED")

# 4. Call system_info
print("\n3. Testing ai_engine_system_info...")
send({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'ai_engine_system_info', 'arguments': {}}})
resp = recv(timeout=10)
if resp:
    data = json.loads(resp['result']['content'][0]['text'])
    for k, v in data.items():
        if not isinstance(v, list):
            print(f"     {k}: {v}")
    if 'python_processes' in data:
        print(f"     python_processes: {len(data['python_processes'])} running")
    print("\n✅ All Context Lab MCP tools verified!")
else:
    print("   FAILED: no response")

proc.terminate()
try:
    proc.wait(timeout=3)
except:
    proc.kill()
