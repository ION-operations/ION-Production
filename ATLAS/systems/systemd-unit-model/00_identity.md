---
atlas_package: system
system_slug: systemd-unit-model
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# systemd unit file model

**Kind:** **Normative text model** for **systemd units** — `.service`, `.socket`, `.target`, `.timer`, `.mount`, `.slice`, … — including **sections**, **directives**, **drop-in** fragments, and **generator**-produced transient units (`DOCUMENTED`, `src-systemd-unit`, `src-systemd-service`).

## Boundaries

- **Not** the whole **systemd** suite — no claim to cover **journald**, **networkd**, **logind**, or full **D-Bus** API (`DOCUMENTED` split; see `systemd`).  
- **Not** **Linux cgroups** internals — units **reference** cgroup settings; kernel behavior is `linux-kernel`.  
- **Not** **xinetd**-class inetd — `.socket` activation is **systemd-specific** (`DOCUMENTED`).

## Why this system matters

- **Law grain** for “what a valid unit means” separate from “what PID 1 is” — audits and generators depend on this surface (`DOCUMENTED`).  
- **Drop-in** / **override** semantics are a reusable **layered config** pattern (`DOCUMENTED`).

## What this system teaches the atlas

- Split **orchestrator identity** (`systemd`) from **declarative grammar** (`systemd-unit-model`) when comparing to **Kubernetes** YAML or other desired-state DSLs.
