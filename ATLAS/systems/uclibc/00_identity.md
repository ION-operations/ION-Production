---
atlas_package: system
system_slug: uclibc
schema_version: "1.0"
last_reviewed: "2026-04-14"
evidence_grade: B
---

# uClibc / uClibc-ng — Identity

**Kind:** **Small** **C** **library** **for** **Linux** **userland** **targets** **(embedded** **and** **resource-constrained** **systems)** — **actively** **maintained** **as** **uClibc-ng** (`DOCUMENTED`, `src-uclibc-ng`).

## Boundaries

- **Not** **`glibc`** **or** **`musl`** — **different** **ABI,** **feature** **set,** **and** **packaging** (`DOCUMENTED`).  
- **Not** **bare-metal** **without** **Linux** — **contrast** **`newlib`** **on** **non-Linux** **targets** (`INFERRED`).  
- **Not** **Wasm** — **`wasi-libc`** **covers** **that** **universe** (`DOCUMENTED` **boundary**).

## Why this system matters

- **Common** **libc** **choice** **in** **Buildroot,** **OpenWrt-class** **stacks,** **and** **embedded** **Linux** **images** (`DOCUMENTED` **/** `OBSERVED`).

## What this system teaches the atlas

**Separate** **embedded** **Linux** **libc** **(uClibc)** **from** **desktop** **`glibc`**, **from** **`musl`**, **and** **from** **non-Linux** **embedded** **`newlib`**.
