# Canonical Doc Index

Created: 2026-03-05 03:24 ET  
Method: direct doc inspection + canonical read-order files + supersedes/historical markers

---

## A) Canonical Docs (Use First)

### Tier 0 - Architecture and Program Doctrine

1. `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md`  
- Master architecture doctrine and lane model.

2. `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`  
- Canonical read order and explicit anti-collision boundaries.

3. `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`  
- COO execution constraints and anti-drift controls.

4. `docs/AIM_OS_PRIME_COO_DASHBOARD_T0.md`  
- Program-level operational dashboard view.

### Tier 1 - Current Coordination Canon

1. `docs/roundtable/START_HERE.md`
2. `docs/roundtable/IDENTITY_CANON.md`
3. `docs/roundtable/decisions/DECISION_LOG.md`
4. `docs/communications_mcp_down/WRITE_POLICY.md`
5. `docs/communications_mcp_down/threads/THREAD_aimos_roundtable_operational_convergence_2026-03-04.md`

### Tier 2 - Browser/JOC Operational Surface

1. `docs/OPUS1_ANTIGRAVITY_BROWSER_SYSTEM_ONBOARDING_MISSION_V1.md`
2. `docs/OPUS1_BROWSER_SYSTEM_RUNBOOK_V1.md`
3. `docs/OPUS1_BROWSER_SYSTEM_VALIDATION_REPORT_V1.md`
4. `docs/OPUS1_JOC_GOALS_AND_ROADMAP.md`
5. `docs/JOC_MASTER_PLAN.md`

### Tier 3 - Active Truth Capsules (External ChatGPT sync)

1. `context/00_operational_definition.md`
2. `context/01_current_truth.md`
3. `context/02_canonical_map.md`
4. `context/03_tonight_plan.md`
5. `context/99_nightly_sync_capsule.md`
6. `context/README.md`

---

## B) Obsolete / Duplicate / Historical (Do Not Lead With)

| Doc | Classification | Evidence |
|---|---|---|
| `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md` | superseded | V3 header explicitly says "Supersedes V2" |
| `docs/PASSIVE_HOOK_IMPLEMENTATION_HANDOFF_PACKET_V0_3.md` | historical | Canon index marks it historical packet |
| `packages/mcp_server/README.md` | alternate path (non-primary) | Describes separate server on `:8000`; current team canonical transport is `:5001` via fallback/monolith |
| `docs/agents/ROLE_CONTINUITY_CANON.md` | historical/conflicting | Earlier role map conflicts with later `docs/roundtable/IDENTITY_CANON.md` (newer + mandatory) |
| `docs/ROLE_CONTINUITY_STATE.md` | historical snapshot | State snapshot tied to earlier recovery window; not current evergreen governance canon |
| `docs/ARCHITECTURE_OVERVIEW.md` | partially stale | Lists MCP integration as 93 tools; parity check now proves 103 |
| `docs/cross_model/MCP_TOOL_SPECIFICATIONS.md` | historical proposal | 2025 tool-spec proposal, not current runtime source of truth |
| `docs/WORK_STATUS_AND_WHAT_NEEDS_HELP.md` | stale operational scope | Last updated `2026-02-24`, mostly Globe/ION scope |
| Role claims embedded inside thread messages that conflict with `IDENTITY_CANON` | non-canonical incident chatter | Conflicting role assertions documented in roundtable thread and DEC log |

---

## C) Important But Hard to Find

| Doc | Why Important |
|---|---|
| `docs/roundtable/CODEX1_ACTIONS_AND_IMPACT_REPORT_2026-03-04.md` | Explicit incident accountability and runtime mutation record |
| `docs/roundtable/CODEX1_DEEP_RESEARCH_SYNTHESIS_PACKET_2026-03-05.md` | Evidence-backed convergence packet connecting doctrine to P0-P2 execution |
| `docs/GIT_HYGIENE_RECOVERY_PACKET_2026-03-04.md` | Drift/noise root-cause analysis and cleanup options |
| `docs/Composer/FINDINGS_MASTER_LIST.md` | Live list of seam failures and resolved/ongoing findings (#10/#11 critical for JOC/BAS) |
| `context/COMPOSER_OWNERSHIP.md` | Delegation intent for ChatGPT packaging (currently has one stale filename reference) |

---

## D) Invariant / Guardrail Docs

| Doc | Invariant Defined |
|---|---|
| `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md` | Sovereignty split and forbidden drift between mapper/daemon/kernel/superstrate |
| `docs/AIM_OS_PRIME_CANON_INDEX_V1.md` | Canonical read sequence and live seam anti-collision list |
| `docs/roundtable/IDENTITY_CANON.md` | Identity map, lanes, and conflict-resolution chain |
| `docs/communications_mcp_down/WRITE_POLICY.md` | No manual thread edits; script-only message writes |
| `DO_NOT_TOUCH_MCP.md` | Runtime guardrail around MCP mutation |

---

## E) Missing or Uncertain References

| Reference | Result |
|---|---|
| `docs/MCP_SYSTEMS_CLARIFICATION.md` | Not found in repo at this path |
| Competing role-map docs (`docs/agents/ROLE_CONTINUITY_CANON.md` vs `docs/roundtable/IDENTITY_CANON.md`) | Roundtable doc treated as current canon; older map remains in-tree without explicit deprecation header |

If a referenced document is missing, do not recreate from memory; resolve by path search or mark uncertain.
