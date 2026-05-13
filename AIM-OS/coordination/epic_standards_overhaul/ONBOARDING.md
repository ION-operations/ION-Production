# EPIC Agent Onboarding Guide

## Purpose
Provide a fast, thorough orientation for any agent joining the EPIC standards rollout (Phase 1 focus), including project context, standards, navigation, gates, workflow, and communication.

## Read First
- Project overview: `README_CONSOLIDATED.md` and `README.md`
- Standards index: `knowledge_architecture/STANDARDS_NAV_INDEX.md`
- Hierarchical nav: `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md`
- EPIC plan: `plans/EPIC_STANDARDS_OVERHAUL.md`
- Tracking: `plans/EPIC_STANDARDS_TRACKING.md`
- Missions hub: `coordination/epic_standards_overhaul/README.md`

## Environment & Setup
- Repo root: ensure Python deps installed if running scripts
- PR flow: `.github/PULL_REQUEST_TEMPLATE.md` (gates must pass)
- Artifacts dir (shared): `coordination/epic_standards_overhaul/artifacts/`

## Standards Orientation
- 32 standards overview: `knowledge_architecture/STANDARDS_NAV_INDEX.md`
- Phase 1 details: L0–L6, maps, index, metadata, validation, templates
- Gate checklists: `knowledge_architecture/validation/` (per-standard files)

## Execution Workflow
1) Pick assigned mission (`coordination/epic_standards_overhaul/missions/*`)
2) Review Gate for your standard(s)
3) Make edits using templates; ensure metadata
4) Run Gate checklist; fix issues
5) Open PR using EPIC checklist; link Gate; update tracker
6) Post end-of-day note in `artifacts/daily_reports/`

## Communication
- Shared message board: `coordination/epic_standards_overhaul/comms/SHARED_MESSAGE_BOARD.md`
- Daily report template: `coordination/epic_standards_overhaul/comms/DAILY_REPORT_TEMPLATE.md`
- Decisions: `knowledge_architecture/AETHER_MEMORY/decision_logs/`
- Questions: `knowledge_architecture/AETHER_MEMORY/questions_for_braden/`

## Quality & Safety
- Validation gates required before merge
- Preserve versioning in `AETHER_MEMORY/active_context/*`
- Snapshot before large changes when possible
