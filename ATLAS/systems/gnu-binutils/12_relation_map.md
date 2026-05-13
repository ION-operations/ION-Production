---
atlas_package: system
system_slug: gnu-binutils
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `elf`:** primary object format on Unix-class GNU stacks (`DOCUMENTED`).  
- **`integrates_with` `dwarf`:** `objdump` / `readelf` expose DWARF sections (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** **gas**/**ld** with **GCC** (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** kernel build traditionally uses GNU **as**/**ld** (`DOCUMENTED` build docs).  
- **`integrates_with` `llvm-ir`:** LLVM stack may use **GNU ld** or substitute **lld** / LLVM tools (`INFERRED` toolchain choice).  
- **`integrates_with` `riscv-isa`:** multi-target **as**/**ld** includes RISC-V (`DOCUMENTED` target lists).
