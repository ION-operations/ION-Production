---
atlas_package: system
system_slug: model-context-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Model Context Protocol (MCP)

**Kind:** Open **application-layer protocol** for connecting AI hosts (applications) to external **tool** and **context** servers using JSON-RPC messages over declared transports.

## Canonical definition

MCP specifies initialization, capability negotiation, resource/prompt/tool discovery, and tool invocation semantics (`DOCUMENTED`, `src-mcp-spec`).

## Boundaries

- **Not** a model inference protocol — does not define tensor serving or weights (`DOCUMENTED` scope limitation).  
- **Not** an OS kernel interface — trust boundaries are **host process ↔ MCP server process** (`DOCUMENTED` security model section of spec).

## Why this system matters

- Standardizes **tooling plug-in** edges for LLM hosts similarly to how LSP standardized language services (`DOCUMENTED` analogy is comparative, not historical claim of lineage).  
- Makes **explicit** the security assumption that the host vouches for server process execution (`DOCUMENTED`).

## What this system teaches the atlas

- How to catalog a **protocol** alongside **kernels** without confusing abstraction layers.  
- How **JSON-RPC + capabilities** patterns recur in control-plane adjacency.
