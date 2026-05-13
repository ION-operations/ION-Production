---
atlas_package: system
system_slug: freebsd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Jails, Capsicum, ZFS, base system integration (`fbd-001`–`fbd-004`).

## INFERRED

- Linux substitution; Docker ecosystem overlap.

## Open questions

- UVM vs VM subsystem naming in current docs — align wording.  
- bhyve package (hypervisor) — separate ATLAS slug.

## Forbidden until sourced

- “More secure than Linux” absolutes.
