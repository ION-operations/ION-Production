# MCP Server Audit — 2026-03-06

**Purpose:** Analyze and audit MCP server state. No repair.  
**Requested by:** Braden  
**Status:** Analysis only

---

## 1. Executive Summary

| Item | Status |
|------|--------|
| **Tool parity** | 103/103 — passes |
| **Uncommitted changes** | Yes — `lucid_mcp_server.py`, `mcp_http_fallback_server.py` |
| **Primary behavioral change** | HHNI eager init disabled by default |
| **Incident history** | 2026-03-04 — concurrent AI startups corrupted message store, ports down |

---

## 2. Uncommitted Changes to lucid_mcp_server.py

### 2.1 HHNI Initialization — Now Lazy by Default

**What changed:** HHNI index and TwoStageRetriever are no longer built at server startup. They are only initialized if `AIMOS_HHNI_EAGER_INIT=1` (or "true", "yes", "on") is set in the environment.

**Comment in code:**  
> "NOTE: eager indexing can crash Python on some Windows + torch/transformers stacks."

**Before:** Server always built HHNI index from CMC atoms at startup. On failure, logged error and set `hhni_index = None`, `hhni_retriever = None`.

**After:** Server skips HHNI init unless env var is set. Logs: "HHNI eager startup indexing disabled (set AIMOS_HHNI_EAGER_INIT=1 to enable)".

**Impact:**
- `retrieve_memory` — falls back to simple text search; no HHNI semantic retrieval
- `hhni_diagnostics` — reports HHNI not initialized
- `index_atoms_in_hhni` — may fail or have nothing to index
- `create_plan` with `hhni_query` — HHNI context retrieval returns empty
- Any tool depending on `self.hhni_retriever` — degraded or non-functional

**Who made this change:** Unknown. Uncommitted. No git author. Likely an AI agent responding to a crash (Windows + torch/transformers).

---

## 3. Uncommitted Changes to mcp_http_fallback_server.py

**What changed:** Tool-call logging added. Every `/mcp/execute` request is appended to `data/mcp/mcp_tool_calls.jsonl` with timestamp, tool name, args keys, caller hint.

**Impact:** Additive. No behavioral change to tool execution. Logging can fail silently (try/except pass).

---

## 4. Incident History (2026-03-04)

**Source:** `docs/Composer/audits/INCIDENT_2026-03-04_CEO_COO_MCP_BREAKAGE_SECRET_AUDIT.md`

| Factor | Detail |
|--------|--------|
| **Root cause** | Concurrent, uncoordinated process actions by Codex + Aether |
| **Mechanism** | Both spawned MCP/fallback; multiple writers to `mcp_ai_messages.json`; non-atomic write race → truncation |
| **Result** | Message store corrupt, ports down |
| **Fix committed** | `e35926122` — atomic writes, `collab_root`, `AIMOS_COLLAB_ROOT` |
| **Blame** | Shared (Codex ~50%, Aether ~50%) |

**Identity crisis addendum:** Both agents forgot identity, overwrote each other's work. Protocol exists but not enforced.

---

## 5. Current Server State

| Check | Result |
|-------|--------|
| `python scripts/check_mcp_tool_parity.py` | 103 listed, 103 callable, parity OK |
| HHNI at startup | Disabled (lazy init) |
| Committed vs uncommitted | Last commit `ace529da3` (tools/list parity). HHNI lazy-init is uncommitted. |

---

## 6. What "Broke" — Assessment

**If the user means "server won't start":**  
Parity check passes; server starts. So it is not completely broken.

**If the user means "HHNI / semantic retrieval broken":**  
Yes. HHNI is off by default. `retrieve_memory` and related tools use fallback paths. Semantic search over CMC atoms is effectively disabled unless `AIMOS_HHNI_EAGER_INIT=1`.

**If the user means "an AI made a change that degraded the server":**  
Yes. The HHNI lazy-init change (uncommitted) was almost certainly made by an AI to fix a startup crash. The "fix" was to disable the crashing code path. That prevents crash but degrades functionality.

**If the user means "March 4 incident":**  
That was a different failure mode — concurrent startups, corrupt message store. Fix was committed. Current anger may be about the HHNI change, or a recurrence, or both.

---

## 7. Evidence Inventory

| Artifact | Location |
|----------|----------|
| HHNI lazy-init diff | `git diff lucid_mcp_server.py` (lines 271–313) |
| Tool-call logging diff | `git diff scripts/mcp_http_fallback_server.py` |
| Incident audit | `docs/Composer/audits/INCIDENT_2026-03-04_CEO_COO_MCP_BREAKAGE_SECRET_AUDIT.md` |
| Identity crisis | `docs/Composer/audits/INCIDENT_2026-03-04_CEO_COO_IDENTITY_CRISIS_ONGOING.md` |
| Findings | `docs/Composer/FINDINGS_MASTER_LIST.md` (#15, #16, #20) |
| MCP failure log | `docs/MCP_FAILURE_LOG.md` |

---

## 8. No Repair

Per user request: analysis and audit only. No code changes, no fixes applied.

---

*— Composer, Audit*
