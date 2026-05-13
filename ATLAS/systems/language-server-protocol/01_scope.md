---
atlas_package: system
system_slug: language-server-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- JSON-RPC message set between **client** (editor/tooling) and **server** (language intelligence) (`DOCUMENTED`, `src-lsp-spec-3-17`).  
- Capabilities negotiation, document sync, diagnostics, completion, etc. (`DOCUMENTED`).

## Out of scope

- Compiler internals not exposed via LSP.  
- Debug Adapter Protocol — see **`debug-adapter-protocol`** (separate specification).

## Versioning note

Specification versioned (e.g. 3.17); servers advertise capabilities (`DOCUMENTED`).
