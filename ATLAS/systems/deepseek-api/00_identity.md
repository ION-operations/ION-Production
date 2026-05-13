---
atlas_package: system
system_slug: deepseek-api
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# DeepSeek API — Public surface

**Kind:** Vendor **HTTP APIs** for DeepSeek models as documented — **not** internal cluster architecture.

## Boundaries

- **DOCUMENTED:** Endpoints, parameters, limits in public API docs (`src-deepseek-api-docs`).  
- **UNKNOWN:** non-public serving, safety stack internals.

## Why this system matters

- Reference **OpenAI-compatible** style API patterns where documented (`DOCUMENTED` — verify “compatible” wording in official docs).  
- Useful comparator in `comparative/ai_runtime_models.md`.

## What this system teaches the atlas

- “API-compatible” claims must be **quoted from vendor docs**, not assumed identical.
