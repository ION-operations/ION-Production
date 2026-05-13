---
atlas_package: system
system_slug: debug-adapter-protocol
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- Normative **JSON-RPC** messages for **debug adapters** and **clients** (`DOCUMENTED`, `src-dap-spec`).  
- Lifecycle: **initialize**, **launch** / **attach**, **threads**, **stackTrace**, **scopes**, **variables**, **continue** / **next** / **stepIn** / **stepOut**, etc. (`DOCUMENTED`).

## Out of scope

- DWARF / symbol format on disk — see **`dwarf`** (different layer).  
- Language-specific compiler diagnostics — **LSP** unless surfaced only through debug events.

## Versioning note

Specification is versioned on the DAP site; capabilities are negotiated in the protocol (`DOCUMENTED`).
