---
atlas_package: system
system_slug: uclibc
schema_version: "1.0"
last_reviewed: "2026-04-14"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel` / `elf` / `c-language` / `gnu-gcc` / `gnu-binutils`:** **Linux** **ELF** **embedded** **flows** (`DOCUMENTED`).  
- **`integrates_with` `clang` / `riscv-isa`:** **cross** **compilation** **and** **architecture** **ports** (`INFERRED`).  
- **`competes_with` `glibc` / `musl` / hosted** **BSD** **libcs** / **`illumos-libc` / `android-bionic` / `newlib` / `wasi-libc`:** **distinct** **libc** **implementations** (`INFERRED`).
