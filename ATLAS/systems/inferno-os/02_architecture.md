---
atlas_package: system
system_slug: inferno-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture

## Three-layer story (survey)

1. **Limbo** — application language (C-like syntax, concurrency primitives in surveys).  
2. **Dis** — virtual machine bytecode.  
3. **Styx** — distributed resource access (Plan 9 **9P** family) (`DOCUMENTED`, `src-wiki-inferno`).

## Namespace and resources

Inferno adopts **file-like** naming and **mount** concepts compatible with Plan 9 thinking — **not** a full Plan 9 kernel replacement in every deployment (`DOCUMENTED` overview; **INFERRED** exact equivalence).

## Hosted vs native

**Hosted Inferno** runs as user process on host OS; **native** builds exist in project history — **HISTORICAL** / **DOCUMENTED** per release notes when cited.
