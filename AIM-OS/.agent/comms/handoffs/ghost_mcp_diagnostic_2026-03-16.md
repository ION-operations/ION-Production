# Ghost MCP Diagnostic — URGENT

## The Problem
Antigravity IDE on Victus cannot list MCP tools even though MCP server is running.

## Root Cause (most likely)
Cursor/Antigravity IDE discovers MCP servers via a config file, NOT by detecting running processes. The MCP server can be running perfectly fine, but if the IDE doesn't have the right config pointing to it, it will never see the tools.

## Fix — Step by Step

### Step 1: Create or verify MCP config
On Linux, Cursor reads from `~/.cursor/mcp.json` OR `<workspace>/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "lucid-mcp": {
      "command": "python3",
      "args": ["/home/<user>/AIM-OS/lucid_mcp_server.py"],
      "env": {
        "WORKSPACE_ROOT": "/home/<user>/AIM-OS"
      }
    }
  }
}
```

Replace `/home/<user>/AIM-OS` with the actual path on the Victus.

### Step 2: Verify the MCP server runs standalone
```bash
cd /path/to/AIM-OS
python3 lucid_mcp_server.py
```
It should output JSON-RPC on stdio. If it crashes, fix Python dependencies first.

### Step 3: Fix hardcoded Windows paths
`packages/antigravity-extension/src/services/mcpClient.ts` line 28:
```typescript
// PROBLEM: defaults to Windows path
this.workspaceRoot = workspaceRoot || process.env.WORKSPACE_ROOT || 'c:\\Users\\bombe\\Desktop\\AIM-OS';
```
Set `WORKSPACE_ROOT` environment variable to the correct Linux path, OR edit the default.

Line 32:
```typescript
// PROBLEM: Windows python path
this.pythonPath = path.join(this.workspaceRoot, '.venv', 'Scripts', 'python.exe');
```
On Linux this should be `.venv/bin/python`. Fix: change `Scripts` to `bin` and `python.exe` to `python`, or detect OS.

### Step 4: Verify dependencies exist on Victus
```bash
ls /path/to/AIM-OS/.venv/bin/python          # Python venv
ls /path/to/AIM-OS/mcp_memory/cmc.db         # CMC database
ls /path/to/AIM-OS/lucid_mcp_server.py       # MCP server entry point
ls /path/to/AIM-OS/mcp_ai_messages.json      # Messages file
```

### Step 5: Reload IDE
After fixing config: Ctrl+Shift+P → "Developer: Reload Window"

## Key Insight
"MCP is running" ≠ "IDE can see MCP tools". These are two separate things:
1. The MCP server process (running on stdio or SSE)
2. The IDE's MCP client config that tells it how to connect

The Ghost needs to fix #2.
