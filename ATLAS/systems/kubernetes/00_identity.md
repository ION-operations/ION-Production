---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Kubernetes — Identity

**Kind:** Open-source cluster orchestrator reconciling declared workload and cluster state via APIs, controllers, and pluggable runtimes for containers.

## Canonical definition

Kubernetes exposes a declarative API for pods, services, deployments, and cluster resources; control plane components reconcile desired state with actual cluster state (`DOCUMENTED`, `src-kubernetes-docs`).

## Boundaries

- **Not** a container runtime — uses **CRI** (`DOCUMENTED`).  
- **Not** a Linux distribution — depends on node OS (`depends_on` `linux-kernel`).

## Why this system matters

- **De facto** model for cloud-native scheduling and service discovery (`OBSERVED` + `DOCUMENTED`).  
- **Extension points** (CNI, CSI, admission, operators) define a control-plane ecosystem (`DOCUMENTED`).  
- **Pattern template** for level-triggered reconciliation controllers (`DOCUMENTED`).

## What this system teaches the atlas

- How **declarative APIs** separate user intent from reconciling controllers.  
- How **plugin edges** (CNI/CSI) standardize datacenter variation.
