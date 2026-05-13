---
atlas_package: system
system_slug: webassembly
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# WebAssembly — Identity

**Kind:** **Portable** **binary** **instruction** **format** — **stack** **machine** **semantics**, **module** **model**, **and** **safety** **constraints** **designed** **for** **embedding** **in** **hosts** **(browsers,** **runtimes,** **edge)** (`DOCUMENTED`, `src-w3c-wasm-core2`).

**Authority:** **W3C** **WebAssembly** **Core** **specification** **(Recommendation** **track)** (`DOCUMENTED`, `src-w3c-wasm-core2`).

## Boundaries

- **Not** **JavaScript** — **Wasm** **is** **a** **distinct** **language** **with** **its** **own** **encoding** (`DOCUMENTED`).  
- **Not** **identical** **to** **JVM** **/** **CIL** — **linear** **memory** **model** **and** **capability** **discipline** **differ** (`DOCUMENTED` comparative).

## Why this system matters

- **Sandboxed** **near-native** **code** **in** **cross**-**vendor** **environments** (`DOCUMENTED` ecosystem).  
- **Toolchains** **often** **lower** **via** **LLVM** **IR** **to** **Wasm** (`INFERRED` common path).

## What this system teaches the atlas

- How **capability**-**based** **host** **embedding** **differs** **from** **classpath** **/** **assembly** **loading** **models**.
