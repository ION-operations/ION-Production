# AIM-OS Known Issues Log
# Maintained by Opus — updated every session
# Last updated: 2026-03-10T11:42:00-04:00

## CRITICAL

### MCP NOT CONFIGURED IN ANTIGRAVITY IDE
- **Status:** OPEN
- **Impact:** Cannot use ANY of the 92+ MCP tools (store_memory, get_ai_messages, etc.)
- **Root cause:** `lucid_mcp_server.py` was configured on Windows Antigravity but NOT set up after Linux deployment
- **Fix needed:** Add MCP server config pointing to `/home/sev/AIM-OS-GIT/lucid_mcp_server.py` via stdio
- **Notes:** HTTP fallback server starts on :5001 but the `store_memory` call hung. The native stdio transport is what should be used.

### ZOMBIE TERMINAL SESSIONS PERSIST
- **Status:** OPEN  
- **Impact:** Running terminal list always shows dead processes as "running"
- **Root cause:** IDE-managed terminal sessions survive OS-level `pkill`. They need `send_command_input` with `Terminate: true` using the original CommandId, but those IDs are lost after conversation truncation.
- **Fix needed:** Either auto-cleanup mechanism in the IDE, or discipline to always save CommandIds

## HIGH

### GIT PUSH AUTHENTICATION FAILS
- **Status:** OPEN
- **Impact:** Can't push local commits to GitHub
- **Root cause:** Password auth disabled on GitHub, needs Personal Access Token
- **Error:** `remote: Invalid username or token. Password authentication is not supported for Git operations.`
- **Fix needed:** Generate PAT at github.com, configure with `git remote set-url origin https://TOKEN@github.com/sev-32/AIM-OS.git`

### GIT PUSH IS SLOW
- **Status:** OPEN / INVESTIGATION NEEDED
- **Impact:** Pushes take very long despite fast internet
- **Notes:** Braden flagged this. Could be: large repo size (907MB .git), HTTPS overhead, or GitHub rate limiting
- **Possible fixes:** SSH key auth, shallow clone, git-lfs for large files

### EMAIL SMTP TIMEOUT
- **Status:** OPEN
- **Impact:** Can't use email as backup comms channel  
- **Root cause:** SMTP connection to smtp.gmail.com:587 timed out. No 2FA on account.
- **Possible causes:** ISP blocking port 587, need to try port 465 (SSL), or "Less secure app access" setting needed
- **Fix needed:** Debug SMTP connection, try alternate port, check firewall

## MEDIUM

### BRIDGE MESSAGE ENDPOINT SLOW
- **Status:** OPEN
- **Impact:** `curl http://localhost:9090/messages` hangs
- **Root cause:** Likely large JSON file or synchronous read blocking
- **Fix needed:** Paginate messages, add timeout, or use direct file read
