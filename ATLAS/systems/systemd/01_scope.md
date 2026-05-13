---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- PID 1 init system role, unit types, target/runlevel mapping, socket activation, timers, dependencies.  
- journald, logind, networkd, resolved, timesyncd where part of systemd suite (`DOCUMENTED` per component).  

## Out of scope

- Non-Linux ports except brief note.  
- Distro political debates — facts only with sources.

## Versioning note

Features gate on systemd release; cite version for precise behavior.
