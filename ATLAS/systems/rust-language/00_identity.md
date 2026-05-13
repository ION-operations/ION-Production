---
atlas_package: system
system_slug: rust-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Rust — Identity

**Kind:** **Multi-paradigm** systems programming language emphasizing **memory safety** without GC (ownership + borrow checker), **concurrency** without data races (type-system discipline), **zero-cost abstractions** (`DOCUMENTED`, `src-wiki-rust`, `src-rust-reference`).

**Editions:** **2015**, **2018**, **2021**, **2024** — evolution without breaking stability guarantees (`DOCUMENTED`, `src-rust-reference`).

## Boundaries

- **Not** C++ — distinct language and ABI culture (`DOCUMENTED`).  
- **Compiler** (**rustc**) / **LLVM** backend — implementation separate from **language** spec (`DOCUMENTED`).

## Why this system matters

- **Linux kernel** **Rust** modules (ongoing integration) — OS-class relevance (`DOCUMENTED`, `src-linux-rust-for-linux`).  
- **Cargo** ecosystem as **build + deps** norm (`DOCUMENTED`, `src-wiki-rust`).

## What this system teaches the atlas

- Tradeoff between **borrow checker** ergonomics and **C**-style freedom (`DOCUMENTED` discourse; not marketing).
