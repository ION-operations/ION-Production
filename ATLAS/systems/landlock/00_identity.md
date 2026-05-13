---
atlas_package: system
system_slug: landlock
schema_version: "1.0"
last_reviewed: "2026-04-18"
evidence_grade: B
---

# Landlock — Identity

**Kind:** **Linux** **Security** **Module** **(LSM)** **for** **unprivileged** **sandboxing** **via** **programmatic** **filesystem** **access** **rules** **(Landlock** **uAPI)** (`DOCUMENTED`, `src-landlock-kernel-docs`, `src-landlock-io`).

## Boundaries

- **Not** **the** **entire** **LSM** **framework** **or** **SELinux**/**AppArmor** **policy** **languages** — **see** **`linux-security-modules`**.  
- **Not** **`ebpf`** **or** **`libbpf`** — **distinct** **mechanism** **for** **kernel** **extensions** (`DOCUMENTED` **boundary**).  
- **Not** **containers** **/** **namespaces** **alone** — **see** **`docker`**, **`kubernetes`**.

## Why this system matters

- **Shows** **how** **capability-style** **sandboxing** **can** **exist** **without** **root-owned** **MAC** **policies** **on** **every** **deployment**.

## What this system teaches the atlas

**Separate** **Landlock** **(one** **LSM)** **from** **the** **umbrella** **`linux-security-modules`** **survey** **and** **from** **eBPF-based** **policy**.
