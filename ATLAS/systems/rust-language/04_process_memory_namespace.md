---
atlas_package: system
system_slug: rust-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Stack vs heap

**Stack** allocation for fixed-size locals; **heap** via **`Box`** / collections (`DOCUMENTED`, `src-rust-reference`).

## Modules

**`mod`** hierarchy maps to **filesystem** paths by convention (`DOCUMENTED`, `src-rust-reference`).
