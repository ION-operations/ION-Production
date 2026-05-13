---
atlas_package: system
system_slug: debug-adapter-protocol
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Debug Adapter Protocol (DAP)

**Kind:** **JSON-RPC** protocol standardizing how a **debug adapter** (runtime/debugger backend) exchanges **launch**, **breakpoints**, **threads**, **stack frames**, and **variables** with a **client** (typically an editor or IDE) (`DOCUMENTED`, `src-dap-spec`).

## Boundaries

- **Not** LSP — LSP covers **language intelligence**; DAP covers **debug sessions** (`DOCUMENTED` scope split; see `language-server-protocol`).  
- **Not** MCP — MCP covers **tool/resource/prompt** surfaces for **agent hosts**; DAP covers **debugger control** (`INFERRED` comparative distinction).

## Why this system matters

- Same **host ↔ server** decoupling pattern as LSP, applied to **debugging** (`DOCUMENTED`).  
- Keeps **debug UX** portable across languages when adapters implement the contract (`DOCUMENTED` intent of spec).

## What this system teaches the atlas

- **Triple split** in modern IDE stacks: **LSP** (language), **DAP** (debug), **MCP** (agent tools) — three packages, three boundaries.
