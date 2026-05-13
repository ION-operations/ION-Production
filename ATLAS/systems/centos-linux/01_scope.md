---
atlas_package: system
system_slug: centos-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **init** **/** **libc** **on** **supported** **CentOS** **Linux** **minor** **releases** **(historical** **survey)** (`DOCUMENTED`, `src-centos-faq-eol`).  
- **`yum`**/**`dnf`** **/** **`rpm`** **package** **surface** (`DOCUMENTED`).  
- **RHEL**-**compatible** **rebuild** **heritage** **and** **EOL** **announcements** (`DOCUMENTED`).  
- **OCI** **/** **Kubernetes** **historical** **adjacency** (`INFERRED` **/** **`DOCUMENTED`** **where** **cited**).

## Out of scope

- **Per**-**minor** **fork** **packages** **(e.g.** **7** **vs** **8)** — **use** **release** **notes** **when** **auditing** (`INFERRED`).

## Versioning note

**CentOS** **Linux** **7** **and** **8** **fixed** **lines** **with** **documented** **EOL** **dates** **per** **project** **communications** (`DOCUMENTED`).
