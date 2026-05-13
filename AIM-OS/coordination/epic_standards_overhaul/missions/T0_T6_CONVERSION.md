# Mission – T0–T6 Conversion (Non-destructive)

## Objective
Create T0–T6 documentation for all systems using the latest standards without overwriting existing L0–L4. Prepare for a clean cutover after review.

## Naming & Placement
- Place T-level files next to L-level: `knowledge_architecture/systems/<system>/T{0-6}_*.md`
- Add banner at top: “Transitional T-level doc; supersedes L-level after acceptance.”

## Priority Hierarchy (convert in this order)
1) Core: CMC → HHNI → VIF → APOE → SEG → SDF-CVF → CAS
2) Supporting: Timeline Context → Cross-Model → Dual-Prompt → MCP Integration
3) Remaining systems/components referenced by core

## Deliverables
- T0–T6 for each system (at least T0–T3 required for first pass)
- Indices updated to include T-level alongside L-level
- Gate: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md` – pass

## Steps
1) For each system, copy structure from L-level docs, then upgrade to latest templates
2) Update content to current standards (links, diagrams, examples)
3) Add T-level metadata and banner
4) Update indices/maps to include T-level
5) Run T0–T6 Gate; fix issues
6) PR per system; update EPIC tracker rows with T-level completion

## Cutover Plan
- After review, rename/migrate T→L (or L→legacy, T→L)
- Re-run L0–L6 Gate post-cutover

## Artifacts
- Notes and diffs → `coordination/epic_standards_overhaul/artifacts/t0_t6/`
