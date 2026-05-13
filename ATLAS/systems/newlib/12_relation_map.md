---
atlas_package: system
system_slug: newlib
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `c-language` / `elf` / `gnu-gcc` / `gnu-binutils`:** **embedded** **link** **and** **startup** **flows** (`DOCUMENTED`).  
- **`integrates_with` `riscv-isa` / `clang`:** **common** **embedded** **targets** **and** **LLVM** **toolchain** **variants** (`INFERRED`).  
- **`competes_with` `glibc` / `musl` / `freebsd-libc` / `openbsd-libc` / `netbsd-libc` / `dragonfly-libc` / `illumos-libc` / `android-bionic`:** **distinct** **libc** **implementations** (`INFERRED`).
