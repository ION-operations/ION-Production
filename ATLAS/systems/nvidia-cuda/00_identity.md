---
atlas_package: system
system_slug: nvidia-cuda
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# NVIDIA CUDA — Identity

**Kind:** **CUDA** **platform** — **toolkit** **(nvcc,** **libraries),** **runtime,** **driver** **interface,** **and** **GPU** **compute** **ecosystem** **for** **NVIDIA** **GPUs** (`DOCUMENTED`, `src-cuda-docs`).

**Authority:** **NVIDIA** **CUDA** **documentation** **and** **release** **notes** (`DOCUMENTED`, `src-cuda-docs`, `src-cuda-toolkit`).

## Boundaries

- **Not** **PTX** **alone** — **that** **virtual** **ISA** **is** **`nvidia-ptx`** (`DOCUMENTED` split).  
- **Not** **SPIR-V** **/** **Vulkan** **—** **different** **primary** **graphics** **/** **Khronos** **pipelines** (`DOCUMENTED`).

## Why this system matters

- **Dominant** **GPU** **compute** **stack** **for** **ML** **and** **HPC** **on** **NVIDIA** **hardware** (`DOCUMENTED` ecosystem).  
- **Pairs** **with** **`nvidia-ptx`** **(IR)** **and** **driver** **lowering** **to** **machine** **ISA** (`DOCUMENTED` toolchain shape).

## What this system teaches the atlas

- How **vendor** **platforms** **bundle** **languages,** **math** **libs,** **and** **runtimes** **beyond** **a** **single** **ISA** **document**.
