---
atlas_package: system
system_slug: netbsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# NetBSD libc — Identity

**Kind:** **NetBSD** **base** **system** **C** **library** **(libc)** **and** **dynamic** **linker** **surface** **for** **hosted** **C**/**POSIX** **on** **NetBSD** (`DOCUMENTED`, `src-netbsd-guide`).

## Boundaries

- **Not** **`glibc`**, **`musl`**, **or** **other** **BSD** **base** **libcs** — **different** **kernel** **ABIs** **and** **release** **engineering** (`DOCUMENTED`).  
- **Not** **a** **dedicated** **`netbsd`** **OS** **package** **in** **ATLAS** **(yet)** — **this** **package** **models** **libc** **only** (`DOCUMENTED`).

## Why this system matters

- **pkgsrc** **/** **cross**-**build** **themes** **and** **stable** **ABI** **discipline** **around** **base** **libc** (`DOCUMENTED` **/** `OBSERVED` **themes**).

## What this system teaches the atlas

**Keep** **NetBSD** **libc** **law** **separate** **from** **FreeBSD** **when** **auditing** **API** **and** **ABI** **claims**.
