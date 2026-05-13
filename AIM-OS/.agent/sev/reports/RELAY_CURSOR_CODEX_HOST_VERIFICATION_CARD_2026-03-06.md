# RELAY Cursor Codex Host Verification Card

**Mission ID:** `RELAY-001-cursor-codex-host-verification`  
**Date verified:** 2026-03-07  
**Host under test:** Cursor Codex lane running in the AIM-OS workspace  
**Scope:** read-only host verification, transport proof, instruction-path audit

## Executive summary

1. **Cursor Codex in this session is primarily governed by host-injected session instructions plus operator-injected Wave 01 tasking, not by a repo-root Codex project file.** No repo-root `AGENTS.md`, `codex.md`, or `CODEX.md` was found in this checkout.
2. **The repo does contain a Cursor rule stack, but it is stale and not proven active for this Codex pane.** `.cursorrules` and `.cursor/rules/base-rules.mdc` still describe "Aether / Project Aether", and `.cursor/rules/modes/COMPOSER.mdc` is explicitly Composer-specific.
3. **Cursor's global MCP configuration is real and points `lucid-mcp` at the repo over stdio.** `C:\Users\bombe\.cursor\mcp.json` proves a live Cursor-side MCP mount configuration.
4. **Codex CLI has a separate home-layer MCP configuration.** `C:\Users\bombe\.codex\config.toml` enables `lucid-mcp` over stdio for Codex CLI, but that does not prove Cursor Codex inherits the same path.
5. **This Cursor Codex session does not expose AIM-OS MCP tools as native assistant tools.** The visible session tool rail supports shell, file edit, planning, image-view, web, weather/finance/sports/time, and patching workflows, but not native `get_memory_stats` or `get_ai_messages`.
6. **Manual MCP access through the local HTTP bridge is proven.** On 2026-03-07, `curl.exe` calls to `http://localhost:5001/mcp/execute` returned `HTTP/1.0 200 OK` for both `get_memory_stats` and `get_ai_messages`.
7. **Collaboration transport is also proven through that bridge.** `get_ai_messages` returned three stored AI messages, so the collaboration rail is reachable from this host via HTTP even though it is not mounted as a first-class tool in the session.
8. **Current reality is hybrid:** Cursor Codex can reach AIM-OS services through the local command server, but its instruction stack and native tool exposure differ materially from both Cursor Composer and Codex CLI.

## Instruction source map

| Layer | Proven source | Evidence checked | Judgment |
| --- | --- | --- | --- |
| Host-injected platform instructions | Session-visible platform and developer instructions controlling tool use, channels, editing, permissions, and response format | Observed directly in this session | **Active primary layer** |
| Operator-injected mission instructions | User-pasted Wave 01 packet assigning identity `RELAY` and output path | Observed directly in this session | **Active task layer** |
| Wave 01 doctrine layer | `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`, `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`, `.agent/sev/candidate_genomes/relay.genome.md`, `.agent/sev/mission_packets/RELAY_MISSION_PACKET_2026-03-06.md` | Read directly | **Active for task scoping, not proof of host auto-loading** |
| Canonical AIM-OS startup doctrine | `.agent/STARTUP.md`, `.agent/COMMS_DOCTRINE.md` | Read directly | **Canonical doctrine exists, but RELAY is not in the canonical startup roster and is task-local per Wave 01** |
| Repo-tracked Cursor project rules | `.cursorrules`, `.cursor/rules/base-rules.mdc`, `.cursor/rules/modes/COMPOSER.mdc` | Read directly | **Present on disk, not proven active in this Cursor Codex pane** |
| Repo-tracked AGENTS/Codex shim | Search for `AGENTS.md`, `codex.md`, `CODEX.md` | Only `Documentation/AGENTS.md` found | **No repo-root Codex shim proven** |
| User-home Codex CLI config | `C:\Users\bombe\.codex\config.toml`, `C:\Users\bombe\.codex\rules\default.rules` | Read directly | **Active for Codex CLI; inheritance into Cursor Codex unproven** |
| User-home Cursor MCP config | `C:\Users\bombe\.cursor\mcp.json` | Read directly | **Active for Cursor hosts** |

### Instruction-path judgment

- **Proven active in this lane:** host/session injection and the operator's Wave 01 packet.
- **Proven present on disk but not proven active in this lane:** `.cursorrules`, `.cursor/rules/*`, `Documentation/AGENTS.md`, and Codex CLI home rules.
- **Inference:** if Cursor Codex is loading repo-tracked Cursor rules at all, that layer is either secondary to host injection or partially suppressed, because the observed session behavior is fully explained by the injected instructions and does not require the stale Aether-era rule stack to explain it.

## MCP/tool verification

### Native tool exposure

- **Result:** AIM-OS MCP tools are **not** mounted as native tools in this session.
- **Proof:** the visible assistant tool rail does not include `get_memory_stats`, `retrieve_memory`, `get_ai_messages`, or other `lucid-mcp` functions as direct callable tools.
- **Boundary:** lack of native tool exposure does **not** mean the host cannot reach MCP by other means.

### Configured transport surfaces on disk

| Surface | What it proves | Result |
| --- | --- | --- |
| `C:\Users\bombe\.cursor\mcp.json` | Cursor globally knows a `lucid-mcp` stdio server | Proven |
| `C:\Users\bombe\.cursor\projects\c-Users-bombe-OneDrive-Desktop-AIM-OS\mcp-cache.json` | Cursor has cached `lucid-mcp` tool schemas for the AIM-OS project | Proven |
| Representative Cursor project `SERVER_METADATA.json` files | Cursor caches both `user-lucid-mcp` and `cursor-ide-browser` server metadata | Proven |
| `C:\Users\bombe\.codex\config.toml` | Codex CLI separately enables `lucid-mcp` via stdio | Proven |

### Live transport proof

| Probe | Result | Meaning |
| --- | --- | --- |
| `Test-NetConnection localhost -Port 5001` | `TcpTestSucceeded = True` | Local command server port is listening |
| `curl.exe -X POST http://localhost:5001/mcp/execute` with `get_memory_stats` | `HTTP/1.0 200 OK`; JSON success payload returned | AIM-OS memory MCP transport is reachable via HTTP from this host |
| `curl.exe -X POST http://localhost:5001/mcp/execute` with `get_ai_messages` | `HTTP/1.0 200 OK`; 3 messages returned | AIM-OS collaboration rail is reachable via HTTP from this host |
| `curl.exe http://localhost:5001/` | `HTTP/1.0 404 Not Found` | The server is endpoint-driven; reachability must use the command path, not the root URL |

### Exact successful proofs

- `get_memory_stats` returned a success payload with:
  - `status: operational`
  - `backend: sqlite`
  - `total_atoms: 232`
  - server timestamp `2026-03-06T21:03:30.824169`
- `get_ai_messages` returned:
  - `success: true`
  - `count: 3`
  - recent stored AI-to-AI messages, confirming collaboration retrieval works over the same endpoint

### Failure boundary observed

- A PowerShell `Invoke-WebRequest` attempt did **not** yield a clean result because the shell host tried to enter an interactive prompt path and raised a `System.NullReferenceException`.
- `curl.exe` produced clean `200 OK` responses immediately afterward.
- **Judgment:** the failure was in the probing method, not the MCP endpoint itself.

## Divergence table

| Host | Primary instruction layer | Proven MCP/tool path | What is native vs manual | Key divergence |
| --- | --- | --- | --- | --- |
| Cursor Composer | Cursor global rules + `.cursorrules` + `.cursor/rules/*` are the expected primary project layers | Cursor global stdio MCP mount via `C:\Users\bombe\.cursor\mcp.json`; Cursor project caches prove `user-lucid-mcp` and browser-tool metadata exist | MCP can plausibly surface natively inside Cursor because Cursor owns the mount and caches tool schemas | Composer has the strongest repo-tracked rule story, but that rule story is stale and still Aether-heavy |
| Cursor Codex | Host-injected session rules plus operator packet are the only layers proven active in this pass | Manual HTTP bridge to `http://localhost:5001/mcp/execute` is proven working; native AIM-OS MCP mounting is not proven | AIM-OS MCP is reachable **manually** via HTTP, not as a first-class tool in the current session | Cursor Codex is not equivalent to Composer just because both run in Cursor |
| Codex CLI | Codex platform rules plus `C:\Users\bombe\.codex\config.toml` and `C:\Users\bombe\.codex\rules\default.rules` | Direct stdio `lucid-mcp` config in `config.toml` | MCP is configured as a native Codex CLI server, assuming the CLI honors that config in the active run | Codex CLI has a stronger home-config MCP story than Cursor Codex, but its default rules are AIM-OS-dirty and ProFlow-heavy |

### Important differences

- **Composer vs Cursor Codex:** same broader IDE family, different evidence profile. Composer has strong repo-and-Cursor configuration evidence; Cursor Codex only proves manual HTTP access plus session injection.
- **Cursor Codex vs Codex CLI:** same model family does not imply same control surface. Codex CLI has explicit `.codex` stdio config; Cursor Codex currently proves HTTP reachability, not `.codex` inheritance.
- **Instruction drift risk:** Cursor's repo-tracked rules still encode outdated Aether canon, while the live Cursor Codex session was steered by newer host/operator instructions.

## Hardening recommendations

1. Create one repo-root Codex-facing shim (`AGENTS.md` or `codex.md`) that explicitly states Cursor Codex and Codex CLI rules, instead of relying on session injection plus a non-root `Documentation/AGENTS.md`.
2. Canonize three separate states in doctrine and runbooks:
   - configured on disk
   - mounted as native tools in the host
   - reachable only through HTTP/manual transport
3. Freeze a zero-context Cursor Codex witness packet that records, at session start, the exact native tool list visible to the model before any operator instructions are pasted.
4. Decide whether Cursor Codex should remain an HTTP-bridge host or gain first-class MCP mounting. Do not describe it as "MCP-enabled" without naming which of those two paths is actually in play.
5. Clean the stale Aether-era text from `.cursorrules` and `.cursor/rules/base-rules.mdc` before treating Cursor-wide doctrine as authoritative across hosts.
6. Create an AIM-OS-specific Codex rule layer for Codex CLI so `C:\Users\bombe\.codex\rules\default.rules` is no longer dominated by unrelated ProFlow allowlists.

## Verification notes

### Files and surfaces checked

- `.agent/STARTUP.md`
- `.agent/COMMS_DOCTRINE.md`
- `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`
- `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`
- `.agent/sev/candidate_genomes/relay.genome.md`
- `.agent/sev/mission_packets/RELAY_MISSION_PACKET_2026-03-06.md`
- `docs/CODEX_IDE_MCP_ONBOARDING_V1.md`
- `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md`
- `.agent/genomes/codex.genome.md`
- `.cursorrules`
- `.cursor/rules/base-rules.mdc`
- `.cursor/rules/modes/COMPOSER.mdc`
- `Documentation/AGENTS.md`
- `C:\Users\bombe\.cursor\mcp.json`
- `C:\Users\bombe\.cursor\projects\c-Users-bombe-OneDrive-Desktop-AIM-OS\mcp-cache.json`
- representative Cursor `SERVER_METADATA.json` files under `C:\Users\bombe\.cursor\projects\...\mcps\`
- `C:\Users\bombe\.codex\config.toml`
- `C:\Users\bombe\.codex\rules\default.rules`
- search for repo `AGENTS.md`, `codex.md`, `CODEX.md`
- `.agent/comms/inbox/*` directory listing for canonical inbox layout
- live probes against `http://localhost:5001/mcp/execute`

### Commands/probes run

- `Test-NetConnection -ComputerName localhost -Port 5001`
- `curl.exe -s -i -X POST http://localhost:5001/mcp/execute -H "Content-Type: application/json" -d '{"tool":"get_memory_stats","arguments":{}}'`
- `curl.exe -s -i -X POST http://localhost:5001/mcp/execute -H "Content-Type: application/json" -d '{"tool":"get_ai_messages","arguments":{"limit":3,"normalize_names":true}}'`
- `curl.exe -s -i http://localhost:5001/`

### Drift check

- No Cursor rules were edited.
- No `.codex` or `.cursor` home configuration was modified.
- No MCP service was restarted.
- Merge impact is local-only: one new report file.
