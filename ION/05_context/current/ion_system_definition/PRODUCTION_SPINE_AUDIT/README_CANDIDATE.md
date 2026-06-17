# ION Production-Spine Audit (candidate)

**Purpose:** evidence base for deciding how to take ION to production via a strangler-fig
extraction to a clean core (NOT a from-scratch rewrite). Launched 2026-06-17 by the ION
North Star / IONOLOGIST on operator direction ("audit first, then decide").

**Class:** candidate / not-accepted-state. No production-readiness claims. Read-only audits;
no product files moved, archived, or deleted by these audits — they PROPOSE only.

## Why (evidence that triggered this)
- Repo 6.7G; `ION/05_context` 5.8G (87%); `domain_weaver/terminal_workers` 4.7G (70%) — almost all
  mission/seat/attempt readiness/gate receipts (process exhaust).
- Product code (`ION/04_packages`) only 61M; `ion_domain_weaver.py` = 49,513 lines in one file.
- 0 vNext domains promoted to accepted state.
- `PRODUCT_READINESS_CHARTER.md` (2026-04-25 / pinned to V32) has 10 real criteria incl.
  #2 "separate demo-only surfaces from reusable production primitives" — never done.
- Diagnosis: "NOT_PRODUCTION_READY" has been lived as canon/ritual (documenting non-readiness)
  rather than a burn-down (removing blockers). Fix = clean core + owned, shrinking gap backlog.

## Reports (filled in by the three audits)
- `MONOLITH_SEAM_AUDIT.candidate.md` — internal seams of `ion_domain_weaver.py` (+ other large
  kernels); proposed decomposition, extraction order, and external public surface to preserve.
- `EXHAUST_AND_DUPLICATION_CATALOG.candidate.md` — categorization of `05_context` (5.8G) /
  `terminal_workers` (4.7G) exhaust + duplicate kernel copies; proposed archival plan; and
  load-bearing exceptions that must NOT be archived.
- `PRODUCTION_CORE_AND_VNEXT_INVENTORY.candidate.md` — product-vs-scaffold inventory; what the
  clean core should contain; ION_VNEXT reality check; charter 10-criteria implementation matrix;
  first extraction candidates.

## Synthesis (capstone — read this after the three reports)
- `PRODUCTION_SPINE_PLAN.candidate.md` — convergent conclusion + phased plan (Phase 0 hygiene ->
  Phase 1 carrier-spine pilot -> Phase 2 front-door; monolith as parallel track; readiness burn-down
  cross-cutting) + the four proposed domains + recommended first action. **Status of A/B/C: all complete (2026-06-17).**

## Context anchors
- `ION/02_architecture/PRODUCT_READINESS_CHARTER.md`, `PRODUCTION_READINESS_GAP_REGISTER.md`,
  `RELEASE_READINESS_GATE_PROTOCOL.md`, `PRODUCTION_RATIFICATION_MATRIX_PROTOCOL.md`.
- Continuity ledger: `../.ion/ACTIVE_CONTEXT_PACKAGE.md` (2026-06-17 eve entry).
- Eventual ratified plan graduates from this candidate lane to `ION/02_architecture/`.
