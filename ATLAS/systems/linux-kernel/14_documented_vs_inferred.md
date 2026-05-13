---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Documented vs inferred

## DOCUMENTED claims

- Core architecture and isolation primitives (`lk-001`–`lk-004`).  
- Scheduler default class (`lk-005`) with version caveat.

## INFERRED claims

- **Market dominance** statements — add economic/reporting sources if used in narrative.

## OBSERVED

- Distro-specific default configs — observe per distribution; not kernel monolith truth.

## Open questions

- Real-time `PREEMPT_RT` merge status over time — track with dated sources.  
- Formal verification subsets (e.g., research branches) — separate package?

## Forbidden until sourced

- Exact line-level exploitability assessments.  
- Hidden vendor backdoors — treat as UNKNOWN absent evidence.
