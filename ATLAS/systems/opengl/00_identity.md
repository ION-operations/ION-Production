---
atlas_package: system
system_slug: opengl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# OpenGL — Identity

**Kind:** **Khronos** **cross**-**vendor** **graphics** **API** **family** **for** **2D** **/** **3D** **rendering** **on** **GPUs** — **state** **machine,** **objects,** **shaders** **(historically** **GLSL**-**centric),** **and** **fixed**-**function** **to** **programmable** **pipeline** **evolution** (`DOCUMENTED`, `src-khronos-opengl`, `src-opengl-registry`).

**Authority:** **Khronos** **OpenGL** **/** **GLSL** **registry** **and** **specification** **materials** (`DOCUMENTED`, `src-opengl-registry`).

## Boundaries

- **Not** **Vulkan** — **different** **explicit** **command** **model** **(successor** **ecosystem** **often** **coexists** **with** **OpenGL** **for** **legacy** **/** **tooling)** (`DOCUMENTED` split).  
- **Not** **SPIR-V** **alone** — **OpenGL** **historically** **uses** **GLSL;** **SPIR-V** **ingest** **is** **a** **later** **extension** **track** (`DOCUMENTED`).

## Why this system matters

- **Decades** **of** **graphics** **/** **CAD** **/** **scientific** **visualization** **code** **and** **tutorials** **anchored** **to** **GL** (`DOCUMENTED` ecosystem).  
- **Bridge** **to** **SPIR-V** **in** **4.6**-**era** **spec** **for** **shader** **IR** **interoperability** (`DOCUMENTED`, extension track).

## What this system teaches the atlas

- How **long**-**lived** **APIs** **accumulate** **extensions** **and** **parallel** **shader** **paths** **(GLSL** **vs** **SPIR-V)** **without** **a** **single** **IR** **mandate**.
