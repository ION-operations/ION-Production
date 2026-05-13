---
atlas_package: system
system_slug: runc
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **CLI** + **libcontainer** library internals (Go) as implemented in repo (`DOCUMENTED` source layout).  
- Consumes **bundle** (`config.json` + `rootfs`) (`DOCUMENTED`, `std-oci-runtime-spec`).  
- Applies **cgroups**, **namespaces**, **capabilities** per spec (`DOCUMENTED`).
