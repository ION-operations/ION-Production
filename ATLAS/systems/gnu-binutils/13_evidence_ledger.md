---
atlas_package: system
system_slug: gnu-binutils
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| bin-001 | GNU Binutils includes ld, as, objdump, readelf, ar, nm, objcopy, strip | DOCUMENTED | `src-binutils-docs` | |
| bin-002 | Tools operate on ELF-class objects on typical Linux targets | DOCUMENTED | `src-binutils-docs`; `elf` package | |
| bin-003 | Kernel build documentation references GNU assembler/linker | DOCUMENTED | `linux-kernel` build docs; `integrates_with` edge | |
