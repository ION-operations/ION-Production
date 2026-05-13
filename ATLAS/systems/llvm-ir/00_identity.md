---
atlas_package: system
system_slug: llvm-ir
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# LLVM IR — Identity

**Kind:** **Static single-assignment (SSA)** **intermediate representation** used by the **LLVM** **compiler** **infrastructure** — **language**-like **IR** **between** **front** **ends** and **code** **generators** (`DOCUMENTED`, `src-llvm-langref`).

**Authority:** **LLVM Language Reference Manual** (evolves with LLVM releases) (`DOCUMENTED`, `src-llvm-langref`).

## Boundaries

- **Not** **machine** **code** — **abstract** **machine** with **typed** **operations** (`DOCUMENTED`).  
- **Not** **one** **source** **language** — **many** **front** **ends** **lower** **to** **LLVM** **IR** (`DOCUMENTED`).

## Why this system matters

- **De** **facto** **hub** **IR** for **Clang**/**Rustc**/**Swift**/**many** **others** (`DOCUMENTED` ecosystem pattern).  
- **Optimization** **pipeline** **(passes)** **shared** **across** **languages** (`DOCUMENTED` LLVM model).

## What this system teaches the atlas

- How **IR** **design** **enables** **shared** **middle** **ends** **without** **merging** **language** **semantics** **at** **the** **source** **level**.
