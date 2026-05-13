---
atlas_package: system
system_slug: nvidia-cuda
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (platform)

## Compilation path

**CUDA** **C++** **/** **Fortran** **→** **PTX** **/** **fatbin** **→** **driver** **JIT** (`DOCUMENTED`, `src-cuda-docs`).

## Libraries

**cuBLAS,** **cuDNN,** **NCCL,** **…** — **layered** **on** **CUDA** **runtime** (`DOCUMENTED` ecosystem).
