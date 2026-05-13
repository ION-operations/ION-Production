# EPIC: AIM-OS Standards Overhaul (32 Standards Integration)

**Goal:** Apply the completed 32 documentation standards across AIM-OS, align systems and repos to the perfected formats, and institutionalize validation gates for continuous quality.

**Drivers:** Historic completion of 32 standards; desire for zero drift, perfect organization, and frictionless authoring.

---

## Scope & Outcomes
- System-wide adoption of 32 standards (Phases 1–4)
- Unified navigation (SUPER_INDEX + Hierarchical Index + System Maps)
- Validation gates enforced in reviews/PRs
- Templates integrated into authoring workflow
- Rollout schedule with dependencies and clear acceptance criteria

---

## Workstreams (by Phase)

### Phase 1 — Foundational Standards
1) L0–L6 Documentation
   - Outcome: Every core/supporting system has complete L0–L4 (L6 where applicable)
   - Repos/Dirs: `knowledge_architecture/systems/*/L{0-4}_*.md`
   - Acceptance: L0–L4 present, cross-linked, passes validation gate

2) System Maps
   - Outcome: JSON5 maps exist + are referenced from L2s
   - Repos/Dirs: `knowledge_architecture/systems/*/system.map.lucid.json5`
   - Acceptance: Map validates, shows relationships, appears in SUPER_INDEX

3) System Index
   - Outcome: Master concept index entries exist for all key concepts
   - Repos/Dirs: `knowledge_architecture/SUPER_INDEX.md`
   - Acceptance: Concepts resolvable; dead links = 0

4) Metadata Standards
   - Outcome: Required frontmatter present in all specs/guides
   - Repos/Dirs: All standards/system docs
   - Acceptance: Metadata lints pass, timestamps maintained

5) Validation Framework
   - Outcome: Review/PR checklist embedded and used
   - Repos/Dirs: `knowledge_architecture/PERFECT_VALIDATION_FRAMEWORK.md`
   - Acceptance: PRs reference gate results

6) Templates Library
   - Outcome: Authoring uses templates consistently
   - Repos/Dirs: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
   - Acceptance: New/updated docs cite template version

### Phase 2 — Consciousness & Memory
7) Thought Journals
8) Decision Logs
9) Learning Logs
10) Active Context
11) Session Continuity
12) Questions for Braden
- Repos/Dirs: `knowledge_architecture/AETHER_MEMORY/*`
- Acceptance: Pipelines capture entries; indexes updated; queries validated

### Phase 3 — Planning & Goals
13) Goal Tree
14) KPI Metrics
15) Task Dependency Map
16) Project Plans
17) System Hierarchy
- Repos/Dirs: `goals/`, `knowledge_architecture/WORKFLOW_ORCHESTRATION/`, `plans/`, `knowledge_architecture/SYSTEM_HIERARCHY.md`
- Acceptance: Objectives mapped; KPIs tracked; dependencies resolvable

### Phase 4 — Supporting Standards
18–34) Timeline/History, Coordination/Communication, Navigation/Indexing, Error/Quality, Research/Ideas, Audit/Analysis, Architecture
- Repos/Dirs: See anchors in `knowledge_architecture/PHASE_4_COMPLETE_STANDARDS_BUNDLE.md`
- Acceptance: Each category has working exemplars + appears in nav

---

## Validation Gates (apply to every deliverable)
- Lint: Metadata present + valid
- Links: No dead links (internal/external)
- Nav: Listed in `HIERARCHICAL_NAVIGATION_INDEX.md` and/or `SUPER_INDEX.md`
- Map: System included in relevant system map(s)
- Template: Uses a template or justified exception
- Review: PR includes checklist with pass/fail and remediation

---

## Rollout Plan (Milestones & Dependencies)
1) M1 — Index & Maps First (Week 1)
   - Update `STANDARDS_NAV_INDEX.md`, `HIERARCHICAL_NAVIGATION_INDEX.md`, `SUPER_INDEX.md`
   - Refresh all `system.map.lucid.json5`
   - Dep: none

2) M2 — Templates + Validation (Week 1–2)
   - Embed template headers; add validation checklist to PR template
   - Dep: M1 (paths stable)

3) M3 — Phase 1 Rollout (Week 2–3)
   - L0–L4 refresh, maps cross-links, metadata pass
   - Dep: M1, M2

4) M4 — Phase 2 Rollout (Week 3)
   - Journals/Logs/Context/Continuity/Questions standards applied
   - Dep: M3

5) M5 — Phase 3 Rollout (Week 3–4)
   - Goals/KPIs/Dependencies/Plans/Hierarchy updated
   - Dep: M3, M4

6) M6 — Phase 4 Rollout (Week 4–5)
   - Timeline/Coordination/Nav/Quality/Research/Audit/Architecture
   - Dep: M5

7) M7 — Audit & Close (Week 5)
   - Full validation sweep; fix deltas; freeze indexes
   - Dep: M6

---

## Acceptance Criteria (EPIC)
- 100% of targeted documents pass validation gates
- All systems present in indices and maps
- Templates and metadata standardized
- Rollout milestones completed with sign-offs

---

## Tracking
- Master checklist lives in: `knowledge_architecture/STANDARDS_NAV_INDEX.md` (browse + jump)
- Program tracking file (suggested): `plans/EPIC_STANDARDS_TRACKING.md` (per-workstream status)


