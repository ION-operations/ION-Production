---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **EKS standard:** AWS manages the **Kubernetes control plane**; node/worker responsibilities follow AWS vs customer split per shared responsibility docs (`DOCUMENTED`).  
- **EKS Auto Mode:** AWS extends management to **Kubernetes nodes** (data plane) with automated provisioning/scaling/patching patterns as described (`DOCUMENTED`).  
- **Conformance:** Amazon EKS is described as **Kubernetes-conformant**, enabling community tooling where applicable (`DOCUMENTED`).

## UNKNOWN at seed depth

- Internal placement of apiserver/etcd equivalents inside AWS — not asserted.
