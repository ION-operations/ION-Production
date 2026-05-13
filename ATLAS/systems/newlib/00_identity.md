---
atlas_package: system
system_slug: newlib
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# newlib — Identity

**Kind:** **newlib** **C** **library** **for** **embedded** **systems** **and** **GCC**-**class** **cross** **toolchains** (**hosted** **and** **bare**-**metal** **targets**) (`DOCUMENTED`, `src-newlib-sourceware`).

## Boundaries

- **Not** **`glibc`**, **`musl`**, **or** **OS** **distribution** **base** **libcs** — **different** **build** **configurations** **and** **ABI** **surfaces** (`DOCUMENTED`).  
- **Not** **a** **single** **fixed** **ABI** **—** **per**-**target** **multilib** **and** **BSP** **choices** **apply** (`DOCUMENTED`).

## Why this system matters

- **Default** **embedded** **libc** **story** **for** **many** **GCC** **bare**-**metal** **and** **RTOS** **SDKs** (`DOCUMENTED`).

## What this system teaches the atlas

**Separate** **embedded** **libc** **law** **from** **desktop** **`glibc`**/**`musl`** **when** **auditing** **cross** **compile** **graphs**.
