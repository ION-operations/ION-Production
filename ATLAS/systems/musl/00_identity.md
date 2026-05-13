---
atlas_package: system
system_slug: musl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# musl libc — Identity

**Kind:** **Lightweight** **ISO C** and **POSIX** **libc** implementation for **Linux**, designed for **static** linking, **small** footprint, and **correctness**-oriented behavior (`DOCUMENTED`, `src-musl-site`, `src-musl-wiki`).

## Boundaries

- **Not** **`glibc`** — different **ABI**, **feature** set, and **dynamic** **linking** culture (`DOCUMENTED` comparative).  
- **Not** **`linux-kernel`** — **syscall** **stubs** sit in **userland** (`DOCUMENTED`).  
- **Not** **Alpine Linux** the **distribution** — **musl** is the **libc**; **Alpine** is not seeded as a package here (`INFERRED` ecosystem note).

## Why this system matters

- **Dominant** **libc** on **Alpine**-based **container** images; **size** and **linking** model differ from **glibc** (`DOCUMENTED` / `INFERRED` field pattern).  
- **Substitution** point for **security**/**supply-chain** discussions (**musl** vs **glibc** **CVE** surface) (`INFERRED`).

## What this system teaches the atlas

- Pair **`musl`** with **`glibc`** under **`c-runtime`** for **“which libc is in this image?”** audits.
