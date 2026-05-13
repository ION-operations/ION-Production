---
atlas_package: system
system_slug: gnu-gcc
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `gnu-binutils`:** **gcc** invokes **GNU as** and **GNU ld** on typical GNU/Linux flows (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** Reference-quality C/C++ implementation for many distros (`DOCUMENTED`).  
- **`integrates_with` `elf`:** Default ELF objects on Unix-class targets (`DOCUMENTED`).  
- **`integrates_with` `dwarf`:** **`-g`** emits DWARF on typical ELF targets (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** Traditional kernel compiler (`DOCUMENTED`).  
- **`integrates_with` `riscv-isa`:** GCC includes RISC-V backend (`DOCUMENTED`).  
- **`competes_with` `clang`:** Substitutable C/C++ compilers in many environments (`INFERRED`).
