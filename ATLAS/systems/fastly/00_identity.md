---
atlas_package: system
system_slug: fastly
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# Fastly — Identity

**Kind:** Global edge cloud — CDN caching, **Compute@Edge** (V8 isolates / Wasm-class workloads per Fastly docs), and security features.

## Boundaries

- Not `cloudflare-workers` — different runtime and product surface.
- Not `amazon-cloudfront` — substitute CDN class, not identical APIs.
