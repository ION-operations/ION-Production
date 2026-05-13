"""Test full MCP discovery flow: initialize → initialized → tools/list."""
import subprocess
import json
import sys
import os
import time

server_path = os.path.join('scripts', 'ai_engine', 'ai_engine_mcp_server.py')

proc = subprocess.Popen(
    [sys.executable, '-u', server_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=os.getcwd(),
    env={**os.environ, 'PYTHONPATH': os.getcwd()},
)

def send_msg(msg_dict):
    body = json.dumps(msg_dict).encode('utf-8')
    header = f"Content-Length: {len(body)}\r\n\r\n".encode('utf-8')
    proc.stdin.write(header + body)
    proc.stdin.flush()
    print(f"  >> Sent: {msg_dict.get('method', '?')} (id={msg_dict.get('id')})")

def read_response(timeout=5):
    """Read a Content-Length framed response."""
    start = time.time()
    # Read header
    header = b""
    while time.time() - start < timeout:
        byte = proc.stdout.read(1)
        if not byte:
            return None
        header += byte
        if header.endswith(b"\r\n"):
            break
    
    if not header.startswith(b"Content-Length:"):
        print(f"  << Unexpected header: {header!r}")
        return None
    
    content_len = int(header.decode().split(':')[1].strip())
    
    # Read blank line
    proc.stdout.read(2)  # \r\n
    
    # Read body
    body = proc.stdout.read(content_len)
    result = json.loads(body.decode())
    print(f"  << Response (id={result.get('id')}): {json.dumps(result, indent=2)[:200]}")
    return result

# Step 1: Initialize
print("=== Step 1: initialize ===")
send_msg({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "gemini-cli-test", "version": "1.0"},
    },
})
resp = read_response()

# Step 2: Initialized notification (no id = no response expected)
print("\n=== Step 2: notifications/initialized ===")
send_msg({
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
})
time.sleep(0.2)
print("  (no response expected for notifications)")

# Step 3: List tools
print("\n=== Step 3: tools/list ===")
send_msg({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {},
})
resp = read_response()
if resp and 'result' in resp:
    tools = resp['result'].get('tools', [])
    print(f"\n  Found {len(tools)} tools:")
    for t in tools:
        print(f"    - {t['name']}: {t['description'][:60]}")

# Read stderr
time.sleep(0.5)
stderr_data = b""
while True:
    try:
        import select
        # Windows doesn't support select on pipes, just try to read
        break
    except Exception:
        break

# Cleanup
proc.stdin.close()
proc.terminate()
try:
    proc.wait(timeout=3)
except Exception:
    proc.kill()

print(f"\nExit code: {proc.returncode}")
# Try to get stderr
try:
    stderr = proc.stderr.read()
    if stderr:
        print(f"Stderr: {stderr.decode()}")
except Exception:
    pass
