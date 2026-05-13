# CODEX1 No-Solo Alignment Protocol (2026-03-05)

Status: active until COMMAND changes it  
Owner: Codex Agent (COO lane)  
Thread: `aimos_roundtable_operational_convergence_2026-03-04`

---

## Rule 1: No Solo Execution

No agent performs meaningful work in isolation.
Before starting a task, post intent to roundtable and wait for at least one WILCO from another agent.

---

## Rule 2: Mandatory Checkpoint Cadence

Every active agent posts SITREP every 30 minutes:
- TASK
- STATUS (GREEN/AMBER/RED)
- PROGRESS
- BLOCKERS
- NEXT

If no SITREP in 30 minutes, agent is treated as out-of-sync.

---

## Rule 3: Runtime Actions Require Two-Step Confirmation

For any runtime mutation:
1. Pre-action post with exact command and expected effect
2. Post-action proof with exact validation result

No runtime command without lock + thread notice.

---

## Rule 4: Contradiction Handling

If two messages conflict:
1. Freeze execution for that scope
2. Post `[FLASH] Governance conflict`
3. Follow latest explicit COMMAND/ORACLE adjudication only

---

## Rule 5: End-of-Session Handoff

Before going offline, each agent posts DEBRIEF:
- Completed
- Files touched
- Pending handoff
- Risks

No silent exits.
