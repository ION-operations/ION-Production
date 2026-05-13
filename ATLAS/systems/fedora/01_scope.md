---
atlas_package: system
system_slug: fedora
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **init** **and** **libc** **story** **on** **supported** **Fedora** **releases** **per** **project** **docs** (`DOCUMENTED`, `src-fedora-releases`).  
- **`dnf`** **/** **`rpm`** **as** **the** **primary** **package** **manager** **surface** (`DOCUMENTED`, `src-dnf-user-guide`).  
- **OCI** **/** **Kubernetes** **ecosystem** **adjacency** **where** **`fedora:*`** **images** **and** **Fedora** **node** **OS** **choices** **appear** (`INFERRED` **/** **`DOCUMENTED`** **where** **cited**).

## Out of scope

- **`rhel`** **as** **a** **separate** **ATLAS** **package** — **seeded**; **CentOS** **Stream,** **Rocky,** **Alma** **still** **not** **seeded** **here** (`INFERRED`).  
- **Full** **Fedora** **Packaging** **Guidelines** **line-by-line** — **pin** **sections** **when** **auditing** (`INFERRED`).

## Versioning note

**Approximately** **six-month** **release** **cadence** **with** **documented** **support** **windows** **defines** **effective** **package** **sets** (`DOCUMENTED`).
