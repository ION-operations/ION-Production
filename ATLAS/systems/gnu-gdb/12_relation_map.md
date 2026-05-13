---
atlas_package: system
system_slug: gnu-gdb
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `dwarf`:** reads DWARF for source-level stepping (`DOCUMENTED`).  
- **`integrates_with` `elf`:** loads ELF binaries and shared objects (`DOCUMENTED`).  
- **`integrates_with` `gnu-gcc` / `clang`:** debug builds **`-g`** produce info GDB consumes (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** primary debugger for C/C++ on many GNU/Linux flows (`DOCUMENTED`).  
- **`integrates_with` `debug-adapter-protocol`:** IDE **adapters** often wrap GDB behind DAP (`INFERRED`).  
- **`integrates_with` `gnu-binutils`:** complementary **readelf**/**objdump** inspection vs live debugging (`INFERRED`).
