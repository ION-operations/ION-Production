---
atlas_package: system
system_slug: fedora
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`glibc`** **userland** **+** **`systemd`** **service** **supervision** **(default** **current** **releases)** (`DOCUMENTED`).  
- **RPM** **metadata** **and** **scripts** **consumed** **via** **`dnf`** **/** **`rpm`** (`DOCUMENTED`).

## Delivery surfaces

- **Workstation** **/** **Server** **/** **IoT** **images**, **cloud** **templates**, **container** **bases** **`fedora:*`**, **and** **Silverblue**-**class** **ostree** **variants** (`DOCUMENTED` **/** `OBSERVED`).
