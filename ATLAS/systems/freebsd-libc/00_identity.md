---
atlas_package: system
system_slug: freebsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# FreeBSD libc — Identity

**Kind:** **FreeBSD** **base** **system** **C** **library** **(libc)** **and** **dynamic** **linker** **surface** **for** **hosted** **C**/**POSIX** **on** **FreeBSD** (`DOCUMENTED`, `src-freebsd-handbook-libc`).

## Boundaries

- **Not** **`glibc`** **or** **`musl`** — **different** **kernel** **ABIs** **and** **release** **engineering** (`DOCUMENTED`).  
- **Not** **`openbsd-libc`** — **separate** **BSD** **lineage** **and** **syscall** **policy** (`DOCUMENTED`).  
- **Not** **`freebsd`** **(OS** **package)** **alone** — **libc** **is** **a** **userland** **component** **within** **the** **base** **system** (`DOCUMENTED`).

## Why this system matters

- **Default** **userland** **C** **ABI** **for** **FreeBSD** **ports** **and** **jail** **/`docker`**-**class** **workflows** **that** **share** **ELF** **linking** **themes** (`DOCUMENTED` **/** `OBSERVED`).

## What this system teaches the atlas

**Model** **BSD** **base** **libc** **explicitly** **when** **contrasting** **Linux** **`glibc`**/**`musl`** **graphs**.
