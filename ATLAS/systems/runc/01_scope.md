---
atlas_package: system
system_slug: runc
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- `runc create/start/exec` class commands, lifecycle, hooks (`DOCUMENTED` README/docs in repo).  
- Alignment with **runtime-spec** fields (`DOCUMENTED`).

## Out of scope

- Kubernetes scheduling — `kubernetes` package.  
- Windows container isolation technologies unrelated to Linux runc usage.

## Versioning note

`runc` releases track security fixes and spec drift — cite version for behavioral claims (`DOCUMENTED`).
