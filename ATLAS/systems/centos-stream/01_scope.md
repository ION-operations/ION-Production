---
atlas_package: system
system_slug: centos-stream
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **init** **/** **libc** **on** **supported** **CentOS** **Stream** **releases** (`DOCUMENTED`, `src-centos-stream-about`).  
- **`dnf`** **/** **`rpm`** **package** **surface** (`DOCUMENTED`, `src-dnf-user-guide-cs`).  
- **Upstream** **relationship** **to** **`rhel`** **minor** **streams** (`DOCUMENTED`).  
- **OCI** **/** **Kubernetes** **node** **adjacency** (`INFERRED` **/** **`DOCUMENTED`** **where** **cited**).

## Out of scope

- **Feature** **parity** **claims** **vs** **every** **Fedora** **release** **—** **pin** **docs** **when** **auditing** (`INFERRED`).

## Versioning note

**Stream** **major** **lines** **(e.g.** **8**/**9**)** **with** **rolling** **updates** **per** **project** **documentation** (`DOCUMENTED`).
