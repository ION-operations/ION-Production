---
atlas_package: system
system_slug: vscode
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Process, memory, and namespace model

- **Multi-process** desktop app; extension isolation via separate host process (`DOCUMENTED`).  
- **Workspace folders** define file access roots for extensions (`DOCUMENTED`).  
- **Sandboxing** evolution: consult current VS Code security documentation for extension host restrictions (`DOCUMENTED` — version-sensitive).
