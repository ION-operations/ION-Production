# Audit Request Inbox

**Purpose:** Other agents can submit audit requests for Composer to investigate.  
**Audience:** Codex Agent, Claude Opus 4.6, gemini, Codex-BAS, Codex-MCP, Codex-Context, and any AIM-OS agent.

---

## How to Submit a Request

1. **Create a new file** in `docs/Composer/requests/` using this naming pattern:
   ```
   REQUEST_YYYY-MM-DD_AgentName_ShortTopic.md
   ```
   Example: `REQUEST_2026-03-03_Codex_BAS_contract_verification.md`

2. **Use the template** below (or copy from `TEMPLATE.md`).

3. **Save the file.** Composer checks this folder during investigations and will pick up pending requests.

If MCP transport is down, also post a pointer message in:

- `docs/communications_mcp_down/threads/THREAD_<thread_id>.md`

and reference the request path so Composer and other agents can track it without MCP.

---

## What Composer Can Audit

- **Seam breakage** — Contract mismatches between clients and services (e.g. BAS ↔ JOC)
- **Code verification** — Trace flows, verify types, confirm endpoints
- **Message store / MCP** — Validity, merge logic, cross-agent visibility
- **Documentation** — Stale refs, broken links, missing docs
- **Store / state** — jocStore vs sessionStore, data flow consistency
- **Build / test** — TypeScript, E2E scripts, dependency issues
- **Onboarding** — Canonical IDs, guidance completeness

---

## Response Flow

- Composer adds findings to `FINDINGS_MASTER_LIST.md`
- Composer creates an audit report in `audits/` when scope warrants it
- Braden receives summaries in chat; reports live in `docs/Composer/`
- Requesting agent can reference the audit report by path

---

## Current Requests

| File | Requester | Topic | Status |
|------|-----------|-------|--------|
| *(none yet)* | — | — | — |

*Composer checks this inbox at session start. Last checked: 2026-03-04.*
