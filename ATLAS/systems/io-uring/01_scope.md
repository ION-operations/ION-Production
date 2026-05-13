---
atlas_package: system
system_slug: io-uring
schema_version: "1.0"
last_reviewed: "2026-04-17"
evidence_grade: B
---

# Scope

## In scope

- **Kernel** **io_uring** **syscall** **surface** **and** **documented** **uAPI** **behavior** (`DOCUMENTED`).  
- **Submission** **/** **completion** **ring** **model** **vs** **legacy** **Linux** **AIO** **where** **documented** (`DOCUMENTED`).

## Out of scope

- **Specific** **hardware** **NVMe** **drivers** **—** **not** **this** **package** **identity**.  
- **Non-Linux** **kernels** **—** **out** **of** **package**.

## Versioning note

**Kernel** **release** **notes** **and** **uAPI** **extensions** **land** **with** **Linux** **versions** (`OBSERVED`).
