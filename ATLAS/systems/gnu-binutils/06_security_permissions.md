---
atlas_package: system
system_slug: gnu-binutils
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Security and permissions

Manipulating binaries can weaken **RELRO** / strip symbols; security-sensitive contexts should pin flags (`INFERRED`).
