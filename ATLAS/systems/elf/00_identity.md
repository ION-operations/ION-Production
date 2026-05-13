---
atlas_package: system
system_slug: elf
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Executable and Linking Format (ELF)

**Kind:** **Object file** and **executable** **container format** — ELF header, program headers, sections, symbols, and relocations — used widely on Unix-class systems and specified in the classic **TIS** / **System V gABI** references (`DOCUMENTED`, `src-tis-elf`, `src-sysv-gabi`).

## Boundaries

- **Not** the **CPU ISA** — machine code inside `.text` is interpreted per **ISA** / **psABI** (`DOCUMENTED` separation).  
- **Not** **DWARF** — debug info is commonly **carried in ELF sections**, but the **DWARF encoding** is its own standard (`DOCUMENTED`; see `dwarf`).  
- **Not** **UKI outer shell** — a UKI is often a **PE** wrapper around an **ELF** Linux kernel image (`DOCUMENTED` in UKI docs; see `unified-kernel-image`).

## Why this system matters

- **Link/load contract** between compilers, linkers, and the kernel loader (`DOCUMENTED`).  
- Shared object (`ET_DYN`), relocations, and dynamic linking metadata are **field reality** for servers and desktops (`DOCUMENTED`).

## What this system teaches the atlas

- Keep **container format** (ELF), **debug encoding** (DWARF), **IR** (`llvm-ir`), and **ISA** (`riscv-isa`, …) as **separate packages** with explicit edges.
