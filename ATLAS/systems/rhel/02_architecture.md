---
atlas_package: system
system_slug: rhel
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **streams** **+** **`glibc`** **userland** **+** **`systemd`** **service** **supervision** **(default** **supported** **releases)** (`DOCUMENTED`).  
- **RPM** **metadata** **and** **scripts** **consumed** **via** **`dnf`** **/** **`yum`**-**class** **interfaces** (`DOCUMENTED`).

## Delivery surfaces

- **Installer** **images**, **cloud** **marketplace** **AMIs** **/** **images**, **container** **bases** **(UBI** **/** **vendor** **published** **RHEL** **roots)**, **and** **bare** **metal** (`DOCUMENTED` **/** `OBSERVED`).
