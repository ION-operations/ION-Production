---
atlas_package: system
system_slug: illumos-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `c-language`:** **hosted** **C** **/** **POSIX** **entry** **points** (`DOCUMENTED`).  
- **`integrates_with` `elf`:** **ELF** **dynamic** **linking** **on** **supported** **targets** (`DOCUMENTED`).  
- **`integrates_with` `gnu-gcc` / `gnu-binutils` / `clang`:** **typical** **distribution** **toolchain** **flows** (`DOCUMENTED` **/** `INFERRED`).  
- **`competes_with` `glibc` / `musl` / `freebsd-libc` / `openbsd-libc` / `netbsd-libc` / `dragonfly-libc`:** **distinct** **libc** **implementations** (`INFERRED`).
