# Operational Spine

Created: 2026-03-05 03:30 ET

---

## 1) Smallest Real Path Through AIM-OS (Current)

Primary operator path:

1. Operator opens JOC (`:5011`)  
2. JOC uses BAS API (`:5002`)  
3. BAS controls browser session and interacts with ChatGPT UI  
4. Team coordination and memory sidecar run through MCP (`:5001`)

In short:
`JOC UI -> BAS runtime -> Browser provider (ChatGPT)`  
with `MCP` as coordination/memory rail.

---

## 2) What Already Works

- MCP health and tool execution work via `:5001` (`get_memory_stats`, `get_ai_messages` tested).
- BAS health works via `:5002`.
- BAS browser lifecycle flow works (launch -> navigate -> status -> close).
- JOC builds successfully.
- BAS builds and tests successfully.
- MCP tool surface parity is verified (`103 listed = 103 callable`).

---

## 3) What Almost Works

- Authenticated ChatGPT response loop is still login-gated:
  - transport can succeed with real browser IDs
  - provider reply/extraction proof requires an authenticated provider session

Dispatch/browserId seam itself is now hardened and no longer the critical blocker.

---

## 4) What Must Be Restored

No full subsystem currently requires full restore for baseline operation; core surfaces are up now.

What must be restored is **discipline stability**:
- identity/lane adherence
- lock/write protocol adherence
- bounded task execution (no cross-surface panic edits)

---

## 5) What Must Be Integrated

1. Full-store convergence beyond Dispatch: `jocStore` display surfaces still diverge from `sessionStore` runtime truth.
2. Auth state awareness in runtime evidence flow: no response-automation claims without authenticated provider session.
3. ChatGPT context packaging flow must remain centralized through Composer without path drift.
4. Context-system canon needs explicit lane-bound consolidation decision to reduce competing mapper paths.

---

## 6) What Blocks Full Operational Status

1. Authenticated ChatGPT response-gate proof (login-dependent) is pending.
2. High repo churn/noise (`git status` shows broad multi-area modifications).
3. Governance drift risk under pressure (identity/lane collisions can invalidate otherwise working runtime).

---

## 7) Operational Spine Conclusion

AIM-OS is not missing a core stack.  
The stack exists; the current critical work is **integration + coherence + proof**, not rebuild.
