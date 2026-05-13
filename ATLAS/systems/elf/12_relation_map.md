---
atlas_package: system
system_slug: elf
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `dwarf`:** debug sections inside ELF objects (`DOCUMENTED`).  
- **`integrates_with` `llvm-ir`:** backends emit ELF objects (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** `execve` / ELF loader path (`DOCUMENTED`).  
- **`integrates_with` `unified-kernel-image`:** UKI bundles an ELF kernel in a PE envelope (`DOCUMENTED` UKI narrative).  
- **`integrates_with` `c-language` / `riscv-isa`:** typical C toolchain objects and RISC-V ELF psABI adjacency (`DOCUMENTED` / `INFERRED`).  
- **`integrates_with` `debug-adapter-protocol`:** debuggers consume symbols often rooted in ELF + DWARF (`INFERRED`).
