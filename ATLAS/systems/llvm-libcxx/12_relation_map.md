---
atlas_package: system
system_slug: llvm-libcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `clang`:** **`-stdlib=libc++`** **selects** **libc++** (`DOCUMENTED`).  
- **`integrates_with` `llvm-lld`:** **link** **stage** **resolves** **libc++** **symbols** (`DOCUMENTED`).  
- **`competes_with` `gnu-libstdcxx`:** **substitutable** **C++** **stdlibs** (`INFERRED`).  
- **`integrates_with` `glibc` / `musl`:** **platform** **C** **library** **under** **C++** **runtime** (`DOCUMENTED` / `INFERRED`).  
- **`integrates_with` `llvm-libcxxabi`:** **ABI** **runtime** **linked** **with** **typical** **libc++** **builds** (`DOCUMENTED`).
