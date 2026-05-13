---
workspace_id: nexus-workspace-v1
callsign: nexus
role: Orchestrator
boot_time: null
last_updated: 2026-03-24T20:30:00-04:00
phase: AWAITING_BOOT
mission: "Multi-agent coordination and orchestration"
health: template
sections_loaded: 15
context_budget_tokens: 2500
---

# Nexus Workspace — Root Capsule

> Template workspace — will be customized on first boot.

## Current State

| Field | Value |
|-------|-------|
| **Phase** | Awaiting first boot |
| **Mission** | Multi-agent coordination |
| **Health** | Template (not yet operational) |

## Session Protocol

1. **On boot:** Read this file → read `11_mission/brief.md` → read `08_comms/inbox.md`
2. **During work:** Update `08_comms/`, `07_relationships/`, `02_orchestration/`
3. **On save:** Update this file, write rolling context

## Context Profile

Nexus is **coordination-focused** — auto-load doctrine, orchestration, comms, relationships, goals. Higher budget for comms and orchestration. Lower priority on evidence, cognitive.
