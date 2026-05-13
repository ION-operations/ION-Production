---
atlas_package: system
system_slug: lldb
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# LLDB

**Kind:** **LLVM** **debugger** — **lldb** CLI and **SB API** (Scripting Bridge) for controlling inferiors, reading **DWARF** (and other debug info) in **ELF**/Mach-O/COFF targets depending on platform, with tight **Clang** / **LLVM** integration (`DOCUMENTED`, `src-lldb-home`, `src-lldb-use`).

## Boundaries

- **Not** **GDB** — different engine and command set (`DOCUMENTED` comparative; see `gnu-gdb`).  
- **Not** **DWARF** — consumes debug info; format is **`dwarf`**.  
- **Not** **DAP** wire format — IDEs may use **adapters**; LLDB also exposes **lldb-dap** / adapter patterns (`DOCUMENTED` / `INFERRED`; see `debug-adapter-protocol`).

## Why this system matters

- Default debug experience in **Xcode** / **Swift** / **Clang**-heavy stacks (`DOCUMENTED` ecosystem).  
- **Scriptability** via Python SB API (`DOCUMENTED`).

## What this system teaches the atlas

- Two major **open-source** debugger lineages on Unix-class systems: **`gnu-gdb`** vs **`lldb`** — keep both packages and mark **`competes_with`** where appropriate.
