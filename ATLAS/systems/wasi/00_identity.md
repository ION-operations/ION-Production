---
atlas_package: system
system_slug: wasi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# WASI — Identity

**Kind:** **WebAssembly** **System** **Interface** — **modular** **import** **APIs** **for** **capabilities** **such** **as** **files,** **clocks,** **randomness,** **and** **sockets** **(per** **snapshot** / **phased** **specs)** (`DOCUMENTED`, `src-wasi-dev`).

**Authority:** **WASI** **specifications** **and** **proposals** **published** **through** **the** **WebAssembly** / **WASI** **community** **process** (`DOCUMENTED`, `src-wasi-dev`, `src-wasi-github`).

## Boundaries

- **Not** **core** **WebAssembly** — **WASI** **extends** **hosts** **with** **importable** **functions** (`DOCUMENTED`).  
- **Not** **a** **single** **frozen** **POSIX** — **API** **surfaces** **evolve** **by** **snapshot** (`DOCUMENTED`).

## Why this system matters

- **Portable** **server** **/** **CLI** **Wasm** **without** **browser** **APIs** (`DOCUMENTED` ecosystem).  
- **Security** **through** **capability** **imports** **rather** **than** **ambient** **authority** (`DOCUMENTED` model).

## What this system teaches the atlas

- How **OS-like** **surfaces** **attach** **to** **sandboxed** **modules** **via** **imports**.
