---
atlas_package: system
system_slug: gnu-gdb
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# GNU Debugger (GDB)

**Kind:** **GNU** **source-level** and **machine-level** **debugger** — controls **inferior** processes, reads **symbols** and **debug info** (typically **DWARF** in **ELF**), supports **breakpoints**, **single-step**, **backtraces**, **remote** targets, and **GDB/MI** machine interface (`DOCUMENTED`, `src-gdb-doc`).

## Boundaries

- **Not** **DWARF** — GDB **consumes** DWARF; the format spec is **`dwarf`**.  
- **Not** **DAP** — **Debug Adapter Protocol** is a separate JSON-RPC contract; many IDEs reach **GDB** via **adapters** (`INFERRED`; see `debug-adapter-protocol`).  
- **Not** a **compiler** — **`gnu-gcc`** / **`clang`** produce debuggable objects (`DOCUMENTED` split).

## Why this system matters

- **De facto** CLI debugger on **GNU/Linux** and **embedded** cross-debug (`DOCUMENTED`).  
- **Remote** / **gdbserver** pattern for target debugging (`DOCUMENTED`).

## What this system teaches the atlas

- Separate **debugger** (`gnu-gdb`), **debug encoding** (`dwarf`), **container** (`elf`), and **IDE protocol** (`debug-adapter-protocol`).
