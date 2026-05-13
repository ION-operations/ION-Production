---
atlas_package: system
system_slug: ubuntu
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **init** **and** **libc** **story** **on** **supported** **Ubuntu** **releases** **per** **project** **docs** (`DOCUMENTED`, `src-ubuntu-release-cycle`).  
- **`dpkg`** **/** **`apt`** **as** **the** **primary** **package** **manager** **surface** **(Debian** **heritage)** (`DOCUMENTED`).  
- **OCI** **/** **Kubernetes** **ecosystem** **adjacency** **where** **`ubuntu:*`** **images** **and** **Ubuntu** **node** **OS** **choices** **dominate** (`INFERRED` **/** **`DOCUMENTED`** **where** **cited**).

## Out of scope

- **Mint,** **Pop!_OS,** **other** **flavors** **as** **separate** **packages** — **not** **seeded** (`INFERRED`).  
- **Full** **Ubuntu** **Security** **Notices** **corpus** — **pin** **USN** **IDs** **when** **auditing** (`INFERRED`).

## Versioning note

**LTS** **and** **interim** **releases** **with** **defined** **support** **windows** **define** **effective** **package** **sets** (`DOCUMENTED`).
