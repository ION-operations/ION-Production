---
atlas_package: system
system_slug: gemini-api
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Google Gemini API — Public surface

**Kind:** Vendor **HTTP/gRPC-class APIs** and SDKs for Gemini models as documented on Google AI / Vertex surfaces — **not** internal Google serving topology.

## Boundaries

- **DOCUMENTED:** API resources, auth modes, quotas as published (`src-gemini-api-docs`).  
- **UNKNOWN:** datacenter placement, TPU topology, proprietary safety stacks beyond public statements.

## Why this system matters

- Major **multimodal** API surface (text/audio/image/video where documented) (`DOCUMENTED`).  
- Often compared to OpenAI APIs for agent design (`INFERRED` usage pattern).

## What this system teaches the atlas

- Same evidence rules as `openai-agents-chatgpt-public-runtime`: **contract-first**.
