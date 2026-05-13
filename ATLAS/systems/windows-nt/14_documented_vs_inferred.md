---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED claims

- Core layering (user/kernel, HAL, executive) (`nt-001`, `nt-003`).  
- Object/handle indirection (`nt-002` pending precise citation upgrade).  
- Win32 as API surface (`nt-004`).

## INFERRED claims

- Competitive substitution with Linux — economic/deployment inference.

## OBSERVED

- None captured in this seed.

## Open questions

- Add build-specific scheduler documentation or mark UNKNOWN per build.  
- Expand driver stack examples with WDK-cited diagrams.

## Forbidden until sourced

- Undocumented kernel structs “as stable truth”.  
- Internal exploit chain details.
