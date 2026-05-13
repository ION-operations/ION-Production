# AIM-OS Prime Canon Index v1

Status: Team navigation index  
Date: 2026-03-02

---

## Canonical Read Order

1. `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md`
2. `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`
3. `docs/AIM_OS_PRIME_COO_DASHBOARD_T0.md`
4. `docs/CROSS_BRANCH_CONSOLIDATION_M1_M2_STATUS_V1.md`
5. `docs/LANE_A_CHECKPOINT_D_PASSIVE_HOOK_EXECUTION_REPORT_V1.md`
6. `docs/CHECKPOINT_D_POST_EXECUTION_CONFIRMATION_V1.md`
7. `docs/LANE_B_CHECKPOINT_D_DECISION_PACKET_V1.md`
8. `docs/CHECKPOINT_D_ADJUDICATION_BRIEF_V1.md`
9. `docs/CHECKPOINT_E_ENTRY_CRITERIA_V1.md`
10. `docs/CHECKPOINT_E_ADJUDICATION_BRIEF_V1.md`
11. `docs/LANE_B_CHECKPOINT_E_DECISION_PACKET_V1.md`
12. `docs/CHECKPOINT_E_EVIDENCE_RUNBOOK_V1.md`
13. `docs/CHECKPOINT_E_EVIDENCE_APPENDIX_TEMPLATE_V1.md`
14. `docs/CHECKPOINT_E_EVIDENCE_APPENDIX_DRAFT_V1.md`
15. `docs/CHECKPOINT_E_OPEN_ITEMS_V1.md`
16. `docs/CHECKPOINT_E_EXECUTIVE_BRIEF_V1.md`
17. `docs/LANE_B_CHECKPOINT_E_ADVISORY_OBSERVABILITY_PROPOSAL_V0_1.md`
18. `docs/LANE_B_CONTEXTUAL_SYNC_CONVERGENCE_BLUEPRINT_V1.md`
19. `docs/LANE_B_MAPPER_ADAPTER_CONTRACT_V0_1.md`
20. `docs/LANE_B_PASSIVE_EMITTER_HOOK_PROPOSAL_V0_2.md`
21. `docs/PASSIVE_HOOK_IMPLEMENTATION_HANDOFF_PACKET_V0_3.md` (historical packet; execution now recorded in Lane A report)

---

## Current Operational State

- Program leadership now includes COO operations scope (`docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`) for anti-drift execution control.
- Program navigation now includes a fast executive dashboard (`docs/AIM_OS_PRIME_COO_DASHBOARD_T0.md`).
- Lane A: live machine authority (runtime seams, harness truth, supervised daemon behavior)
- Lane B: shadow superstrate authority (schema, emitter proof, adapter contract, hook proposal)
- Cross-branch consolidation (M1 + M2): documented with post-D convergence updates
- Checkpoint D constrained passive slice: implemented and validated by Lane A (off-by-default, fail-open, bounded, observational-only)
- Checkpoint E package: decision-ready (adjudication brief + decision packet + evidence runbook/template/draft)

---

## Checkpoint Queue

- Checkpoint C: Shadow emitter proof acceptance status (Lane B green)
- Checkpoint D: First constrained passive hook execution completed (follow-on expansion remains explicit-approval only)
- Post-execution confirmation: `docs/CHECKPOINT_D_POST_EXECUTION_CONFIRMATION_V1.md`
- Checkpoint D adjudication brief: `docs/CHECKPOINT_D_ADJUDICATION_BRIEF_V1.md`
- Execution report: `docs/LANE_A_CHECKPOINT_D_PASSIVE_HOOK_EXECUTION_REPORT_V1.md`
- Checkpoint E entry criteria: `docs/CHECKPOINT_E_ENTRY_CRITERIA_V1.md`
- Checkpoint E adjudication brief: `docs/CHECKPOINT_E_ADJUDICATION_BRIEF_V1.md`
- Checkpoint E decision packet: `docs/LANE_B_CHECKPOINT_E_DECISION_PACKET_V1.md`
- Checkpoint E evidence runbook: `docs/CHECKPOINT_E_EVIDENCE_RUNBOOK_V1.md`
- Checkpoint E evidence appendix template: `docs/CHECKPOINT_E_EVIDENCE_APPENDIX_TEMPLATE_V1.md`
- Checkpoint E evidence appendix draft: `docs/CHECKPOINT_E_EVIDENCE_APPENDIX_DRAFT_V1.md`
- Checkpoint E open items tracker: `docs/CHECKPOINT_E_OPEN_ITEMS_V1.md`
- Checkpoint E executive brief: `docs/CHECKPOINT_E_EXECUTIVE_BRIEF_V1.md`
- Checkpoint E advisory proposal (design-only): `docs/LANE_B_CHECKPOINT_E_ADVISORY_OBSERVABILITY_PROPOSAL_V0_1.md`

---

## Active Mission Packets

- Codex Agent execution charter: `docs/CODEX_AGENT_EXECUTION_CHARTER_V1.md`
- Claude Opus browser onboarding mission: `docs/OPUS1_ANTIGRAVITY_BROWSER_SYSTEM_ONBOARDING_MISSION_V1.md`

---

## Lane B Artifact Root

- `context_capsule_wire_and_mapper_v1/shadow_sync/`

Primary files in that root:

- `shadow_bci_v1_schema.json`
- `shadow_bci_v1_emitter.py`
- `mapper_adapter_v0_1.py`
- `fixtures/`
- `tests/`
- `out/`

---

## Anti-Collision Reminder

Do not perform uncontrolled concurrent edits to:

- `kernel_planes`
- `context_service`
- mapper core internals
- `daemon_bridge`
- core IPC routing seams

Live adoption remains explicit and checkpoint-gated.
