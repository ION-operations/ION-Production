---
atlas_package: system
system_slug: openai-agents-chatgpt-public-runtime
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Process, memory, and namespace model

- **Client-side:** user OS processes hold API keys and assemble prompts (`OBSERVED` / `DOCUMENTED` security guidance).  
- **Server-side memory:** context windows and conversation storage behaviors as documented per product (`DOCUMENTED`).  
- **Process isolation on vendor side:** **UNKNOWN**.
