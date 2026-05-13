---
atlas_package: system
system_slug: vscode
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

## Structural overview

- **Main process (Electron)** hosts UI and system integration (`DOCUMENTED` pattern in Electron apps; VS Code specifics in wiki/docs).  
- **Extension Host** process runs extensions with RPC to main (`DOCUMENTED`, `src-vscode-api`).  
- **Language servers** run as separate processes communicating via LSP (`DOCUMENTED` pattern).

## Control vs data plane

- **Control:** settings, commands, keybindings, extension activation events (`DOCUMENTED`).  
- **Data plane:** file buffers, search, terminal I/O — mediated by workbench services (`DOCUMENTED` at API level).

## UNKNOWN

- Exact IPC message schemas internal to Electron layer without reading source — mark **INFERRED** if derived from source later.
