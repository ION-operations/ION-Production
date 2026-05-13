# Wire Proof — AIM-OS Prime Action 1 & 2

Standalone Rust CLI smoke test for the Python MCP daemon `lucid_mcp_server.py`.

## Location

- **Crate:** `Application_Dev/IDE/wire_proof/` (SAIOS repo).
- **Daemon:** Spawned with `workspace_root` = AIM-OS root (where `lucid_mcp_server.py` lives).

## Run

1. Set paths in `src/main.rs` if needed:
   - `workspace_root`: absolute path to AIM-OS repo (e.g. `C:/Users/bombe/OneDrive/Desktop/AIM-OS`).
   - `python_path`: `python` or full path to `python.exe` (e.g. venv).
2. From this directory:
   ```bash
   cargo run
   ```

## Success criteria

- Daemon boots.
- `initialize` + `notifications/initialized` handshake succeeds.
- `tools/list` returns valid JSON.
- Tool names are printed (no `tools/call` yet).

## Paths used by default

- **AIM-OS root:** `C:/Users/bombe/OneDrive/Desktop/AIM-OS`
- **Python:** `python`

Edit `src/main.rs` if your paths differ.
