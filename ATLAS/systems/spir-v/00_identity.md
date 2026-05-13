---
atlas_package: system
system_slug: spir-v
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# SPIR-V — Identity

**Kind:** **Binary** **intermediate representation** for **GPU** **and** **parallel** **compute** — **Khronos**-**governed**, **used** **by** **Vulkan**, **OpenCL**, and **related** **ecosystems** (`DOCUMENTED`, `src-khronos-spirv`).

**Authority:** **Khronos** **SPIR-V** **specification** **registry** (`DOCUMENTED`, `src-khronos-spirv`).

## Boundaries

- **Not** **CPU** **machine** **code** (§1 of `language_machine_and_assembly_stack.md`) — **different** **execution** **model** (`DOCUMENTED`).  
- **Not** **NVIDIA** **PTX** — **different** **vendor** **/** **representation** (`DOCUMENTED`).

## Why this system matters

- **Portable** **shader** **/** **kernel** **IR** **across** **Vendors** **when** **combined** **with** **APIs** **(e.g.** **Vulkan)** (`DOCUMENTED` ecosystem).  
- **LLVM** **tooling** **can** **emit** **/** **consume** **SPIR-V** **in** **documented** **workflows** (`DOCUMENTED`, `src-llvm-spirv`).

## What this system teaches the atlas

- How **GPU** **compilation** **pipelines** **diverge** **from** **classic** **CPU** **link** **models**.
