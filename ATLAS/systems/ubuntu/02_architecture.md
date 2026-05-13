---
atlas_package: system
system_slug: ubuntu
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`glibc`** **userland** **+** **`systemd`** **service** **supervision** **(default** **current** **releases)** (`DOCUMENTED`).  
- **Package** **metadata** **and** **maintainer** **scripts** **via** **`dpkg`** **/** **`apt`** **(Debian-class)** (`DOCUMENTED`).

## Delivery surfaces

- **Desktop** **/** **server** **ISOs**, **cloud** **images**, **container** **bases** **`ubuntu:*`**, **and** **WSL** **roots** (`DOCUMENTED` **/** `OBSERVED`).
