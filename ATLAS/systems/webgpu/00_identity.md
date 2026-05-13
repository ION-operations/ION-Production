---
atlas_package: system
system_slug: webgpu
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# WebGPU — Identity

**Kind:** **W3C** **browser** **/** **web** **platform** **GPU** **API** **for** **graphics** **and** **compute** **—** **adapters,** **devices,** **queues,** **pipelines,** **and** **resources** **with** **WGSL** **as** **the** **shader** **language** (`DOCUMENTED`, `src-w3c-webgpu`, `src-w3c-wgsl`).

**Authority:** **W3C** **WebGPU** **and** **WGSL** **specifications** (`DOCUMENTED`, `src-w3c-webgpu`, `src-w3c-wgsl`).

## Boundaries

- **Not** **Vulkan** **/** **Metal** **/** **Direct3D** **directly** — **those** **are** **native** **APIs;** **user** **agents** **implement** **WebGPU** **on** **top** **of** **them** (`DOCUMENTED` layering).  
- **Not** **WebGL** — **different** **API** **model** **(retained** **mode** **OpenGL** **ES** **in** **browsers)** (`DOCUMENTED`).

## Why this system matters

- **Modern** **web** **GPU** **path** **for** **games,** **ML** **inference** **UI,** **and** **visualization** **without** **plugins** (`DOCUMENTED` ecosystem).  
- **Clear** **pairing** **with** **`webassembly`** **for** **engine** **stacks** **that** **ship** **Wasm** **+** **GPU.**

## What this system teaches the atlas

- **How** **a** **sandboxed** **web** **API** **maps** **onto** **native** **GPU** **drivers** **through** **implementation**-**defined** **backends.**
