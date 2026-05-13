---
atlas_package: system
system_slug: systemd-confext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Lower** **layer:** **host** **configuration** **tree** **(e.g.** **`/etc`** **per** **manual)** (`DOCUMENTED`).  
- **Upper** **layers:** **confext** **images** **merged** **read-only** **via** **overlay** (`DOCUMENTED`).

## Control plane

- **`systemd`** **drives** **merge** **/** **refresh** **through** **`systemd-confext`** **and** **its** **service** **unit** (`DOCUMENTED`).
