---
atlas_package: system
system_slug: liburing
schema_version: "1.0"
last_reviewed: "2026-04-17"
evidence_grade: B
---

# liburing — Identity

**Kind:** **Reference** **userspace** **C** **library** **for** **Linux** **io_uring** **(helpers** **around** **the** **io_uring** **uAPI)** (`DOCUMENTED`, `src-liburing-github`, `src-io-uring-kernel-docs`).

## Boundaries

- **Not** **the** **kernel** **io_uring** **implementation** **itself** — **see** **`io-uring`**.  
- **Not** **a** **network** **or** **storage** **protocol** — **it** **is** **a** **local** **API** **wrapper** **library**.

## Why this system matters

- **Mirrors** **the** **`ebpf`**/**`libbpf`** **split** **for** **another** **major** **Linux** **kernel** **uAPI** **family**.

## What this system teaches the atlas

**Do** **not** **merge** **`io-uring`** **(kernel** **uAPI)** **with** **`liburing`** **(userspace** **library)**.
