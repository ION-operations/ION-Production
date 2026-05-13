---
atlas_package: system
system_slug: lldb
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `clang`:** shared LLVM/Clang components for expressions and types (`DOCUMENTED`).  
- **`integrates_with` `dwarf` / `elf`:** reads DWARF in ELF on Linux (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** common debugger for Clang-built C/C++ (`DOCUMENTED`).  
- **`integrates_with` `debug-adapter-protocol`:** **lldb-dap** and VS Code **CodeLLDB**-class adapters (`DOCUMENTED` / `INFERRED`).  
- **`competes_with` `gnu-gdb`:** substitutable debuggers on many Linux developer machines (`INFERRED`).
