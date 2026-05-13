---
atlas_package: system
system_slug: direct3d
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Direct3D — Identity

**Kind:** **Microsoft** **graphics** **API** **family** **for** **GPU** **rendering** **and** **compute** **on** **Windows** **(and** **related** **ecosystems** **where** **supported)** — **device** **/** **command** **recording,** **pipelines,** **resources,** **and** **HLSL** **/** **DXIL** **shader** **compilation** **in** **modern** **versions** (`DOCUMENTED`, `src-ms-learn-d3d12`).

**Authority:** **Microsoft** **Learn** **documentation** **for** **Direct3D** **(e.g.** **Direct3D** **12)** (`DOCUMENTED`, `src-ms-learn-d3d12`).

## Boundaries

- **Not** **“DirectX”** **in** **full** — **DirectX** **bundles** **audio,** **input,** **and** **other** **subsystems;** **this** **package** **is** **the** **GPU** **graphics** **/** **compute** **API** **grain** (`DOCUMENTED` scope).  
- **Not** **SPIR-V** — **modern** **Direct3D** **shader** **pipelines** **use** **HLSL** **→** **DXIL** **(LLVM** **based)** **on** **documented** **paths** (`DOCUMENTED` split).

## Why this system matters

- **Default** **GPU** **API** **culture** **for** **many** **Windows** **games** **and** **applications** (`DOCUMENTED` ecosystem).  
- **Pairs** **with** **Vulkan** **/** **Metal** **/** **OpenGL** **as** **the** **major** **platform** **GPU** **API** **set** **in** **ATLAS.**

## What this system teaches the atlas

- **OS**-**vendor** **graphics** **stacks** **remain** **central** **even** **when** **Khronos** **APIs** **are** **cross**-**platform.**
