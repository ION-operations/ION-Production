---
atlas_package: system
system_slug: c-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Memory safety

**No** mandatory bounds checking on arrays — **UB** on overflow (`DOCUMENTED`, `src-wiki-c`).

## Mitigations

**Modern** defenses are **toolchain** + **runtime** (ASan, stack canaries) — **not** language guarantees (`DOCUMENTED` industry practice).
