---
atlas_package: system
system_slug: debian
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **init** **and** **libc** **story** **on** **current** **Debian** **stable** **per** **project** **docs** **and** **wiki** (`DOCUMENTED`, `src-debian-systemd-wiki`).  
- **`dpkg`** **/** **`apt`** **as** **the** **primary** **package** **manager** **surface** (`DOCUMENTED`).  
- **OCI** **/** **Kubernetes** **ecosystem** **adjacency** **where** **Debian** **or** **derivative** **bases** **dominate** (`INFERRED` **/** **`DOCUMENTED`** **where** **cited**).

## Out of scope

- **`ubuntu`** **as** **a** **separate** **ATLAS** **package** — **seeded** **(Debian**-**derived** **`linux-distribution`)**; **other** **RHEL**-**class** **derivatives** **still** **not** **seeded** (`INFERRED`).  
- **Full** **Debian** **Policy** **manual** **line-by-line** — **pin** **sections** **when** **auditing** (`INFERRED`).

## Versioning note

**Stable** **/** **testing** **/** **sid** **suites** **and** **point** **releases** **define** **effective** **package** **sets** (`DOCUMENTED`).
