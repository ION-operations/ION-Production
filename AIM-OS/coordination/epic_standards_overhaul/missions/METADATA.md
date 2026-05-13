---
id: mission_metadata
type: mission
phase: 1
owner: Aether
status: planned
updated: 2025-10-30
---

# Mission – Metadata Standards

## Objective
Ensure required frontmatter exists and is valid across all targeted documents.

## Deliverables
- Frontmatter present (ids, titles, dates, owners, versions)
- Consistent keys and cadence fields where needed
- Gate: `knowledge_architecture/validation/METADATA_STANDARDS.validation.md` – pass

## Steps
1) Scan targeted docs for missing/invalid metadata
2) Normalize keys and values
3) Re-run lints/validators
4) Run Gate checklist; fix issues
5) PR with EPIC checklist; update tracker

## Dependencies
- Templates Library key names

## Artifacts
- Metadata scan results → `coordination/epic_standards_overhaul/artifacts/metadata/`
