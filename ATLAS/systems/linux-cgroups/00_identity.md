---
atlas_package: system
system_slug: linux-cgroups
schema_version: "1.0"
last_reviewed: "2026-04-21"
evidence_grade: B
---

# Linux cgroups — Identity

**Kind:** **Linux** **kernel** **cgroup** **hierarchy** **(cgroup** **v2** **focus** **in** **current** **admin** **guides)** **for** **resource** **control** **and** **accounting** (`DOCUMENTED`, `src-linux-cgroups-kernel-docs`).

## Boundaries

- **Not** **`linux-namespaces`** **view** **isolation** **alone** — **cgroups** **control** **resources;** **namespaces** **change** **visibility** (`DOCUMENTED` **boundary**).  
- **Not** **a** **container** **engine** — **see** **`docker`**, **`kubernetes`**.  
- **Not** **the** **cgroup** **namespace** **type** **by** **itself** — **that** **is** **a** **namespace** **kind** **under** **`linux-namespaces`**.

## Why this system matters

- **Explains** **CPU**/**memory**/**I/O** **limits** **and** **delegation** **without** **conflating** **them** **with** **PID**/**mount** **isolation**.

## What this system teaches the atlas

**Separate** **cgroup** **controllers** **from** **namespace** **sandboxes** **and** **from** **OCI** **runtime** **bundles**.
