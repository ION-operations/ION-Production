---
atlas_package: system
system_slug: nvidia-ptx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# NVIDIA PTX — Identity

**Kind:** **Parallel** **Thread** **Execution** **(PTX)** **virtual** **ISA** — **NVIDIA**-**defined** **textual** **/** **assembly**-**level** **IR** **consumed** **by** **CUDA** **toolchains** **and** **drivers** (`DOCUMENTED`, `src-nvidia-ptx`).

**Authority:** **NVIDIA** **CUDA** **documentation** **—** **Parallel** **Thread** **Execution** (`DOCUMENTED`, `src-nvidia-ptx`).

## Boundaries

- **Not** **SPIR-V** — **different** **vendor** **and** **portable** **GPU** **IR** **model** (`DOCUMENTED`).  
- **Not** **final** **SASS** **machine** **code** — **PTX** **is** **typically** **further** **compiled** **by** **the** **driver** (`DOCUMENTED`, `src-nvidia-ptx`).

## Why this system matters

- **Dominant** **CUDA** **compilation** **target** **before** **device**-**specific** **machine** **ISA** (`DOCUMENTED` ecosystem).  
- **LLVM** **NVPTX** **backend** **emits** **PTX** **from** **LLVM** **IR** (`DOCUMENTED`, `src-llvm-nvptx`).

## What this system teaches the atlas

- How **GPU** **vendors** **expose** **a** **stable** **virtual** **ISA** **distinct** **from** **CPU** **ABIs**.
