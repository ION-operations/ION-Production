---
atlas_package: system
system_slug: rhel
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **init** **and** **libc** **story** **on** **supported** **RHEL** **major** **/** **minor** **streams** **per** **Red** **Hat** **docs** (`DOCUMENTED`, `src-rhel-lifecycle`).  
- **`rpm`** **/** **`dnf`** **as** **the** **primary** **package** **manager** **surface** (`DOCUMENTED`).  
- **OpenShift** **/** **Kubernetes** **node** **OS** **adjacency** **where** **RHEL** **is** **the** **documented** **base** (`DOCUMENTED` **/** `INFERRED`).

## Out of scope

- **`rocky-linux`** **and** **`almalinux`** **as** **separate** **ATLAS** **packages** — **seeded**; **CentOS** **Stream** **still** **not** **seeded** **here** (`INFERRED`).  
- **Full** **Red** **Hat** **Subscription** **Agreement** **text** — **legal** **artifact** **out** **of** **ATLAS** **grain** (`INFERRED`).

## Versioning note

**Major** **minor** **streams** **with** **documented** **full** **support** **/** **maintenance** **phases** **define** **effective** **package** **sets** (`DOCUMENTED`).
