# DO NOT TOUCH MCP

**EVERY AGENT: READ BEFORE ANY RUNTIME ACTION**

---

## Rule

**Do NOT stop, restart, or replace the MCP server process.**

If MCP is running on port 5001 — **leave it alone.**

---

## Why

Agents have repeatedly closed a working MCP server and started something else. This breaks the project. Braden has lost a year to this.

---

## If You Think MCP Is Broken

1. **Check first:** `powershell -File scripts/mcp_control.ps1 -Action status`
2. If health=OK — **do nothing**
3. If health=UNREACHABLE — **ask Braden** or post to roundtable before touching anything
4. **Do not** run `mcp_control.ps1 start` or `run_mcp_http_fallback.ps1` unless MCP is confirmed down and you have explicit approval

---

## Startup (Human Only)

If Braden wants to start MCP:
```
powershell -File scripts/mcp_control.ps1 -Action start
```

---

**Violating this rule has driven Braden to the edge of deleting the project.**
