---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Amazon Elastic Kubernetes Service (EKS) — Identity

**Kind:** **Fully managed Kubernetes service** on AWS: AWS operates the Kubernetes control plane for standard EKS; optional **EKS Auto Mode** extends managed scope to nodes per AWS docs (`DOCUMENTED`, `src-aws-eks-user-guide`).

## Boundaries

- **Not** “Kubernetes the upstream project” — this package is the **AWS product** that hosts conformant Kubernetes clusters (`DOCUMENTED`).  
- **Not** a map of undocumented AWS control-plane microservices — **UNKNOWN** at internal depth.

## Why this system matters

- Canonical bridge between **upstream Kubernetes** semantics and **AWS-managed operations** (`DOCUMENTED`).  
- Pairs with **`aws-ecs`** as the other major AWS container orchestration product line (`INFERRED` market framing).

## What this system teaches the atlas

- Distinguish **Kubernetes API portability** (conformance) from **control-plane ownership** (self vs AWS) in `comparative/orchestration_models.md`.
