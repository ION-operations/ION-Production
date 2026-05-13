---
atlas_package: system
system_slug: vulkan
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Vulkan — Identity

**Kind:** **Khronos** **explicit** **GPU** **API** **for** **high-efficiency** **access** **to** **graphics** **and** **compute** **on** **modern** **GPUs** — **objects,** **queues,** **pipelines,** **synchronization,** **and** **memory** **model** (`DOCUMENTED`, `src-vulkan-org`).

**Authority:** **Khronos** **Vulkan** **specification** **registry** **and** **reference** **materials** (`DOCUMENTED`, `src-vulkan-registry`, `src-vulkan-org`).

## Boundaries

- **Not** **SPIR-V** — **Vulkan** **consumes** **SPIR-V** **for** **shader** **modules** (`DOCUMENTED` split).  
- **Not** **OpenCL** — **different** **programming** **model** **(though** **both** **can** **target** **GPUs)** (`DOCUMENTED`).

## Why this system matters

- **Cross**-**vendor** **graphics** **/** **compute** **API** **on** **desktop** **and** **mobile** (`DOCUMENTED` ecosystem).  
- **Explicit** **synchronization** **and** **multi**-**threaded** **command** **recording** **culture** (`DOCUMENTED` design).

## What this system teaches the atlas

- How **API** **layers** **compose** **with** **IR** **packages** **(SPIR-V)** **without** **merging** **them**.
