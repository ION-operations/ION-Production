---
atlas_package: system
system_slug: clang
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `llvm-ir`:** Clang emits LLVM IR for optimization and codegen (`DOCUMENTED`).  
- **`integrates_with` `llvm-lld`:** Driver can select **lld** (`DOCUMENTED`, `-fuse-ld=lld`).  
- **`integrates_with` `gnu-binutils`:** Typical **GNU/Linux** triplets use **GNU as/ld** unless overridden (`DOCUMENTED` / `INFERRED`).  
- **`integrates_with` `c-language`:** Primary **C/C++** compiler front end in LLVM ecosystem (`DOCUMENTED`).  
- **`integrates_with` `dwarf`:** **`-g`** debug info generation (usually **DWARF** on ELF targets) (`DOCUMENTED`).  
- **`integrates_with` `elf`:** Default object format on Unix-class targets (`DOCUMENTED`).  
- **`integrates_with` `language-server-protocol`:** **clangd** speaks **LSP** (`DOCUMENTED`).
