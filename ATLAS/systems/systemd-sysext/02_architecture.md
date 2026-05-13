---
atlas_package: system
system_slug: systemd-sysext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Lower** **layer:** **host** **`/usr`** **(or** **configured** **merge** **root)** (`DOCUMENTED`).  
- **Upper** **layers:** **one** **or** **more** **sysext** **images** **merged** **read-only** **via** **overlay** **(per** **manuals)** (`DOCUMENTED`).

## Control plane

- **`systemd`** **invokes** **merge** **/** **refresh** **logic** **through** **`systemd-sysext`** **and** **service** **units** (`DOCUMENTED`).
