---
atlas_package: system
system_slug: freebsd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# FreeBSD — Identity

**Kind:** BSD-licensed **operating system** distributing kernel + base system (userland, ports/packages ecosystem), with features such as **ZFS**, **jails**, and **Capsicum** (`DOCUMENTED`, `src-freebsd-handbook`).

## Boundaries

- **Not** Linux; syscall and licensing models differ (`DOCUMENTED`).  
- **Not** identical to other BSDs (OpenBSD, NetBSD) — separate packages if deep comparison needed.

## Why this system matters

- Reference point for **jails** (OS-level virtualization) and **Capsicum** capabilities (`DOCUMENTED`).  
- **Ports/packages** dual packaging culture (`DOCUMENTED`).

## What this system teaches the atlas

- Compare **jail** vs **namespaces+cgroups** vs **NT job objects** in comparative docs.  
- How **base system coherence** differs from many Linux distros’ glue model (`INFERRED` pattern statement—tighten with sources).
