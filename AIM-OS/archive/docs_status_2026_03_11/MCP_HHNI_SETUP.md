# MCP HHNI Setup (retrieve_memory, index_atoms_in_hhni)

## Enable HHNI

**Do not add user-lucid-mcp** — you already have lucid-mcp with 94 tools. Edit your **existing** lucid-mcp server (Option C) or switch to the launcher (Option B).

If adding from scratch (server was removed), use these values:
- **Name:** (do not add — use existing lucid-mcp)
- **Command:** `python`
- **Args:** `-u`, `C:/Users/bombe/OneDrive/Desktop/AIM-OS/lucid_mcp_server.py`
- **Env:** Add `HHNI_LOCAL=1` and `MCP_MEMORY_DIR=C:/Users/bombe/OneDrive/Desktop/AIM-OS/mcp_memory`

If the UI doesn’t support env, use the launcher instead:
- **Command:** `pwsh`
- **Args:** `-File`, `C:/Users/bombe/OneDrive/Desktop/AIM-OS/scripts/run_mcp_dev.ps1`

---

## Option B: Use launcher script (recommended)

Point Cursor MCP to the launcher so HHNI_LOCAL and PYTHONPATH are set automatically:

**Command:** `pwsh`  
**Args:** `-File`, `C:/Users/bombe/OneDrive/Desktop/AIM-OS/scripts/run_mcp_dev.ps1`

This makes HHNI work without Docker. Restart Cursor after changing.

## Option C: Manual env (if launcher not used)

In Cursor: Settings → MCP → edit **lucid-mcp** → add to `env`:

```json
"env": {
  "HHNI_LOCAL": "1",
  "MCP_MEMORY_DIR": "C:/Users/bombe/OneDrive/Desktop/AIM-OS/mcp_memory",
  "PYTHONPATH": "C:/Users/bombe/OneDrive/Desktop/AIM-OS;C:/Users/bombe/OneDrive/Desktop/AIM-OS/packages"
}
```

`cwd` must be `C:/Users/bombe/OneDrive/Desktop/AIM-OS`. With `HHNI_LOCAL=1`: Qdrant uses in-memory, DGraph uses no-op. Data does not persist across restarts.

## With Docker (full HHNI, persistent)

```bash
docker compose -f deployment/docker-compose-hhni.yml up -d
```

Then ensure `QDRANT_URL=http://localhost:6333` (default). No `HHNI_LOCAL` needed.

## Memory path

MCP server uses `./mcp_memory` by default (relative to server cwd). To point to AIM-OS mcp_memory explicitly, set `MCP_MEMORY_DIR` in your MCP server config to the full path, e.g.:
`C:\Users\...\AIM-OS\mcp_memory`

## Dependencies

- `qdrant-client` — installed ✅
- `sentence-transformers` — required for embeddings. Install: `pip install sentence-transformers`
- DGraph — optional; only needed for full graph storage
