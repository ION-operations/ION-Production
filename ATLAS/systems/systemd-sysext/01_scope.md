---
atlas_package: system
system_slug: systemd-sysext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **`systemd-sysext`** **CLI** **and** **`systemd-sysext.service`** **lifecycle** **as** **documented** **on** **freedesktop.org** (`DOCUMENTED`, `src-sysext-man`, `src-sysext-service`).  
- **Merge** **model** **for** **system** **hierarchy** **extensions** **on** **Linux** **hosts** **running** **`systemd`** (`DOCUMENTED`).

## Out of scope

- **`systemd-confext`** **/** **`/etc`** **merge** — **`systemd-confext/`** **package** (`DOCUMENTED`).  
- **Vendor-specific** **extension** **image** **formats** **beyond** **documented** **systemd** **behaviors** (`INFERRED`).

## Versioning note

**Behavior** **tracks** **`systemd`** **releases** (`DOCUMENTED`).
