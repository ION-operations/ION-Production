# Git Update Mission — 2026-03-05

**Purpose:** Update the existing public sev-32/AIM-OS repo so it fully represents the project. Other AIs and collaborators can clone and work from the repo when they can't access the local folder.

**Target:** `https://github.com/sev-32/AIM-OS.git` (public)  
**Branch:** `codexgit-mcp-fallback-offline-comms` (current)  
**Status:** Mission plan — execution after Braden review.

---

## Mission Context

- **Repo already exists** — We are updating sev-32's repo, not creating from scratch.
- **Public repo** — No secrets, tokens, or sensitive data in commits.
- **Current branch** — Commit and push to `codexgit-mcp-fallback-offline-comms`.
- **README must be updated** — Main README.md does not reflect GPT 5.2, ChatGPT MCP, PROJECT_TRUTH, .agent, or audit-day deliverables.

---

## Scope (from git status 2026-03-05)

| Category | Modified | Untracked | Action |
|----------|----------|-----------|--------|
| **Docs** | ~15 | ~80+ | Include: AUDIT_01–04, MCP_RUNBOOK, CONTEXT_CANON, SALVAGE_PLAN, BRADEN_RETURN_README, roundtable, findings |
| **PROJECT_TRUTH** | 0 | 9 files | Include — canonical truth pack |
| **context/** | 0 | Yes | Include — ChatGPT sync capsule |
| **.agent/** | 0 | Yes | Include — genomes, comms, identity |
| **scripts/** | 2 | ~15 | Include: mcp_sse_server, ngrok_tunnel, package_chatgpt_context, offline_comms, mcp_control |
| **packages/joc** | 0 | Yes | Include — canonical UI |
| **packages/browser-automation-service** | ~15 | tests, jest | Include — BAS updates |
| **packages/shared** | 0 | Yes | Include |
| **lucid_mcp_server.py** | Yes | 0 | Include — store_memory tags fix |
| **cursor-addon** | ~50 (src + out) | 0 | Include src only; exclude out/ |
| **Exclude** | — | — | mcp_ai_messages, mcp_timeline, codex_ai_messages, mcp_memory/index/tags, IDE, context_capsule, large apps |

---

## Phase 0: Pre-Commit (Must Complete First)

### 0.1 Fix ngrok token (security)

**File:** `scripts/ngrok_tunnel.py`

- Replace hardcoded `auth_token` with `os.environ.get("NGROK_AUTH_TOKEN", "")`
- Add `NGROK_AUTH_TOKEN=` to `.env.template` (placeholder, no real value)
- Document in `docs/MCP_RUNBOOK.md`: "Set NGROK_AUTH_TOKEN in .env or environment"

### 0.2 De-index tracked runtime files

These are in `.gitignore` but still tracked. Run before any staging:

```powershell
git rm --cached mcp_ai_messages.json
git rm --cached mcp_timeline_entries.json
git rm --cached codex_workspace/persistence/collaboration/codex_ai_messages.json
git rm --cached mcp_memory/index/tags/*.json
```

### 0.3 .gitignore (already done)

- `cursor-addon/out/` — added
- Verify no other exclusions needed for this push

---

## Phase 1: README Update

**File:** `README.md`

### Additions

1. **Optional components** — Add ChatGPT MCP (GPT 5.2):
   ```
   - **ChatGPT MCP (GPT 5.2):** See [MCP Runbook](docs/MCP_RUNBOOK.md) — `mcp_sse_server.py` + `ngrok_tunnel.py` for native ChatGPT connection
   ```

2. **Reader paths** — Add row for AI agents / new collaborators:
   ```
   | AI agent / new collaborator | [BRADEN_RETURN_README](docs/BRADEN_RETURN_README.md), [PROJECT_TRUTH](PROJECT_TRUTH/README.md), [MCP Runbook](docs/MCP_RUNBOOK.md) | 15–20 min |
   ```

3. **Repository contents** — Add rows:
   ```
   | `PROJECT_TRUTH/` | Canonical truth pack (evidence-ledger, system index, operational definition) |
   | `.agent/` | Agent genomes, comms, identity (genomes, STARTUP, COMMS_DOCTRINE) |
   | `context/` | Operational context, ChatGPT sync capsule |
   | `scripts/mcp_sse_server.py`, `scripts/ngrok_tunnel.py` | ChatGPT native MCP (SSE + ngrok) |
   | `packages/joc/` | JOC shell (canonical UI) |
   ```

4. **Documentation and Links** — Add:
   ```
   - [MCP Runbook](docs/MCP_RUNBOOK.md) — HTTP, SSE, ChatGPT launch options
   - [BRADEN_RETURN_README](docs/BRADEN_RETURN_README.md) — Current state, GPT 5.2, roadmap
   - [Project Truth Pack](PROJECT_TRUTH/README.md) — Canonical system index, operational definition
   ```

5. **Status line** — Optionally refresh:
   ```
   **Status:** Advanced prototype. GPT 5.2 connected via ChatGPT MCP (2026-03-05). See [Evidence Snapshot](#evidence-snapshot) and [Risks](#risks-and-limitations).
   ```

### No changes needed (keep as-is)

- Clone URL (already sev-32/AIM-OS)
- Evidence Snapshot section (Feb 19 audit still valid; can add note: "ChatGPT MCP verified 2026-03-05")
- Architecture, core systems, benchmark workflow

---

## Phase 2: Staging and Commits

**Strategy:** Option A (logical commits) — easier rollback, clearer history.

### Commit sequence

1. **Pre-commit + de-index**
   - `chore: De-index runtime files (mcp_ai_messages, mcp_timeline, mcp_memory tags, codex_ai_messages)`
   - Files: result of `git rm --cached` (no content change, just stop tracking)

2. **ngrok fix**
   - `fix: Move ngrok auth token to NGROK_AUTH_TOKEN env var`
   - Files: `scripts/ngrok_tunnel.py`, `.env.example` (if exists or create)

3. **Audit Day docs**
   - `docs: Add Audit Day deliverables (AUDIT_01-04, MCP_RUNBOOK, CONTEXT_CANON, SALVAGE_PLAN, findings)`
   - Files: docs/AUDIT_*.md, MCP_RUNBOOK.md, CONTEXT_CANON.md, SALVAGE_PLAN, roundtable, Composer/findings

4. **PROJECT_TRUTH + context**
   - `feat: Add PROJECT_TRUTH pack and context capsule`
   - Files: PROJECT_TRUTH/, context/

5. **.agent**
   - `feat: Add .agent genomes, comms, identity infrastructure`
   - Files: .agent/

6. **SSE MCP + scripts**
   - `feat: Add SSE MCP server and ngrok tunnel for ChatGPT`
   - Files: scripts/mcp_sse_server.py, scripts/ngrok_tunnel.py, scripts/package_chatgpt_context.ps1, scripts/offline_comms, scripts/mcp_control.ps1

7. **store_memory fix**
   - `fix: store_memory accept list tags (lucid_mcp_server)`
   - Files: lucid_mcp_server.py

8. **JOC, BAS, shared**
   - `feat: Add JOC package, BAS updates, shared packages`
   - Files: packages/joc/, packages/browser-automation-service/, packages/shared/

9. **cursor-addon (src only)**
   - `feat: Cursor addon updates (commandServer, MCP)`
   - Files: cursor-addon/src/* (exclude cursor-addon/out/)

10. **README**
    - `docs: Update README for GPT 5.2, PROJECT_TRUTH, .agent, MCP Runbook`
    - Files: README.md

11. **Remaining docs**
    - `docs: Add roundtable, governance deprecation, BRADEN_RETURN_README, misc`
    - Files: BRADEN_RETURN_README, roundtable, role continuity, etc.

---

## Phase 3: Push

```powershell
git push origin codexgit-mcp-fallback-offline-comms
```

---

## Exclusions (Do Not Stage)

| Path | Reason |
|------|--------|
| mcp_ai_messages.json | Runtime, Exclude-By-Default |
| mcp_timeline_entries.json | Runtime, Exclude-By-Default |
| codex_workspace/persistence/collaboration/*.json | Runtime |
| mcp_memory/index/tags/*.json | Runtime, Exclude-By-Default |
| cursor-addon/out/* | Build output |
| IDE/ | ~12 GB, deferred |
| context_capsule_wire_and_mapper_v1/ | ~342 MB, deferred |
| apps/Globe, HyperRealH20Monolith, etc. | Deferred lane |
| data/manager_ai, data/memory, data/safety_orchestrator | Runtime |

---

## Verification Before Push

- [ ] No secrets or tokens in staged files (`ngrok` uses env var)
- [ ] `git status` shows no accidental staging of IDE, context_capsule, runtime JSON
- [ ] README renders correctly (links work)
- [ ] Clone URL in README is `https://github.com/sev-32/AIM-OS.git`

---

## Related Docs

- [GIT_UPDATE_PLAN_2026-03-05.md](GIT_UPDATE_PLAN_2026-03-05.md) — Original plan + inspection answers
- [CODEXGIT_RELEASE_SLICING_PLAN_2026-03-03.md](CODEXGIT_RELEASE_SLICING_PLAN_2026-03-03.md) — Exclude-by-default, slices

---

*Mission plan ready. No git commands executed. — Composer*
