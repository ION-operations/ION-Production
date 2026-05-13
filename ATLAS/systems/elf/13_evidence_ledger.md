---
atlas_package: system
system_slug: elf
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| elf-001 | ELF defines relocatable, executable, shared object, and core file classes | DOCUMENTED | `src-tis-elf` | |
| elf-002 | ELF sections commonly carry DWARF debug data (e.g. `.debug_*`) | DOCUMENTED | `src-tis-elf`; `dwarf` package | |
| elf-003 | Linux loads ELF binaries via its ELF interpreter path | DOCUMENTED | Kernel docs / `linux-kernel` package | |
