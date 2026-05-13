---
atlas_package: system
system_slug: apache-mesos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Apache Mesos — Identity

**Kind:** **Retired** Apache cluster manager (“distributed systems kernel”) historically used for two-level scheduling and datacenter-scale workloads (`HISTORICAL`, `src-apache-mesos-site`, `src-apache-attic-mesos`).

## Boundaries

- **Not** actively maintained product guidance — treat operational claims as **HISTORICAL** unless sourced to a specific release doc archive.  
- **Not** Kubernetes — different architecture and ecosystem (`HISTORICAL` comparative).

## Why this system matters

- **Historical anchor** for two-level scheduling and Mesos-framework patterns that influenced later systems discourse (`HISTORICAL`).  
- Demonstrates how atlas handles **retired** infrastructure with explicit tiering.

## What this system teaches the atlas

- Compare **framework/plugin scheduler** layering to Kubernetes’ monolithic scheduler + controllers model in `comparative/orchestration_models.md` (high level only at seed depth).
