---
atlas_package: system
system_slug: dwarf
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# DWARF — Identity

**Kind:** **Debugging** **information** **format** — **describes** **mapping** **between** **object** **code** **and** **source**-**level** **names**, **types**, **and** **line** **tables** (`DOCUMENTED`, `src-dwarfstd-home`).

**Authority:** **DWARF** **Standards** **Committee** — **published** **standards** **(DWARF** **2** … **5** …) (`DOCUMENTED`, `src-dwarfstd-home`).

## Boundaries

- **Not** **executable** **by** **itself** — **metadata** **carried** **in** **ELF**/Mach-O/PE **objects** (`DOCUMENTED`).  
- **Not** **the** **same** **as** **core** **file** **formats** — **orthogonal** **to** **ABI** **calling** **conventions** (`DOCUMENTED` scope).

## Why this system matters

- **Universal** **debug** **interchange** **for** **C**, **C++**, **Rust**, **Ada**, **many** **compilers** (`DOCUMENTED` ecosystem).  
- **Enables** **symbolication**, **breakpoints**, **stack** **unwinding** **metadata** (`DOCUMENTED` practice).

## What this system teaches the atlas

- How **debug** **metadata** **is** **a** **first-class** **artifact** **alongside** **machine** **code**.
