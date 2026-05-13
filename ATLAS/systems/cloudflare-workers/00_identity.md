---
atlas_package: system
system_slug: cloudflare-workers
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Cloudflare Workers — Identity

**Kind:** Serverless JavaScript/WebAssembly execution at Cloudflare edge PoPs (`DOCUMENTED`, Cloudflare Workers docs).

## Boundaries

- Not a full Linux VM — V8/isolates model per product docs.
- Not the `webassembly` spec itself — may host Wasm modules where documented for the Workers runtime.
