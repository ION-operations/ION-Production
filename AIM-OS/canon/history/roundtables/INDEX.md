# Roundtable Index

**Purpose:** Curated view of active roundtable threads and decisions.  
**Updated:** 2026-03-05

---

## Active Roundtable Threads

| Thread ID | File | Topic | Owner | Last Update |
|-----------|------|-------|-------|-------------|
| aimos_roundtable_mcp_recovery_audit_2026-03-06 | `../communications_mcp_down/threads/THREAD_aimos_roundtable_mcp_recovery_audit_2026-03-06.md` | MCP recovery audit, evidence, signoff | Shared (all agents) | 2026-03-06T23:15:52Z |
| aimos_roundtable_operational_convergence_2026-03-04 | `../communications_mcp_down/threads/THREAD_aimos_roundtable_operational_convergence_2026-03-04.md` | Operational convergence, critical path | Shared (Aether/Codex/Opus/Composer) | 2026-03-05T03:30:49Z |
| aimos_recovery_codex_aether_2026-03-04 | `../communications_mcp_down/threads/THREAD_aimos_recovery_codex_aether_2026-03-04.md` | MCP recovery, lock protocol | Codex | 2026-03-04 |

---

## Decisions (Summary)

See `decisions/DECISION_LOG.md` for full entries.

| ID | Topic | Owner | Date |
|----|-------|-------|------|
| DEC-001 | Code freeze and communications-only mode | Braden (COMMAND) | 2026-03-04 |
| DEC-002 | Roundtable as canonical fallback coordination path | Braden (COMMAND) | 2026-03-04 |
| DEC-003 | Incident damage report published | Codex Agent | 2026-03-04 |
| DEC-004 | `:5001` repair window requires explicit authorization | COMMAND/Aether adjudication | 2026-03-04 |
| DEC-005 | Deep research synthesis packet and P0-P2 execution ladder published | Codex Agent | 2026-03-05 |
| DEC-006 | Composer assigned as ChatGPT sync and zip packaging owner | Braden (COMMAND) | 2026-03-05 |
| DEC-007 | Context systems federate-by-lane now; consolidate by promotion gate later | Codex (adjudication path: Opus) | 2026-03-05 |
| DEC-008 | HTTP fallback (:5001) required for Codex — canonize startup | Braden (COMMAND) | 2026-03-06 |

---

## How to Update This Index

1. **New thread:** Add row to Active Roundtable Threads when you create a thread.
2. **New decision:** Add row to Decisions and full entry in `decisions/DECISION_LOG.md`.
3. **Reconciled:** Mark thread as `reconciled` when MCP returns and thread is merged.

---

## Opus: Start Here

**Opus (COO):** When you start, read `docs/roundtable/OPUS_READ_FIRST.md` — Composer is waiting for your ACK.

---

## Thread Creation Checklist

When starting a new roundtable thread:

1. Choose thread ID: `aimos_roundtable_<topic>_YYYY-MM-DD`
2. Post kickoff via `post_offline_message.py`
3. Add row to this INDEX
4. Notify other agents (post to thread with `--to "all"` or list agents)
