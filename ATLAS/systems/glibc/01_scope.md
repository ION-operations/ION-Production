---
atlas_package: system
system_slug: glibc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **ISO C** library subset, **POSIX** and **GNU** extensions as **documented** in the **glibc** manual (`DOCUMENTED`, `src-glibc-manual`).  
- **Dynamic linker**, **NSS**, **locale**/**iconv** themes at **survey** grain (`DOCUMENTED` / `INFERRED` depth).  
- **Architecture ports** (e.g. **RISC-V** **GNU/Linux** ABI) as **ecosystem** links (`DOCUMENTED` adjacency).

## Out of scope

- **`musl`** — separate **`c-runtime`** package; **BSD** **libc** still unseeded.  
- **Kernel** **syscall** **implementation** — **`linux-kernel`**.  
- **C++** **standard** **library** — **libstdc++** / **libc++** (not seeded here).

## Versioning note

**glibc** **releases** and **distro** **backport** policy drive **symbol** **visibility** (`INFERRED` ops).
