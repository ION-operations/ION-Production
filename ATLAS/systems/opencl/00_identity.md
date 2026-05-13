---
atlas_package: system
system_slug: opencl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# OpenCL — Identity

**Kind:** **Khronos** **open** **standard** **for** **parallel** **programming** **of** **heterogeneous** **platforms** — **C**-**based** **kernel** **model,** **platform** **/** **device** **discovery,** **and** **runtime** **APIs** (`DOCUMENTED`, `src-khronos-opencl`).

**Authority:** **Khronos** **OpenCL** **specification** **registry** **and** **reference** **pages** (`DOCUMENTED`, `src-khronos-opencl`, `src-opencl-registry`).

## Boundaries

- **Not** **CUDA** — **different** **vendor** **/** **ecosystem** **(though** **often** **co-deployed)** (`DOCUMENTED`).  
- **Not** **SPIR-V** **alone** — **OpenCL** **is** **an** **API;** **SPIR-V** **is** **an** **IR** **used** **in** **OpenCL** **tooling** **tracks** (`DOCUMENTED`).

## Why this system matters

- **Cross**-**vendor** **portability** **layer** **for** **CPUs,** **GPUs,** **FPGAs** **(where** **supported)** (`DOCUMENTED` scope).  
- **Bridges** **to** **SPIR-V** **for** **portable** **device** **code** **(modern** **spec** **lines)** (`DOCUMENTED`, Khronos).

## What this system teaches the atlas

- How **standardized** **host** **APIs** **differ** **from** **single**-**vendor** **GPU** **platforms** **like** **CUDA**.
