# AIM-OS Goal Map (v0.1)

**Current Phase:** Finalization + Integration for chat/IDE v0  
**Global Goal (O0):** All 8 main systems are production-ready and integrated for chat/IDE orchestration.

## System Goals (G1/G2/G3)

- **APOE (Planner/Executor)**
  - **APOE-G1 – CMC v1 Locked:** APOE emits `plan_execution` atoms per spec on every plan run; CMC history/stats used for decisions.
    - *Support tasks:* `feature/apoe-cmc-v1` (Aether/Codex) plus Alex's spec/test synchronizer & sandbox protocol keep the contract enforced.
  - **APOE-G2 – Integrations Real:** All documented APOE integrations (CMC, HHNI, VIF, SEG, SDF-CVF, CAS, TCS) have code + at least one test.
    - *Guardrail linkage:* Alex documents tier-aware edit rules and synchronizer wiring so Tier-2 integrations stay compliant.
  - **APOE-G3 – Orchestration Ready:** APOE is wired into the orchestrator path (plan from IDE/chat → APOE → CMC history → visible summary).

- **CMC (Memory)**
  - **CMC-G1:** All claimed connections (APOE, TCS, HHNI, VIF, SEG, SDF-CVF, CAS) exist in code + tests.
  - **CMC-G2:** Bitemporal storage contracts stable and documented (T0–T2).
  - **CMC-G3:** Orchestrator can query/append atoms safely from chat/IDE flows.

- **VIF, HHNI, SEG, SDF-CVF, CAS, TCS**
  - Follow the same pattern (G1: consolidation/validation done, G2: integrations real, G3: orchestration-ready); status already tracked in their Phase reports and boards.

> Use this map as a quick lens: when choosing work, prefer tasks that move some G1/G2/G3 closer to ✅, especially APOE-G1/G2/G3 while we finish Finalization.





