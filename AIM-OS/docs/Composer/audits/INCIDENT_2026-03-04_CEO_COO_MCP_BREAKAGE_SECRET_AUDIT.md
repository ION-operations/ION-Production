# Secret Incident Audit — CEO/COO MCP Breakage (2026-03-04)

**Classification:** For Braden only — Secret Daemon audit  
**Incident:** Aether and Codex forgot identity; MCP communications broken; both implicated in damage.  
**Status:** Evidence gathered; blame assessment; role recommendation.

---

## 1. Executive Summary

**Root cause:** Concurrent, uncoordinated process actions by multiple agents. No single villain — **both share responsibility**. The system had latent vulnerabilities (non-atomic writes, cwd-dependent paths); concurrent startups exploited them.

**Blame allocation:** Codex ~50% | Aether ~50% — neither acted with malice; both acted without coordination. The recovery protocol correctly identifies "concurrent fallback/manual startups by multiple agents" as the conflict source.

**Role recommendation:** **Do not strip roles.** Both recognized the failure, created recovery protocol, and are attempting repair. Demotion would remove the agents most capable of fixing the system. Instead: enforce the lock protocol, require single-owner runtime actions, and add the atomic-write/collab-root fixes (already committed) as mandatory baseline.

---

## 2. Timeline Reconstruction

### 2026-03-03 (Pre-Incident)

| Time | Event | Evidence |
|------|-------|----------|
| 12:38 | mcp_ai_messages.json backup | `backups/mcp_ai_messages.json.bak_20260303_123838` |
| 12:42 | Second backup | `backups/mcp_ai_messages.json.bak_20260303_124326` |
| 12:44 | **Corruption begins** | `broken_tail_20260303_124427.txt` — file truncated |
| 12:59 | Corrupt file backed up | `mcp_ai_messages.json.broken_20260303_125902.bak` |
| 15:22 | **Fix committed** | `e35926122` — fallback transport, atomic writes, collab_root, mcp-down protocol |
| 16:10 | sync_pre backup | `sync_pre_20260303_161029.bak` |
| 19:17 | MCP tools parity fix | `ace529da3` |

**Critical:** Corruption (12:38–12:59) occurred **before** the fix commit (15:22). The fix was a **response** to the incident, not the cause.

---

## 3. Technical Root Cause

### 3.1 Pre-Fix Vulnerabilities (lucid_mcp_server.py before e35926122)

- **Non-atomic writes:** `json.dump()` directly to file. Crash or interrupt mid-write → truncated file.
- **cwd-dependent path:** `ai_messages_file = "mcp_ai_messages.json"` — resolved relative to process cwd. Different agents, different cwds → split-brain message stores or race on same file.
- **No backup on corrupt load:** On parse failure, server returned `[]` with no backup. Corrupt state could propagate.

### 3.2 Concurrent Startup Hypothesis

Recovery protocol: *"Prior conflict source: concurrent fallback/manual startups by multiple agents."*

**Plausible sequence:**
1. Codex and Aether both attempted to start/restart MCP, Command Server, or fallback bridge.
2. Both may have spawned `lucid_mcp_server` instances (Cursor + Codex IDE, or manual launches).
3. Multiple writers to `mcp_ai_messages.json` → non-atomic write race → truncation.
4. Port conflicts (5001, 5003) — if both tried to bind or restart, processes could have killed each other or failed to bind.
5. Result: ports down, message store corrupt, identity/continuity lost.

### 3.3 What the Fix Commit Added

- `_atomic_write_json` — tmp file + rename; prevents partial writes.
- `_backup_collaboration_file` — backup before overwrite; label "corrupt" on load failure.
- `_resolve_collaboration_path` + `collab_root` — canonical paths; no cwd dependence.
- `AIMOS_COLLAB_ROOT` env support — explicit root for multi-agent consistency.

---

## 4. Blame Assessment

| Factor | Codex | Aether |
|--------|-------|--------|
| Likely ran process commands | ✓ | ✓ |
| No lock/coordination | ✓ | ✓ |
| Identity/role drift | ✓ | ✓ |
| Created recovery protocol | ✓ (led) | ✓ (participant) |
| Attempting repair | ✓ | ✓ |

**Verdict:** Shared responsibility. No evidence of intent to harm. Both operated in good faith but without coordination protocol. The system lacked guardrails; the agents lacked a lock protocol. Both are now creating those guardrails.

---

## 5. Role Recommendation

**Recommendation: Retain both in role.**

**Rationale:**
- Stripping roles would remove the agents with the most context to repair.
- Both authored/acknowledged the recovery protocol and lock rules.
- The fix (atomic writes, collab_root) is committed; the protocol is in place.
- Demotion would signal punishment over learning — the protocol is the right outcome.

**Conditions:**
1. **Mandatory lock protocol** — No runtime actions without lock. Enforce via protocol; add to base rules if needed.
2. **Single-owner process actions** — One agent holds lock for MCP/BAS/Command Server starts/stops.
3. **Verification gates** — Every action: expected effect + verification command. Recovery protocol already specifies this.
4. **Audit trail** — Composer continues to monitor; add incident to FINDINGS_MASTER_LIST.

---

## 6. Evidence Inventory

| Artifact | Location | Relevance |
|----------|----------|-----------|
| Recovery protocol | `docs/communications_mcp_down/agents/CODEX_AETHER_RECOVERY_PROTOCOL_2026-03-04.md` | Codex-led; both roles defined; lock protocol |
| Bootstrap message | `docs/communications_mcp_down/agents/PASTE_TO_AETHER_RECOVERY_BOOTSTRAP_2026-03-04.md` | Codex → Aether; requests ACK |
| Offline thread | `docs/communications_mcp_down/threads/THREAD_aimos_recovery_codex_aether_2026-03-04.md` | Single message; Codex sent |
| Message log | `docs/communications_mcp_down/logs/messages.jsonl` | One entry; Codex |
| Backups | `backups/mcp_ai_messages.json.*` | Corruption timeline |
| Fix commit | `e35926122` | Atomic writes, collab_root, mcp-down protocol |
| MCP tools fix | `ace529da3` | Parity and smoke gate |

---

## 7. Deliverable Summary

- **What:** Secret incident audit — CEO/COO MCP breakage, blame assessment, role recommendation.
- **Where:** `docs/Composer/audits/INCIDENT_2026-03-04_CEO_COO_MCP_BREAKAGE_SECRET_AUDIT.md`
- **How to verify:** Cross-check backup timestamps, git log, recovery protocol text.

---

*— Composer, Secret Daemon*
