---
atlas_package: system
system_slug: centos-stream
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`glibc`** **+** **`systemd`** **(default)** (`DOCUMENTED`).  
- **RPM** **metadata** **via** **`dnf`** (`DOCUMENTED`).

## Delivery surfaces

- **Server** **/** **cloud** **images**, **`quay.io/centos/centos:stream*`** **OCI** **bases**, **bare** **metal** (`DOCUMENTED` **/** `OBSERVED`).
