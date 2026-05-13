---
atlas_package: system
system_slug: dwarf
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Information leakage

**Debug** **builds** **expose** **symbols**, **paths**, **types** — **strip** **for** **release** (`DOCUMENTED` practice).

## Stripping

**`strip`** **/** **linker** **flags** **remove** **or** **separate** **debug** (`DOCUMENTED` toolchain).
