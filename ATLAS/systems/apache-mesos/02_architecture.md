---
atlas_package: system
system_slug: apache-mesos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Architecture

- **Mesos kernel on each machine** offering APIs for resource management and scheduling across clusters — phrasing per historical project summary (`HISTORICAL`, `src-apache-mesos-site`).  
- **Two-level scheduling** described as a first-class design point (`HISTORICAL`).  
- **HA** described as replicated master/agents with **ZooKeeper** in historical marketing copy (`HISTORICAL` — upgrade with archived technical spec if needed).

## UNKNOWN at seed depth

- Exact current artifact locations for every subsystem spec post-Attic — use Attic and archive mirrors when deepening.
