# Standards Rollout Backlog (Actionable)

Purpose: Apply the 32+ standards across the repo with clear, verifiable steps.
Owner: Aether
Status: Draft (ready to execute)

## Workstreams

1) Foundational (L0–L6, Maps, Indexes, Metadata, Validation, Templates)
- Inventory: List all systems in `knowledge_architecture/systems/*`
- Verify: Each has L0–L6 files with required frontmatter
- Maps/Indexes: Confirm presence and format; convert legacy where needed
- Metadata: Enforce required fields across docs
- Validation: Add checks/scripts; document in Validation Framework
- Templates: Ensure templates folder is referenced in each standard

2) Consciousness (Thought, Decision, Learning, Active Context, Session, Questions)
- Seed: Ensure directories exist under `AETHER_MEMORY/*`
- Create: Baseline examples per standard; link from README
- Wire: Reference in `.cursorrules` and ops guides

3) Planning & Goals (Goal Tree, KPI, Task Map, Project Plans, System Hierarchy)
- Sync: `goals/` files with latest standards
- Map: Ensure `SYSTEM_HIERARCHY.md` is authoritative and linked
- Plans: Update existing plans to new template

4) Supporting (Timeline, Ledger, Coordination, Status, Dashboard, SUPER_INDEX, Navigation,
   Error Intelligence, Test Docs, Quality Metrics, Ideas, Research, Audit, Analysis, Atlas, Config)
- Create: Missing shells where absent
- Migrate: Legacy docs into new structures
- Link: Cross-reference from README and dashboards

## Per-Standard Task Template

- Standard: <name>
- Scope: system(s)/folders affected
- Actions:
  - Inventory targets
  - Apply template/metadata
  - Validate with checklist
  - Link from indices
- Exit Criteria:
  - Files present; metadata valid; references updated
  - Validation check passes

## Priority Order (execute top-down)
1. Metadata + Validation
2. L0–L6 coverage
3. System Maps + Indexes
4. Consciousness set
5. Planning set
6. Remaining supporting

## Short Sprints (initial 3)
- Sprint 1: Metadata/Validation sweep (repo-wide)
- Sprint 2: L0–L6 coverage completion (core systems)
- Sprint 3: Maps/Indexes normalization (core systems)

## Metrics
- Coverage % per standard
- Validation pass rate
- Root files ≤ 10
- Number of floating files (target 0)

## Tracking
- Use `active_work/move_ledger.md` for moves
- Record updates in `reports/status/YYYY-MM-DD_status.md`
