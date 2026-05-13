---
atlas_package: system
system_slug: amd-rocm
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# AMD ROCm — Identity

**Kind:** **Open** **source** **GPU** **compute** **stack** **for** **AMD** **GPUs** — **HIP** **(C++** **GPU** **kernel** **model),** **drivers,** **math** **/** **ML** **libraries,** **and** **tooling** **(ROCm** **releases)** (`DOCUMENTED`, `src-rocm-docs`).

**Authority:** **AMD** **ROCm** **documentation** **and** **release** **notes** (`DOCUMENTED`, `src-rocm-docs`, `src-amd-rocm-product`).

## Boundaries

- **Not** **SPIR-V** **/** **Vulkan** **alone** — **ROCm** **targets** **compute** **(HIP,** **OpenCL** **via** **stack)** (`DOCUMENTED` scope).  
- **Not** **a** **single** **ISA** **manual** **for** **RDNA/CDNA** **machine** **encoding** — **that** **layer** **remains** **vendor** **/** **partially** **public** (`DOCUMENTED` gap).

## Why this system matters

- **Open** / **Linux-first** **symmetry** **with** **proprietary** **CUDA** **ecosystems** **for** **GPU** **HPC** **and** **ML** (`DOCUMENTED` positioning).  
- **LLVM**/**Clang**-**centric** **tooling** **paths** **for** **GPU** **code** **generation** (`DOCUMENTED`, LLVM AMDGPU target).

## What this system teaches the atlas

- How **vendor** **stacks** **bundle** **IR,** **runtimes,** **and** **libraries** **beyond** **a** **single** **virtual** **ISA** **package** **(cf.** **`nvidia-ptx`)**.
