---
atlas_package: system
system_slug: uclibc
schema_version: "1.0"
last_reviewed: "2026-04-14"
evidence_grade: B
---

# Scope

## In scope

- **uClibc-ng** **as** **the** **maintained** **Linux** **libc** **implementation** **line** **for** **this** **package** (`DOCUMENTED`).  
- **POSIX/C** **surface** **and** **dynamic** **linker** **behavior** **as** **documented** **for** **supported** **architectures** (`DOCUMENTED` / `INFERRED`).

## Out of scope

- **Full** **glibc** **compatibility** **claims** — **explicit** **non-goals** **in** **upstream** **docs** (`DOCUMENTED`).  
- **Per-board** **BSP** **kernels** — **`linux-kernel`** **package** **unless** **cross**-**reference** **only**.

## Versioning note

**uClibc-ng** **releases** **and** **distribution** **pins** **(Buildroot** **/** **OpenWrt)** **drive** **visible** **revisions** (`OBSERVED`).
