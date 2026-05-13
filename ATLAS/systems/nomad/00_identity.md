---
atlas_package: system
system_slug: nomad
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# HashiCorp Nomad — Identity

**Kind:** **Cluster scheduler and orchestrator** for running container, VM, Java, batch, and other workload types across a pool of agents, with a centralized control plane (`DOCUMENTED`, `src-nomad-docs`).

## Boundaries

- **Not** Kubernetes — different API/object model and ecosystem (`DOCUMENTED` comparative).  
- **Not** only containers — task drivers span multiple execution backends (`DOCUMENTED`).

## Why this system matters

- Reference point for **non-Kubernetes** orchestration patterns still widely deployed (`OBSERVED` / `DOCUMENTED`).  
- Useful comparator for **multi-scheduler** vs **kube-only** operations models (`INFERRED` ops pattern).

## What this system teaches the atlas

- “Orchestrator” is not synonymous with “pods/deployments”; compare **job**/**allocation** semantics in `comparative/orchestration_models.md`.
