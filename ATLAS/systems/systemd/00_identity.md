---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# systemd — Identity

**Kind:** Userspace service manager and system bootstrap suite for Linux, conventionally PID 1, providing unit-based activation, dependency resolution, logging, and host integration.

## Canonical definition

systemd manages services via unit files, uses the journal for structured logging, and provides a broad set of host management daemons and D-Bus APIs (`DOCUMENTED`, `src-systemd-documentation`).

## Boundaries

- **Not** the Linux kernel.  
- **Not** a container orchestrator — relationship to workloads is **host service** scope unless explicitly integrated (`kubernetes` edge is operational pattern).  
- **Unit file grammar** (sections, directives, drop-ins, generators) is cataloged separately as **`systemd-unit-model`** — this package is the **whole suite** / PID 1 identity.  
- **Portable service images** / **`portablectl`** are cataloged as **`systemd-portable`** — attachable bundle workflow distinct from generic PID 1 overview text alone.  
- **System extensions** / **`systemd-sysext`** are cataloged as **`systemd-sysext`** — **`/usr`** **merge** **via** **overlay** **semantics**, **distinct** **from** **portable** **services** **and** **from** **containers**.  
- **Configuration extensions** / **`systemd-confext`** are cataloged as **`systemd-confext`** — **`/etc`**-**class** **merge** **via** **overlay**, **sibling** **to** **`systemd-sysext`** **per** **manuals**.

## Why this system matters

- Defines **modern Linux boot + service lifecycle** on major distributions (`OBSERVED` + `DOCUMENTED`).  
- **Declarative units** parallel desired-state patterns at single-host scale (`DOCUMENTED`).  
- **Journal + cgroups integration** shape observability and resource accounting (`DOCUMENTED`).

## What this system teaches the atlas

- Single-host **desired-state** vs cluster reconcilers (`kubernetes`).  
- How **dbus**-mediated control planes appear in OS services.
