---
atlas_package: system
system_slug: dietlibc
schema_version: "1.0"
last_reviewed: "2026-04-15"
evidence_grade: B
---

# dietlibc — Identity

**Kind:** **Minimal** **C** **library** **for** **Linux** **intended** **for** **static** **linking** **and** **very** **small** **footprints** (`DOCUMENTED`, `src-dietlibc-fefe`).

## Boundaries

- **Not** **`glibc`**, **`musl`**, **`uclibc`** — **different** **feature** **completeness** **and** **ABI** (`INFERRED`).  
- **Not** **bare-metal** **without** **Linux** — **contrast** **`newlib`** (`DOCUMENTED` **boundary**).  
- **Not** **Wasm** — **`wasi-libc`** (`DOCUMENTED` **boundary**).

## Why this system matters

- **Demonstrates** **how** **small** **a** **Linux** **hosted** **libc** **surface** **can** **be** **for** **specialized** **static** **builds** (`DOCUMENTED` **themes**).

## What this system teaches the atlas

**Separate** **“smallest** **Linux** **libc”** **stories** (**dietlibc**) **from** **general-purpose** **`musl`**/**`uclibc`**/**`glibc`**.
