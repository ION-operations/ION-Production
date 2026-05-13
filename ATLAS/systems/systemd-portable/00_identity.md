---
atlas_package: system
system_slug: systemd-portable
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# systemd portable services

**Kind:** **systemd** subsystem for **portable service images** — **OS tree**-style bundles (often **raw**/**directory** profiles) attached to the host **`systemd`** with **`portablectl`**, enabling **system extension** / **portable service** workflows documented on **systemd.io** (`DOCUMENTED`, `src-portable-io`, `src-portablectl`).

## Boundaries

- **Not** **OCI** images — **`oci-image-spec`** defines the interoperable **container image** layout; **`docker`** is an engine that uses it (`DOCUMENTED` comparative).  
- **Not** the full **PID 1** suite identity — this is a **feature slice** of **`systemd`** (`DOCUMENTED`).  
- **Not** only **unit file grammar** — **`systemd-unit-model`** covers `.service` text; portable adds **image attach** semantics (`DOCUMENTED` split).

## Why this system matters

- **Field pattern** for shipping **services** as **immutable-ish** bundles on **systemd** hosts without full container orchestration (`DOCUMENTED`).  
- **`systemd-sysext`** covers **system** **extension** **merge** **(`sysext`)** **as** **its** **own** **ATLAS** **package**; **confext** **/** **`/etc`** **merge** **remains** **optional** (`DOCUMENTED` **split**).

## What this system teaches the atlas

- Separate **orchestrator** (`systemd`), **unit grammar** (`systemd-unit-model`), and **portable attach** (`systemd-portable`) when auditing Linux service delivery.
