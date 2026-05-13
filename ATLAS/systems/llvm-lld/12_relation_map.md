---
atlas_package: system
system_slug: llvm-lld
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `llvm-ir`:** LTO and codegen pipeline feed the linker (`DOCUMENTED`).  
- **`integrates_with` `elf`:** ELF linking on Unix-class targets (`DOCUMENTED`).  
- **`competes_with` `gnu-binutils`:** **lld** vs **GNU ld** in the link role (`INFERRED` substitutable class).  
- **`integrates_with` `c-language`:** **Clang** drives **lld** (`DOCUMENTED` / `INFERRED`).  
- **`integrates_with` `riscv-isa`:** RISC-V target support in LLVM/lld (`DOCUMENTED` target matrix themes).
