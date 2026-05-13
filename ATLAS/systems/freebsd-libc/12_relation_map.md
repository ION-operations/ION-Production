---
atlas_package: system
system_slug: freebsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `freebsd`:** **base** **system** **userland** **component** (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** **hosted** **C** **/** **POSIX** **entry** **points** (`DOCUMENTED`).  
- **`integrates_with` `elf`:** **ELF** **dynamic** **linking** **on** **supported** **targets** (`DOCUMENTED`).  
- **`integrates_with` `gnu-gcc` / `gnu-binutils` / `clang`:** **typical** **toolchain** **link** **flows** (`DOCUMENTED` **/** `INFERRED`).  
- **`competes_with` `glibc` / `musl` / `openbsd-libc`:** **distinct** **libc** **implementations** (`INFERRED`).
