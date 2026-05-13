---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

## Structural overview

- **PID 1** parses unit graph, applies transaction, tracks jobs (`DOCUMENTED`).  
- **Unit files** describe services, sockets, mounts, swaps, timers, paths, slices, scopes (`DOCUMENTED`).  
- **D-Bus** interface for runtime control (`DOCUMENTED`).  
- **journald** aggregates structured logs (`DOCUMENTED`).

## Control vs data plane

- **Control:** `systemctl`, D-Bus APIs, generators (`DOCUMENTED`).  
- **Data plane:** Managed daemons’ own I/O — systemd mediates lifecycle/cgroups only (`DOCUMENTED`).
