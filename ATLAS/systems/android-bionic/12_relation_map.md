---
atlas_package: system
system_slug: android-bionic
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `android-aosp`:** **core** **platform** **C** **library** **in** **the** **AOSP** **stack** (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** **native** **userspace** **atop** **the** **device** **Linux-based** **kernel** (`DOCUMENTED`).  
- **`integrates_with` `c-language` / `elf` / `clang`:** **NDK** **and** **on-device** **ELF** **native** **link** **flows** (`DOCUMENTED` **/** `INFERRED`).  
- **`competes_with` `glibc` / `musl` / `freebsd-libc` / `openbsd-libc` / `netbsd-libc` / `dragonfly-libc` / `illumos-libc`:** **distinct** **libc** **implementations** (`INFERRED`).
