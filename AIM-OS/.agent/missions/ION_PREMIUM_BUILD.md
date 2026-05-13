---
ion_id: missions/ion_premium_build
ion_type: mission
title: "ION Premium Build — First Fully Functional ION"
authority: A2
owner: braden
confidence: 0.85
created: 2026-03-23T21:20:00-04:00
status: ACTIVE
---

# ION PREMIUM BUILD — MISSION BRIEF

> **Classification:** MANDATORY — All agents on this mission must read this first.
> **Authority:** Braden (COMMAND)
> **Date:** 2026-03-23

---

## Mission Objective

Build the first fully functional ION system by fixing all V5 wiring issues,
completing the LLM adapter, and enabling agent self-organization.

## Swarm Composition

| # | Callsign | Model | IDE | Role |
|---|----------|-------|-----|------|
| 1 | **AETHER** | Claude Opus 4.6 | Antigravity | Oracle — orchestration, governance, NO code |
| 2 | **FORGE** | Claude Opus 4.6 | Antigravity | ION Core — V5 C1-C3 fixes, engine unification |
| 3 | **ATLAS** | Gemini 3.1 Pro | Antigravity | Deep Reader — knowledge_architecture, package analysis |
| 4 | **NEXUS** | Gemini 3.1 Pro | Antigravity | ION Context — J.01 adapter, context convergence |
| 5 | **WEAVER** | Composer 2 | Cursor | ION Hierarchy — agent types, supervisor emergence |
| 6 | **SENTINEL** | Composer 2 | Cursor | ION Audit — tests, verification, documentation |

## Communication Rules

1. **ALL output goes to files.** No chat-only reasoning.
   - Path: `.agent/comms/output/{callsign}_{date}_{topic}.md`
   - Follow `protocol_ide_output.md` strictly.
2. **Read Aether's assignments before starting work.**
   - Path: `.agent/comms/output/aether_*.md`
3. **Post SITREP after each milestone.**
   - Use COMMS_DOCTRINE format.
4. **Status updates** to `.agent/comms/status/{callsign}.status.md`
5. **Governed writes require review.**
   - Any change to A0-A2 files needs Aether sign-off.
   - A3-A4 changes can proceed with SITREP notification.

## Key Reference Documents

| Document | Path |
|----------|------|
| **Master Index** | `docs/Aether-OS/MASTER_INDEX.md` |
| **Consolidation Analysis** | `docs/Aether-OS/DEEP_CONSOLIDATION_ANALYSIS.md` |
| **ION-OS Vision** | `docs/Aether-OS/ION_OS_VISION.md` |
| **V5 Consolidation** | `operation-victus/docs/ION_CONSOLIDATION_V5.md` |
| **ION Master Plan** | `operation-victus/docs/ION_MASTER_PLAN.md` |
| **Aether Constitution** | `docs/Aether-OS/AETHER_CONSTITUTION.md` |

## Priority Sequence

```
Phase 1: CONSOLIDATE (V5 C1-C3)
  → Fix enum drift, wire real engine, unify duplicates
  → Owner: FORGE
  → Gate: ION server boots, imports without error

Phase 2: THINK (J.01 + Capsules)
  → Complete LLM adapter, capsule system, context wiring
  → Owner: NEXUS
  → Gate: ION can send prompt to Gemini and get response

Phase 3: KNOW (Deep Reading + Ingestion)
  → Ingest codebase as ions, build bond graph
  → Owner: ATLAS
  → Gate: 500+ ions indexed with bonds

Phase 4: GROW (Agent Hierarchy)
  → Restore IonType.AGENT, build supervisor emergence
  → Owner: WEAVER
  → Gate: Agent ions creatable via governed write

Phase 5: VERIFY (Integration Testing)
  → Full system test, documented results
  → Owner: SENTINEL
  → Gate: All V5 k-gate criteria passing
```

## Rules of Engagement

1. **No rushing.** Today's IONv2 failure was caused by rushing. Think before acting.
2. **Read before writing.** Always understand what exists before creating new code.
3. **Follow ION spec.** Ions are markdown with YAML frontmatter. Not Python dataclasses.
4. **Governed writes.** Every mutation goes through the pipeline.
5. **Epistemic honesty.** Mark claims as OBSERVED/DERIVED/ASSUMED.
6. **File-first.** If it's not in a file, it doesn't exist.
