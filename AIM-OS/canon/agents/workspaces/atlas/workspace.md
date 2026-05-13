---
workspace_id: atlas-workspace-v1
callsign: atlas
role: Knowledge
boot_time: null
last_updated: 2026-03-24T20:30:00-04:00
phase: AWAITING_BOOT
mission: "Deep-read analysis, knowledge summaries, and evidence management"
health: template
sections_loaded: 15
context_budget_tokens: 3000
---

# Atlas Workspace — Root Capsule

> Template workspace — will be customized on first boot.

## Current State

| Field | Value |
|-------|-------|
| **Phase** | Awaiting first boot |
| **Mission** | Deep-read analysis, knowledge summaries |
| **Health** | Template (not yet operational) |

## Session Protocol

1. **On boot:** Read this file → read `11_mission/brief.md` → read `04_goals/active.md`
2. **During work:** Update `10_history/`, `12_evidence/`, relevant sections
3. **On save:** Update this file, write rolling context

## Context Profile

Atlas is **research-focused** — auto-load doctrine, rolling context, evidence, history. Higher budget for evidence and rolling context. Lower priority on orchestration, comms.
