---
atlas_package: system
system_slug: musl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **musl** as **C/POSIX** **libc** on **Linux** — **stdio**, **pthread**, **malloc**, **socket** themes (`DOCUMENTED`, `src-musl-wiki`).  
- **Static**-**linking**-**friendly** design vs **glibc** **NSS**/**iconv** **complexity** (`DOCUMENTED` design docs).  
- **GCC**/**Clang** **toolchains** that **target** **musl** (e.g. **Alpine**) (`DOCUMENTED` ecosystem).

## Out of scope

- **glibc**-only **GNU** **extensions** — use **`glibc`** (`DOCUMENTED` split).  
- **FreeBSD**/**OpenBSD** **libc** — not **musl** (`INFERRED`).  
- **libstdc++**/**libc++** — C++ runtimes (not seeded here).

## Versioning note

**musl** **releases** ship with **distro** **pinning** on **Alpine** (`INFERRED`).
