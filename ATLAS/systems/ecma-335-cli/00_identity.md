---
atlas_package: system
system_slug: ecma-335-cli
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# ECMA-335 CLI — Identity

**Kind:** **Common Language Infrastructure** (**CLI**) — **virtual** **execution** **system** **for** **Common** **Intermediate** **Language** (**CIL**) **bytecode**, **assemblies**, **metadata**, **and** **runtime** **services** (`DOCUMENTED`, `src-ecma-335`).

**Authority:** **ECMA-335** **standard**; **.NET** **implements** **CLR** **as** **a** **major** **conforming** **implementation** (`DOCUMENTED`, `src-ecma-335`, `src-ms-clr`).

## Boundaries

- **Not** **C#** **the** **language** **alone** — **C#** **compiles** **to** **CIL**, **but** **CLI** **defines** **the** **runtime** **and** **type** **system** **intersection** (`DOCUMENTED`).  
- **Not** **identical** **to** **JVM** **bytecode** — **different** **verification**, **metadata**, **and** **interop** **model** (`DOCUMENTED`).

## Why this system matters

- **Multi-language** **managed** **stack** **(C#,** **F#,** **VB.NET,** **…)** **on** **shared** **runtime** **assumptions** (`DOCUMENTED` ecosystem).  
- **Contrast** **with** **JVM** **for** **comparative** **OS** **and** **tooling** **questions** (`DOCUMENTED` comparative).

## What this system teaches the atlas

- How **standardized** **portable** **IL** **+** **metadata** **enable** **cross-language** **libraries**.
