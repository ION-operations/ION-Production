---
atlas_package: system
system_slug: systemd-confext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **`systemd-confext`** **CLI** **and** **`systemd-confext.service`** **as** **documented** **on** **freedesktop.org** (`DOCUMENTED`, `src-confext-man`, `src-confext-service`).  
- **Overlay** **merge** **semantics** **for** **configuration** **trees** **on** **`systemd`** **Linux** **hosts** (`DOCUMENTED`).

## Out of scope

- **Exact** **list** **of** **merged** **paths** **beyond** **manual** **wording** — **pin** **per** **`systemd`** **release** **when** **auditing** (`INFERRED`).  
- **`systemd-sysext`** **/** **`/usr`** **merge** **—** **see** **`systemd-sysext/`** (`DOCUMENTED`).

## Versioning note

**Behavior** **tracks** **`systemd`** **releases** (`DOCUMENTED`).
