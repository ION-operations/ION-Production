---
atlas_package: system
system_slug: systemd-portable
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **`portablectl`** commands: **attach**, **detach**, **list**, **reboot** semantics as documented (`DOCUMENTED`, `src-portablectl`).  
- **Portable service** concepts from **systemd.io** (`DOCUMENTED`, `src-portable-io`).

## Out of scope

- **Portable** **wallet** / unrelated “portable” software — word-sense trap (`UNKNOWN` here).  
- **Vendor** fork behaviors — pin distro notes when load-bearing (`INFERRED`).

## Versioning note

Feature set expanded across **systemd** releases; cite **version** when making capability claims (`INFERRED`).
