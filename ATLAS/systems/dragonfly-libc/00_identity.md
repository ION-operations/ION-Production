---
atlas_package: system
system_slug: dragonfly-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# DragonFly BSD libc — Identity

**Kind:** **DragonFly BSD** **base** **system** **C** **library** **(libc)** **and** **dynamic** **linker** **surface** **for** **hosted** **C**/**POSIX** **on** **DragonFly** (`DOCUMENTED`, `src-dfly-handbook`).

## Boundaries

- **Not** **`glibc`**, **`musl`**, **or** **other** **BSD** **base** **libcs** — **different** **kernel** **ABIs** **and** **release** **engineering** (`DOCUMENTED`).  
- **Not** **a** **dedicated** **DragonFly** **OS** **package** **in** **ATLAS** **(yet)** — **this** **package** **models** **libc** **only** (`DOCUMENTED`).

## Why this system matters

- **Kernel** **/** **userland** **boundary** **themes** **(DragonFly** **architecture)** **adjacent** **to** **libc** **and** **dynamic** **linking** (`DOCUMENTED` **/** `INFERRED` **themes**).

## What this system teaches the atlas

**Keep** **DragonFly BSD** **libc** **law** **separate** **from** **FreeBSD** **when** **auditing** **API** **and** **ABI** **claims**.
