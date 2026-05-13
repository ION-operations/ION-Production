---
atlas_package: system
system_slug: llvm-ir
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Supply chain

**Compiler** **is** **trust** **anchor** — **malicious** **IR** **can** **embed** **unsound** **assumptions** (`INFERRED` threat model).

## Sanitizers

**LLVM** **sanitizer** **passes** — **orthogonal** **to** **IR** **grammar** (`DOCUMENTED` LLVM project).
