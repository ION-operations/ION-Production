# Git Update Plan — 2026-03-05

**Purpose:** Update the existing public sev-32/AIM-OS repo so it fully represents the project. Other AIs can clone and work from the repo when they can't access the local folder.

**Target:** `https://github.com/sev-32/AIM-OS.git` (public)  
**Branch:** `codexgit-mcp-fallback-offline-comms` (current — commit and push here)  
**Status:** Plan only — discuss with Braden before executing.

**Full mission:** See [GIT_UPDATE_MISSION_2026-03-05.md](GIT_UPDATE_MISSION_2026-03-05.md) for phased execution, README spec, and exclusions.

---

## Current State

**Last commit:** `0c13c65e6` — Add runbook for BAS authenticated gates 7-8 proof

**Uncommitted work:**
- **Modified:** ~90 files (lucid_mcp_server, mcp_http_fallback_server, docs, packages, cursor-addon, etc.)
- **Untracked:** ~120+ paths (PROJECT_TRUTH, context/, .agent/, docs/AUDIT_*, roundtable, scripts, packages/joc, etc.)

---

## What Should Be in Git (For AI Onboarding)

Other AIs cloning the repo need:

| Category | Include? | Notes |
|----------|----------|-------|
| **Core docs** | Yes | AUDIT_01-04, BRADEN_RETURN_README, MCP_RUNBOOK, CONTEXT_CANON, SALVAGE_PLAN, findings, roundtable |
| **PROJECT_TRUTH** | Yes | Canonical truth pack — essential for context |
| **context/** | Yes | Operational definition, current truth, canonical map — ChatGPT sync capsule |
| **.agent/** | Yes | Genomes, comms, STARTUP, COMMS_DOCTRINE — identity and coordination |
| **scripts/** | Yes | mcp_sse_server, ngrok_tunnel, offline_comms, package_chatgpt_context |
| **packages/joc** | Yes | JOC is canonical UI |
| **packages/browser-automation-service** | Yes | BAS — modified files |
| **packages/shared** | Yes | Shared types/selectors |
| **lucid_mcp_server.py** | Yes | store_memory tags fix, core MCP |
| **mcp_ai_messages.json** | Maybe | Contains message history — could be large; consider .gitignore or commit empty/sample |
| **mcp_memory/** | Maybe | Runtime data — may contain sensitive or large data |
| **data/memory, data/mcp** | Maybe | CMC/memory runtime — often excluded |
| **codex_workspace/** | Maybe | Codex-specific persistence |
| **IDE/** | ? | Tauri IDE — large? |
| **context_capsule_wire_and_mapper_v1/** | ? | Tier B prototype — part of context canon |
| **cursor-addon/out/** | Usually no | Compiled output — typically gitignored |
| **apps/Globe, apps/HyperRealH20Monolith, etc.** | ? | App examples — user preference |

---

## Exclusions to Decide

1. **mcp_ai_messages.json** — Message history. Include for continuity, or gitignore and commit empty template?
2. **mcp_memory/** — CMC index/tags. Include for structure, or exclude (runtime data)?
3. **data/memory, data/mcp** — Runtime stores. Usually exclude.
4. **codex_workspace/** — Codex persistence. Exclude or include?
5. **IDE/** — Full Tauri app. Size? Include if core to AIM-OS.
6. **cursor-addon/out/** — Build output. Should be gitignored.
7. **Large app examples** (Globe, HyperRealH20Monolith, etc.) — Include or exclude?

---

## Proposed Commit Strategy

**Option A: Logical commits (recommended for history)**
1. `docs: Add Audit Day deliverables (AUDIT_01-04, MCP_RUNBOOK, CONTEXT_CANON, etc.)`
2. `feat: Add PROJECT_TRUTH pack and context capsule`
3. `feat: Add .agent genomes, comms, identity infrastructure`
4. `feat: Add SSE MCP server and ngrok tunnel for ChatGPT`
5. `fix: store_memory accept list tags (lucid_mcp_server)`
6. `feat: Add JOC package, BAS updates, shared packages`
7. `docs: Add roundtable, salvage plan, governance deprecation`
8. `chore: Add scripts (offline_comms, package_chatgpt_context, mcp_control)`

**Option B: Fewer, larger commits**
1. `Audit Day + GPT 5.2 milestone (docs, PROJECT_TRUTH, context, .agent)`
2. `MCP: SSE server, ngrok, store_memory fix, runbook`
3. `JOC, BAS, packages, scripts`

**Option C: Single consolidated commit**
- One commit: "Full project state 2026-03-05 — Audit Day, GPT 5.2, salvage"
- Simpler but loses granular history

---

## Pre-Commit Checklist

- [ ] Review .gitignore — ensure secrets, .env, logs, node_modules excluded
- [ ] Confirm no API keys or tokens in committed files (ngrok_tunnel.py has auth token — **check**)
- [ ] Decide on mcp_ai_messages.json, mcp_memory, data/
- [ ] Decide on IDE/, context_capsule, app examples
- [ ] cursor-addon/out/ — add to .gitignore if not already?
- [ ] Run `git status` after .gitignore updates to verify scope

---

## ngrok_tunnel.py — Sensitive?

`scripts/ngrok_tunnel.py` contains: `conf.get_default().auth_token = "3AWskQeLM9ah7QDuxIkTwJmEwWY_..."`

**Action:** Move to env var or exclude from commit. Do not push auth tokens to public repo.

---

## Resolved (from Braden)

1. **Repo:** Public, existing (sev-32/AIM-OS). We are updating it.
2. **Branch:** Current branch (`codexgit-mcp-fallback-offline-comms`).
3. **README:** Must be updated — see [GIT_UPDATE_MISSION](GIT_UPDATE_MISSION_2026-03-05.md) Phase 1.

## Questions for Braden (if any override)

1. ~~Repo visibility~~ — Public. Resolved.
2. **mcp_ai_messages.json:** Commit with history, or empty template, or gitignore?
3. **mcp_memory, data/:** Exclude (runtime) or include structure?
4. **IDE/, context_capsule, app examples:** Include all, some, or none?
5. **Commit style:** A (logical), B (fewer), or C (single)?
6. **ngrok token:** Remove from file before commit; use env var? *(Inspection says: must fix — use NGROK_AUTH_TOKEN env)*
7. ~~Branch~~ — Current branch. Resolved.

---

## Answers from Repo Inspection (2026-03-05)

*These answers are derived from inspecting the repo and aligning with `docs/CODEXGIT_RELEASE_SLICING_PLAN_2026-03-03.md`. Braden can override any of these.*

### 2. mcp_ai_messages.json — **Exclude**

- **Status:** Already in `.gitignore` (line 143), but **still tracked** (committed before gitignore).
- **CODEXGIT plan:** Explicitly in "Exclude-By-Default Set" — "do not include in production commits."
- **Action:** `git rm --cached mcp_ai_messages.json` to stop tracking. Do not commit contents.

### 3. mcp_memory, data/ — **Exclude runtime; include structure only if needed**

- **mcp_memory/index/tags/:** 38 tag JSON files are **tracked**. In `.gitignore` (line 146) but committed earlier.
- **CODEXGIT plan:** `mcp_memory/index/tags/**` is Exclude-By-Default.
- **Action:** `git rm --cached mcp_memory/index/tags/*.json` to stop tracking.
- **data/:** Exists (analysis, databases, mcp, memory, etc.). Only `packages/cmc_service/data/` is in gitignore. Root `data/` is not gitignored but contains runtime stores — **exclude** per CODEXGIT (runtime data).

### 4. IDE/, context_capsule, app examples — **Exclude for this push**

- **IDE/:** ~12 GB. CODEXGIT Slice 5: "deferred lane" — "move to dedicated feature branches."
- **context_capsule_wire_and_mapper_v1/:** ~342 MB. Same policy.
- **apps/Globe, HyperRealH20Monolith, etc.:** Slice 5 — "land only with explicit product acceptance criteria."
- **Action:** Do not include in this update. Add to `.gitignore` if not already, or leave untracked.

### 5. Commit style — **Recommend Option A (logical)**

- Easier rollback, clearer history, aligns with CODEXGIT slice-based approach.

### 6. ngrok token — **Must fix before commit**

- **Current:** Hardcoded in `scripts/ngrok_tunnel.py` line 23.
- **Action:** Use `os.environ.get("NGROK_AUTH_TOKEN")` and document in runbook. Add `NGROK_AUTH_TOKEN` to `.env.example` (placeholder). Do not push token.

### 7. Branch — **Stay on current branch or create feature branch**

- **Current:** `codexgit-mcp-fallback-offline-comms`.
- **Options:** Commit here and push, or create `audit-day-2026-03-05` from it, then merge to main after review. CODEXGIT plan uses this branch as baseline.

### Additional: De-index tracked runtime files

These are in `.gitignore` but still tracked. Run before staging:

```powershell
git rm --cached mcp_ai_messages.json
git rm --cached mcp_timeline_entries.json
git rm --cached codex_workspace/persistence/collaboration/codex_ai_messages.json
git rm --cached mcp_memory/index/tags/*.json
```

### Additional: cursor-addon/out/

- **Status:** Not in `.gitignore`. CODEXGIT Exclude-By-Default.
- **Action:** Add `cursor-addon/out/` to `.gitignore` if not present. (Checked: not present — add it.)

---

---

## README Update

README must be updated to reflect GPT 5.2, ChatGPT MCP, PROJECT_TRUTH, .agent. Full spec: [GIT_UPDATE_MISSION](GIT_UPDATE_MISSION_2026-03-05.md) Phase 1.

---

*Plan updated with inspection answers. No git commands executed. — Composer*
