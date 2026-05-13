---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Per-process visibility

Namespace **composition** affects **what** is reachable — security posture is tied to **mount visibility** and **file permissions** in the synthetic tree (`DOCUMENTED` model; **INFERRED** threat model depth).

## Authentication

**Factotum** and **secstore** appear in Plan 9 security discussions in surveys (`DOCUMENTED`, `src-wiki-plan9-security`).

## Absolute claims

**“Plan 9 is secure by default”** — **UNKNOWN** without cited audit; prefer **mechanism** descriptions.
