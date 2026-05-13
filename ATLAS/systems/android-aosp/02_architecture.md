---
atlas_package: system
system_slug: android-aosp
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Linux kernel** + vendor modules (`DOCUMENTED`, `src-linux-kernel-android`).  
- **HAL** interfaces hardware to framework (`DOCUMENTED`).  
- **Native daemons** + **system server** hosting core services (`DOCUMENTED`).  
- **ART** executes app bytecode; **Zygote** process forking model (`DOCUMENTED` high level).  
- **Binder** as primary IPC (`DOCUMENTED`).

**UNKNOWN** at seed: per-service full dependency graph without diagram citation.
