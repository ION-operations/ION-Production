---
atlas_package: system
system_slug: llvm-libcxxabi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `llvm-libcxx`:** **paired** **C++** **stdlib** **and** **ABI** **runtime** **on** **LLVM** **stacks** (`DOCUMENTED`).  
- **`integrates_with` `clang` / `llvm-lld`:** **toolchain** **produces** **and** **links** **ABI** **objects** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `musl`:** **unwinding** **and** **low-level** **services** **interact** **with** **C** **library** **/** **pthread** **layers** (`DOCUMENTED` / `INFERRED`).
