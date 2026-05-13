---
atlas_package: system
system_slug: centos-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`glibc`** **+** **`systemd`** **(default** **on** **7+)** (`DOCUMENTED`).  
- **RPM** **metadata** **via** **`yum`**/**`dnf`** (`DOCUMENTED`).

## Delivery surfaces

- **Server** **/** **cloud** **images**, **`centos:*`** **legacy** **OCI** **bases**, **bare** **metal** (`DOCUMENTED` **/** `OBSERVED`).
