---
atlas_package: system
system_slug: wasm-component-model
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# WebAssembly Component Model — Identity

**Kind:** **Typed** **composition** **model** **for** **WebAssembly** — **interfaces,** **packages,** **and** **linking** **rules** **that** **sit** **above** **core** **modules** (`DOCUMENTED`, `src-component-model-ba`).

**Authority:** **Bytecode** **Alliance** **/** **WebAssembly** **community** **specifications** **(WIT,** **packages,** **worlds)** (`DOCUMENTED`, `src-component-model-ba`, `src-wasm-cm-github`).

## Boundaries

- **Not** **core** **Wasm** **opcode** **semantics** — **builds** **on** **modules** (`DOCUMENTED`).  
- **Not** **identical** **to** **WASI** — **WASI** **defines** **system** **imports;** **components** **define** **how** **interfaces** **compose** (`DOCUMENTED`).

## Why this system matters

- **Interop** **between** **languages** **compiled** **to** **Wasm** **(Rust,** **C,** **…)** **with** **typed** **contracts** (`DOCUMENTED` ecosystem).  
- **Foundation** **for** **WASI** **worlds** **and** **tooling** **(e.g.** **wit-bindgen)** (`DOCUMENTED` practice).

## What this system teaches the atlas

- How **interface** **types** **and** **packages** **change** **linking** **compared** **to** **plain** **Wasm** **modules**.
