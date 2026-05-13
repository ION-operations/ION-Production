---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Mach+BSD hybrid; Mach ports (`xnu-001`, `xnu-003`).  
- I/O Kit presence (`xnu-002` pending dedicated locator).

## UNKNOWN

- `xnu-004` Secure Enclave internals.

## Open questions

- Deeper hardware-driver claims may still need archived IOKit programming guide chapter anchors.  
- iOS-specific hardening deltas vs macOS — split claims by OS.

## Forbidden until sourced

- Detailed T2/M-series boot chain without primary Apple technical paper.
