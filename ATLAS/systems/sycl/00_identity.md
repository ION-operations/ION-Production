---
atlas_package: system
system_slug: sycl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# SYCL — Identity

**Kind:** **Khronos** **open** **standard** **for** **single**-**source** **C++** **heterogeneous** **programming** — **queues,** **buffers,** **accessors,** **and** **kernel** **dispatch** **across** **CPUs** **and** **accelerators** (`DOCUMENTED`, `src-khronos-sycl`, `src-sycl-registry`).

**Authority:** **Khronos** **SYCL** **specification** **registry** (`DOCUMENTED`, `src-sycl-registry`).

## Boundaries

- **Not** **OpenCL** **host** **API** **directly** — **SYCL** **is** **a** **C++** **embedding** **/** **programming** **model;** **implementations** **may** **lower** **to** **OpenCL,** **Level** **Zero,** **CUDA** **interop,** **etc.** (`DOCUMENTED` split).  
- **Not** **CUDA** — **different** **vendor** **/** **language** **surface** (`DOCUMENTED`).

## Why this system matters

- **Standardized** **C++** **approach** **to** **portable** **accelerator** **code** **alongside** **OpenCL** **/** **GPU** **ecosystems** (`DOCUMENTED` ecosystem).  
- **Common** **LLVM**-**based** **compiler** **implementations** **(Intel** **oneAPI** **DPC++,** **AdaptiveCpp,** **…)** (`DOCUMENTED` practice).

## What this system teaches the atlas

- **How** **a** **language** **embedding** **layer** **relates** **to** **lower**-**level** **runtime** **APIs** **without** **replacing** **them.**
