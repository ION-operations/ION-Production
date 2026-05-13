---
atlas_package: system
system_slug: debug-adapter-protocol
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `vscode` / `cursor`:** built-in or extension-backed DAP clients (`DOCUMENTED` product pattern; pin URLs in package `sources.yaml` when curating).  
- **`integrates_with` `language-server-protocol`:** complementary **language** vs **debug** planes in the same editor (`INFERRED` architecture pattern).  
- **`integrates_with` `model-context-protocol`:** may coexist in **agent-augmented** editors; different capability contracts (`INFERRED`).
