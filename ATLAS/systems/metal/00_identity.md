---
atlas_package: system
system_slug: metal
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Metal — Identity

**Kind:** **Apple** **low**-**overhead** **GPU** **API** **for** **graphics** **and** **compute** **on** **Apple** **silicon** **and** **supported** **GPUs** — **command** **queues,** **resources,** **pipelines,** **and** **Metal** **Shading** **Language** **(MSL)** (`DOCUMENTED`, `src-apple-metal`).

**Authority:** **Apple** **developer** **documentation** **for** **Metal** **and** **MSL** (`DOCUMENTED`, `src-apple-metal`).

## Boundaries

- **Not** **SPIR-V** **as** **the** **native** **shader** **submission** **IR** — **Metal** **uses** **MSL** **and** **Apple** **IR** **(AIR)** **internally** **in** **vendor** **tooling** (`DOCUMENTED` split; **MoltenVK** **/** **portability** **layers** **map** **Vulkan** **/** **SPIR-V** **elsewhere`).  
- **Not** **Vulkan** — **different** **API** **and** **platform** **scope** (`DOCUMENTED`).

## Why this system matters

- **Primary** **GPU** **path** **on** **macOS,** **iOS,** **iPadOS,** **and** **related** **Apple** **platforms** (`DOCUMENTED` ecosystem).  
- **Illustrates** **vendor**-**controlled** **GPU** **stack** **orthogonal** **to** **Khronos** **SPIR-V** **defaults.**

## What this system teaches the atlas

- **Platform**-**bound** **GPU** **APIs** **remain** **first**-**class** **even** **when** **cross**-**vendor** **standards** **exist.**
