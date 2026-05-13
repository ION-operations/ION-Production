---
atlas_package: system
system_slug: gnu-binutils
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# GNU Binutils

**Kind:** **GNU** collection of **binary utilities** — assembler (**as**), linker (**ld**), archiver (**ar**), object copier (**objcopy**), object dumper (**objdump**), ELF inspector (**readelf**), strip, nm, strings, addr2line, c++filt, etc. — for producing and inspecting **object files** and **executables** (`DOCUMENTED`, `src-binutils-docs`).

## Boundaries

- **Not** the **ELF specification** — Binutils **implements** consumers/producers of ELF (`DOCUMENTED`; see `elf`).  
- **Not** **GCC** itself — the compiler is **`gnu-gcc`**; Binutils **pairs** with GCC in classic GNU flows (`DOCUMENTED`).  
- **Not** **LLVM lld** — see **`llvm-lld`**; LLVM also ships **llvm-objdump** and related tools (`INFERRED` substitution class).

## Why this system matters

- Default **link/load pipeline** on many **Linux** distributions and **embedded** cross-compile flows (`DOCUMENTED`).  
- **Inspection** tools (`readelf`, `objdump`) are the operational interface to **ELF** + **DWARF** on disk (`DOCUMENTED`).

## What this system teaches the atlas

- Separate **format** (`elf`), **debug encoding** (`dwarf`), **IR** (`llvm-ir`), and **toolchain** (`gnu-binutils`) packages — then draw edges, do not merge.
