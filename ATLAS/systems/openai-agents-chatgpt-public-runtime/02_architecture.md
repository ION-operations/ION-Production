---
atlas_package: system
system_slug: openai-agents-chatgpt-public-runtime
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

## Structural overview (public only)

- **Client → HTTPS API** to vendor endpoints (`DOCUMENTED`).  
- **State:** conversations/threads or stateless request/response depending on API product area (`DOCUMENTED` per API family).  
- **Tool execution:** model may emit tool calls; **client or hosted executor** responsibilities differ by product — follow exact API doc (`DOCUMENTED`).

## Internal topology

**UNKNOWN** — not asserted in this package.

## Control vs data plane (public contract)

- **Control:** account/org management, key issuance (vendor consoles — `DOCUMENTED` at UX/doc level).  
- **Data plane:** token streams, uploaded files where API permits (`DOCUMENTED`).
