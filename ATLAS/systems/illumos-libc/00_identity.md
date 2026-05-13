---
atlas_package: system
system_slug: illumos-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# illumos libc — Identity

**Kind:** **illumos** **core** **distribution** **C** **library** **(libc)** **and** **dynamic** **linker** **surface** **for** **hosted** **C**/**POSIX** **on** **illumos** **(Solaris**/**ON** **lineage)** (`DOCUMENTED`, `src-illumos-dev-guide`).

## Boundaries

- **Not** **`glibc`**, **`musl`**, **or** **BSD** **base** **libcs** — **different** **ABI** **and** **linker** **conventions** (`DOCUMENTED`).  
- **Not** **a** **dedicated** **`illumos-distribution`** **(e.g.** **OpenIndiana**/**OmniOS)** **OS** **package** **in** **ATLAS** **(yet)** — **this** **package** **models** **libc** **only** (`DOCUMENTED`).

## Why this system matters

- **Stable** **link** **/loader** **ABI** **themes** **and** **Zones**/**SMF**-**adjacent** **userland** **culture** **on** **illumos** **distributions** (`DOCUMENTED` **/** `INFERRED` **themes**).

## What this system teaches the atlas

**Model** **Solaris/illumos** **libc** **explicitly** **when** **contrasting** **Linux** **`glibc`**/**`musl`** **and** **BSD** **base** **libcs**.
