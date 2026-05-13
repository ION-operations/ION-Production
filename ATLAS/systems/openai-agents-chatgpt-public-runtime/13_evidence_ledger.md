---
atlas_package: system
system_slug: openai-agents-chatgpt-public-runtime
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| oai-001 | Public HTTP API exists with documented endpoints | DOCUMENTED | `src-openai-api-ref` | |
| oai-002 | Authentication uses API keys / documented OAuth flows | DOCUMENTED | `src-openai-platform-docs` | Verify current flows |
| oai-003 | Internal service topology of ChatGPT | UNKNOWN | — | Explicit non-claim |
| oai-004 | Tool/function calling is part of documented API surface | DOCUMENTED | `src-openai-api-ref` | Model-dependent |
