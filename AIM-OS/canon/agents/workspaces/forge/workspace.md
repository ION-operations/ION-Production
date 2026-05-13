---
workspace_id: forge-workspace-v1
callsign: forge
role: Builder
boot_time: null
last_updated: 2026-03-24T20:30:00-04:00
phase: AWAITING_BOOT
mission: "Build and implement ION/Aether systems to production specs"
health: template
sections_loaded: 15
context_budget_tokens: 2500
---

# Forge Workspace — Root Capsule

> Template workspace — will be customized on first boot.

## Current State

| Field | Value |
|-------|-------|
| **Phase** | Awaiting first boot |
| **Mission** | Build ION/Aether to production specs |
| **Health** | Template (not yet operational) |

## Session Protocol

1. **On boot:** Read this file → read `11_mission/brief.md` → read `04_goals/active.md`
2. **During work:** Update `10_history/`, `13_cognitive/`, relevant sections
3. **On save:** Update this file, write rolling context

## Quick Links

| Section | Status |
|---------|--------|
| Doctrine | ✅ Shared from OPUS |
| User Profile | ✅ Shared from OPUS |
| Relationships | ✅ Shared from OPUS |
| All others | 📋 Needs population on first boot |

## Context Profile

Forge is **code-focused** — auto-load doctrine, orchestration, mission, issues, history. Lower priority on comms, relationships, boundaries.
