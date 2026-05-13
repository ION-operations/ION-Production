---
atlas_package: system
system_slug: openbsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# OpenBSD libc — Identity

**Kind:** **OpenBSD** **base** **system** **C** **library** **(libc)** **and** **dynamic** **linker** **surface** **for** **hosted** **C**/**POSIX** **on** **OpenBSD** (`DOCUMENTED`, `src-openbsd-faq`).

## Boundaries

- **Not** **`glibc`**, **`musl`**, **or** **`freebsd-libc`** — **different** **BSD** **policies** **and** **ABI** (`DOCUMENTED`).  
- **Not** **a** **dedicated** **`openbsd`** **OS** **package** **in** **ATLAS** **(yet)** — **this** **package** **models** **libc** **only** (`DOCUMENTED`).

## Why this system matters

- **Security**-**forward** **libc** **choices** **and** **pledge**/**unveil** **adjacency** **in** **OpenBSD** **manual** **sets** (`DOCUMENTED` **themes**).

## What this system teaches the atlas

**Keep** **OpenBSD** **libc** **law** **separate** **from** **FreeBSD** **when** **auditing** **API** **and** **ABI** **claims**.
