# Next Bounded Task

Created: 2026-03-05 03:35 ET  
Updated: 2026-03-05 15:30 ET

---

## Current Priority (2026-03-05)

**Superseded:** BAS Gate 7/8 auth run — blocked by Finding #19 (ChatGPT via BAS never worked; automation detected).

**Working path:** GPT 5.2 connected via native ChatGPT MCP (SSE+ngrok). Verified 2026-03-05.

---

## Recommended Next 3 (from AUDIT_04 + Sev)

1. **Context Pack tool** — `context_pack.get_current()` that returns canonical truth bundle (operational def, branch+commit, what's broken/working, doc index, tonight's tasks). Sev proposed; GPT 5.2 requested.

2. **Genome injection** — Connect Layer 1 (genome → system prompt) so agent identity loads at session start. Turns infrastructure into working identity system.

3. **Organizer agent spec** — Directive 2: agent whose only job is document organization (indexes, maps, prevent overwrites, tag stale docs). Draft spec for when Opus assigns.

---

## Legacy: BAS Gate 7/8 (PENDING_AUTH)

If BAS auth path is ever unblocked (Finding #19 resolved):

- Execute one live authenticated Gate 7/8 run
- Use `docs/BAS_AUTH_GATE_READINESS_PACKET_2026-03-05.md`
- Operator token `AUTH_READY` required
- Evidence bundle: timestamp, browserId, payloads, status

---

## Legacy: Allowed/Forbidden Files (BAS task only)

*Below applies only if BAS Gate 7/8 task is unblocked.*

**Allowed:**
- `docs/BAS_AUTH_GATES_7_8_PROOF_RUNBOOK_2026-03-04.md`
- `docs/BAS_AUTH_GATE_READINESS_PACKET_2026-03-05.md`
- `docs/OPUS1_BROWSER_SYSTEM_VALIDATION_REPORT_V1.md`
- `context/00_operational_definition.md`
- `context/01_current_truth.md`
- `context/03_tonight_plan.md`
- `context/99_nightly_sync_capsule.md`
- `PROJECT_TRUTH/05_operational_definition.md`
- `PROJECT_TRUTH/07_next_bounded_task.md`

---

**Forbidden:**
- `lucid_mcp_server.py`
- `scripts/mcp_*`
- BAS/JOC runtime source code (unless a verified bug forces a separately approved hotfix)
- unrelated docs outside auth-gate and truth capsule scope

---

## Legacy: Success / Proof Criteria (BAS task only)

**Success:**
1. Operator issues explicit token `AUTH_READY`.
2. Operator confirms authenticated ChatGPT session in BAS browser.
3. Gate 7 succeeds with `waitForResponse=true`.
4. Gate 8 returns non-empty extracted provider response.
5. Evidence bundle recorded in validation docs and roundtable update.
6. If auth is missing, status is explicitly `PENDING_AUTH` (not pass).

**Proof bundle:**

1. Timestamp + operator + `browserId`
2. Raw Gate 7 request/response payloads
3. Raw Gate 8 request/response payloads
4. Final status: `PASS_AUTH`, `FAIL_AUTH`, or `PENDING_AUTH`
5. Roundtable message ID referencing evidence location

---

## Ownership Suggestion (Execution Discipline)

- Live execution coordination: Opus + operator
- Verification checks: Codex
- Evidence packet and external sync packaging: Composer
