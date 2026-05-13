---
atlas_package: system
system_slug: language-server-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Language Server Protocol (LSP)

**Kind:** **JSON-RPC** protocol standardizing how editors and IDEs communicate with **language servers** for features like completion, diagnostics, and navigation (`DOCUMENTED`, `src-lsp-spec-3-17`).

## Boundaries

- **Not** MCP — LSP addresses **language services**; MCP addresses **tool/context servers** for agents (`INFERRED` comparative distinction; do not equate transports).  
- **Not** a runtime for LLM inference.

## Why this system matters

- De facto **decoupling** of editor UX from language implementation (`DOCUMENTED`).  
- Structural analog to MCP for a different class of capabilities (`INFERRED` pattern only).

## What this system teaches the atlas

- Protocol layering: **LSP (language)** vs **MCP (tools)** vs **DAP (debugging)** — keep packages separate (`debug-adapter-protocol`).
