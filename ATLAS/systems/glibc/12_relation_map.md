---
atlas_package: system
system_slug: glibc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **syscall** **boundary** (`DOCUMENTED`).  
- **`integrates_with` `gnu-gcc` / `gnu-binutils` / `elf`:** **link**, **load**, **ABI** (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** **standard** **library** **face** of **C** on **GNU/Linux** (`DOCUMENTED`).  
- **`integrates_with` `gnu-gdb` / `lldb`:** **debug** **of** **libc-linked** **programs** (`DOCUMENTED` / `INFERRED`).  
- **`competes_with` `musl`:** **Linux** **libc** **substitution** **class** (`INFERRED`).
