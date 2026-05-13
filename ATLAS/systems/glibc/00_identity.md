---
atlas_package: system
system_slug: glibc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# GNU C Library (glibc) — Identity

**Kind:** **GNU** implementation of the **C standard library** and much of **POSIX** userland API on **GNU/Linux** and related **GNU** triplets — includes the **dynamic linker** (**`ld-linux`**) (`DOCUMENTED`, `src-glibc-manual`, `src-glibc-sourceware`).

## Boundaries

- **Not** **`linux-kernel`** — **syscalls** cross into the kernel, but **API** and **ABI** policy live in **userland** (`DOCUMENTED`).  
- **Not** **`gnu-gcc`** or **`clang`** — compilers **target** **glibc**; they are not the **libc** (`DOCUMENTED`).  
- **Not** **`elf`** — **ELF** is the **object** format; **glibc** ships **shared objects** and **interpreter** semantics (`DOCUMENTED`).  
- **Not** **`c-language`** — ISO **C** is the **language** spec; **glibc** is one **runtime** implementation (`DOCUMENTED`).

## Why this system matters

- **Dominant** **libc** on many **Linux** distros; **ABI** stability and **symbol versioning** shape userspace (`DOCUMENTED`).  
- **Joins** **compiler**/**linker**/**debugger** packages to **kernel** **syscall** reality for **ION** “OS stack” audits.

## What this system teaches the atlas

- Separate **libc** from **toolchain** and **kernel** when reasoning about **containers**, **compat**, and **security** updates.
