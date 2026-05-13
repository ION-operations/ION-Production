---
atlas_package: system
system_slug: systemd-unit-model
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **Unit file** structure: sections, key-value directives, line continuation, include rules (`DOCUMENTED`, `src-systemd-unit`).  
- **Install** section semantics for **enablement** (`WantedBy`, …) (`DOCUMENTED`).  
- **Generators** — `systemd.generator(7)` contract (`DOCUMENTED`, `src-systemd-generator`).

## Out of scope

- **Preset** policy files — adjacent; pin if load-bearing (`INFERRED`).  
- **Portable services** / **portablectl** image format — see `systemd` **portable** docs unless split later.

## Versioning note

Directive sets evolve with **systemd** releases; always cite **manual version** / distro (`INFERRED` deployment).
