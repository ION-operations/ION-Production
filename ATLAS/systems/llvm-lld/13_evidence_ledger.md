---
atlas_package: system
system_slug: llvm-lld
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lld-001 | lld is LLVM’s linker subproject | DOCUMENTED | `src-lld-home` | |
| lld-002 | lld links ELF on Unix-class targets | DOCUMENTED | `src-lld-cg` | |
| lld-003 | Clang can select lld via -fuse-ld=lld | DOCUMENTED | Clang docs (see `c-language` / LLVM docs cross-read) | |
