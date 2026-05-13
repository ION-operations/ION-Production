---
atlas_package: system
system_slug: wasi-libc
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `wasi` / `webassembly` / `c-language` / `clang` / `llvm-lld`:** **WASI** **Wasm** **toolchain** **sysroot** (`DOCUMENTED`).  
- **`integrates_with` `wasm-component-model`:** **component** **tooling** **often** **shares** **Wasm** **link** **ecosystem** (`INFERRED`).  
- **`integrates_with` `gnu-libstdcxx` / `llvm-libcxx` / `llvm-libcxxabi`:** **C++** **on** **Wasm** **targets** **may** **layer** **above** **wasi-libc** (`INFERRED`).  
- **`competes_with` hosted libcs:** **distinct** **libc** **implementation** **for** **Wasm** **vs** **native** **OS** **userlands** (`INFERRED`).
