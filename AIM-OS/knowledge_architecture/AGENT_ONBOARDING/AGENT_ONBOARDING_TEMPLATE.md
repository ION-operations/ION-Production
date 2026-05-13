# AGENT ONBOARDING TEMPLATE

Use this to bootstrap a new agent folder under `knowledge_architecture/AGENT_ONBOARDING/agents/{name}/`.

## Files to create (copy/paste)
- `README.md` — Agent index, role, quick links, status
- `CONTEXT.md` — Timeline, keywords, relationships, important things
- `NAVIGATION.md` — Situation-based links to docs/code/templates
- `MISSIONS.md` — Past/current missions, status, blockers
- (Optional) `logs/` — Daily journals and mission logs

## Suggested contents
- **README.md**
  - Name, role, core system, status
  - Purpose and rationale
  - Quick links to key docs (registry, assignment plan, core system docs)
  - Relationships to other agents/systems
- **CONTEXT.md**
  - Timeline of key events
  - Keywords and important things to remember
  - Dependencies and risks
  - Upstream/downstream relationships
- **NAVIGATION.md**
  - “I need to…” sections with direct links (build, debug, integrate, document)
  - Pointers to templates, specs, indexes, code roots
- **MISSIONS.md**
  - Mission list with status (planned/active/done)
  - Notes, decisions, blockers
  - Links to mission logs
- **logs/**
  - `YYYY-MM-DD_journal.md` from `WORK_JOURNAL_TEMPLATE.md`
  - `mission_{id}.md` from `MISSIONS_LOG_TEMPLATE.md`

## First-hour checklist
- [ ] Add agent entry to `AGENT_PROFILE_REGISTRY.md`
- [ ] Create folder and 4 onboarding files
- [ ] Create today’s work journal
- [ ] Create mission log for current mission (if any)
- [ ] Review page ownership in `LUCID_IMAGE_SPECIALIST_ASSIGNMENT_PLAN.md`
- [ ] Announce active status in `MISSIONS.md`

## Standards
- Keep links current (no orphan docs)
- Preserve history (do not overwrite stateful docs without versioning)
- Confidence ≥ 0.70 before executing tasks
- Align with AIMOS documentation hierarchy (indexes → sections → leaves)

**Last Updated:** 2025-01-27

