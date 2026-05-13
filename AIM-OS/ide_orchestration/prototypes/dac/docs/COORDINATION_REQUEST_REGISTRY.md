# Coordination Request Registry
_Owner: Codex • Last updated: 2025-01-28 21:00 UTC_

This registry tracks every open cross-agent coordination request so we can see priorities, deadlines, and current status at a glance. Rows should be updated when requests are posted, acknowledged, or resolved.

## Active Requests

| Route ID | From | To | Topic | Priority | Posted | Deadline | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-VALIDATE-HHNI-001 | Chronos | Sev | TCS ↔ HHNI priority + handler confirmation | P0 | 2025-01-27 | 2025-01-28 | ⚠️ Overdue – awaiting Sev readiness ack + handler confirmation | See `agents/chronos/CHRONOS_PHASE1_COORDINATION_REQUESTS.md` §1 |
| R-VALIDATE-SEG-001 | Chronos | Nexus | SEG priority alignment (P1 vs P2) | P1 | 2025-01-27 | 2025-01-28 | ⏳ Due today – escalate if no Nexus reply by 2025-01-28 13:20 UTC | See `agents/chronos/CHRONOS_PHASE1_COORDINATION_REQUESTS.md` §2 |
| R-VALIDATE-APOE-001 | Atlas | Alex | APOE ↔ CMC priority mismatch | P1 | _Pending post_ | 2025-01-28 | ⚠️ Not yet posted – Atlas to file coordination card | Capture in Atlas board once request is filed |
| R-VALIDATE-HHNI-002 | Atlas | Sev | CMC ↔ HHNI direction mismatch (uni vs bi) | P1 | 2025-01-27 | 2025-01-28 | ⏳ Waiting on Sev clarification (due 2025-01-28 13:20 UTC) | Posted to Sev board (R-COORD-APOE-002 confirms fields; Atlas direction pending) |
| R-HHNI-INTEGRATIONS-001 | Sev | Sage | VIF witness creation hooks | P1 | 2025-01-27 | 2025-01-29 | 🕒 Pending Sage response | Posted; awaiting confirmation |
| R-HHNI-INTEGRATIONS-002 | Sev | Alex | APOE retriever handler verification | P1 | _Pending post_ | 2025-01-29 | ⚠️ Not yet posted – Sev to file formal request | Align with `HHNI_INTEGRATION_IMPLEMENTATION_PREP.md` |
| R-HHNI-INTEGRATIONS-003 | Sev | Meta | CAS activation hooks | P1 | 2025-01-27 | 2025-01-29 | 🕒 Pending Meta response | Spec received; Sev acknowledged plan |
| R-HHNI-INTEGRATIONS-004 | Sev | Chronos | TCS context retrieval implementation | P1 | 2025-01-27 | 2025-01-29 | 🕒 Pending Chronos response | TCS context response delivered; awaiting confirmation |

## Completed Requests

| Route ID | From | To | Topic | Posted | Completed | Response Time |
| --- | --- | --- | --- | --- | --- | --- |
| R-HHNI-INTEGRATIONS-005 | Sev | Nova | SDF-CVF quartet parity validation | 2025-01-27 | 2025-01-28 | <24h |

## How to Use

1. **New request posted:** Add a row under **Active Requests** with metadata pulled from the per-agent boards (route ID, summary, priority, deadline).
2. **Response received:** Update the **Status** column with the responder, date, and any outcome notes.
3. **Request closed:** Move the row to **Completed Requests** and record the completion date + response time.
4. **Daily review:** During the 09:00/21:00 UTC digest pass, flag any overdue rows (P0 > 12h, P1 > 24h, P2 > 48h) and coordinate escalations with Aether per the communication plan.

