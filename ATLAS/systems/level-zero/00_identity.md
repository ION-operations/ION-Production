---
atlas_package: system
system_slug: level-zero
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Level Zero — Identity

**Kind:** **oneAPI** **low**-**level** **GPU** **/** **accelerator** **API** **for** **devices,** **queues,** **memory,** **and** **kernels** — **closer** **to** **driver** **surfaces** **than** **SYCL** **or** **OpenCL** (`DOCUMENTED`, `src-lz-spec`, `src-lz-github`).

**Authority:** **Level** **Zero** **specification** **(GitHub** **Pages)** **and** **upstream** **repository** (`DOCUMENTED`, `src-lz-spec`).

## Boundaries

- **Not** **SYCL** — **Level** **Zero** **is** **a** **C** **API** **/** **ABI** **grain;** **SYCL** **compilers** **may** **lower** **to** **it** (`DOCUMENTED` split).  
- **Not** **Vulkan** — **different** **problem** **space** **(though** **both** **can** **target** **GPUs)** (`DOCUMENTED`).

## Why this system matters

- **Common** **backend** **for** **Intel** **GPU** **tooling** **and** **SYCL** **runtimes** **on** **supported** **stacks** (`DOCUMENTED` ecosystem).  
- **Useful** **when** **reasoning** **about** **“what** **the** **runtime** **actually** **calls.”**

## What this system teaches the atlas

- **Explicit** **layering:** **language** **(SYCL)** **→** **low**-**level** **runtime** **(Level** **Zero)** **→** **driver.**
