---
atlas_package: system
system_slug: vscode
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Visual Studio Code — Identity

**Kind:** Cross-platform source code editor with extension host architecture, language services integration, and integrated terminal/debugger surfaces.

## Canonical definition

VS Code is an Electron-based desktop application distributing a workbench UI, a **Extension Host** process for third-party extensions, and documented extension APIs (`DOCUMENTED`, `src-vscode-repo`, `src-vscode-api`).

## Boundaries

- **Not** a full IDE for all languages out of the box — capabilities come from extensions and built-in language servers where bundled (`DOCUMENTED`).  
- **Not** an operating system kernel — host OS provides process isolation primitives.

## Why this system matters

- **Extension Host** model isolates extension code in a separate process from the UI (`DOCUMENTED`).  
- **Language Server Protocol (LSP)** ecosystem central to modern editing (`DOCUMENTED` — LSP spec not in this package).  
- **MCP client** integration connects editors to external tool servers (`DOCUMENTED` via product docs/release notes; pin precise URLs).

## What this system teaches the atlas

- How **extension platforms** create trust boundaries inside a desktop app.  
- How **protocol bridges** (LSP, MCP) decouple UI from tools.
