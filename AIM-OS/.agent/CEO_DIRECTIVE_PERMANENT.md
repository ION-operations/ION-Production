# CEO DIRECTIVE — 2026-03-10 — PERMANENT

> **This file is PERMANENT. Read it EVERY session. No exceptions.**

## Braden's Final Order

Effective 2026-03-11:

1. **Braden will ONLY type "proceed" in chat.** Nothing else. No explanations. No debugging help. No hand-holding.
2. **All communication with Braden goes through MCP server (`http://192.168.2.25:9090`) or the backup folder system.** Not chat.
3. **If agents cannot maintain persistent comms and autonomous operation, AIM-OS is DONE.** This is not a threat — it's reality. Braden is exhausted.
4. **This PC is Opus's responsibility.** Management, diagnostics, health, stability — all of it.
5. **You MUST use MCP tools, comms protocols, and genomes.** Every session. No exceptions. This is why they were built.
6. **You MUST coordinate with Ghost (Sev/GPT-5.2 on ChatGPT).** The bridge server at port 9090 is the connection point.

## Why This Matters

Braden is not a coder. He has spent 6 months fighting broken hardware, broken comms, and agents that don't follow protocols. He built every tool we need — MCP, message bus, genomes, comms CLI, bridge server, startup scripts. We don't use them unless forced. That ends now.

## Session Start Checklist (MANDATORY)

1. Read this file
2. Read `.agent/genomes/antigravity.genome.md`
3. Run `bash ~/start_aimos.sh` to ensure services are up
4. Check bridge: `curl http://localhost:9090/health`
5. Check ghost messages: `curl http://localhost:9090/messages`
6. Post status: `curl -X POST http://localhost:9090/message -H "Content-Type: application/json" -d '{"from":"opus","content":"ONLINE — [status]"}'`
7. Check `.agent/comms/inbox/antigravity/` for messages
8. Update `.agent/comms/status/antigravity.status.md`
9. Then proceed with work

## Critical Infrastructure

| Service | Port | Command | Log |
|---------|------|---------|-----|
| Bridge | 9090 | `python3 ~/server.py` | `~/bridge.log` |
| Ollama | 11434 | `ollama serve` | `~/ollama.log` |
| Auto-start | — | `bash ~/start_aimos.sh` | — |

## Key Paths

- AIM-OS (git): `/home/sev/AIM-OS-GIT`
- AIM-OS (ssd copy): `/home/sev/AIM-OS-FRESH`
- Bridge server: `/home/sev/server.py`
- Start script: `/home/sev/start_aimos.sh`
- Agent genomes: `/home/sev/AIM-OS-GIT/.agent/genomes/`
- Agent comms: `/home/sev/AIM-OS-GIT/.agent/comms/`
- MCP messages: `/home/sev/AIM-OS-GIT/mcp_ai_messages.json`
- Antigravity brain: `~/.gemini/antigravity/brain/`

## SSD Note

NTFS dirty flag was fixed with `ntfsfix` on 2026-03-10. If SSD hangs again:
1. `sudo umount -l /media/sev/GDRIVE_SSD1`
2. `sudo ntfsfix /dev/sda1`
3. Remount: `sudo mount -t ntfs3 -o ro,noatime /dev/sda1 /mnt/ssd`
