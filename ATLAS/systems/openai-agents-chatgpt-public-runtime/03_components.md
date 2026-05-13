---
atlas_package: system
system_slug: openai-agents-chatgpt-public-runtime
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| HTTP API gateway (conceptual) | Public entrypoint | DOCUMENTED (as “API” in docs; not internal microservice map) |
| Model inference (opaque) | Computes outputs | UNKNOWN internal; DOCUMENTED external behavior only |
| Client SDKs | Wrappers around HTTP | DOCUMENTED where official SDKs exist |

**Rule:** Do not name undocumented microservices.
