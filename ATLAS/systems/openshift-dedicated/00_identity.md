---
atlas_package: system
system_slug: openshift-dedicated
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# OpenShift Dedicated — Identity

**Kind:** **OpenShift Dedicated** offers **OpenShift Container Platform clusters as a managed service** on **Amazon Web Services (AWS)** or **Google Cloud** (`DOCUMENTED`, `src-redhat-osd-getting-started`).

## Boundaries

- **Not** self-installed **OpenShift Container Platform** in customer datacenter — that is the **`red-hat-openshift`** package (`INFERRED` positioning).  
- **Not** **ROSA** (OpenShift on AWS managed SKU) unless merged into this doc set — treat as separate SKU until a dedicated package exists (`UNKNOWN` at seed depth).  
- **Not** undocumented SRE runbooks — **UNKNOWN** at depth.

## Why this system matters

- **Red Hat–operated** control plane + **CCS vs Red Hat–owned account** deployment models (`DOCUMENTED`).  
- **Direct adjacency** to **hyperscaler managed Kubernetes** (EKS/GKE) when customers standardize on OpenShift on those clouds (`INFERRED`).

## What this system teaches the atlas

- Split **vendor-managed OpenShift** (`openshift-dedicated`) from **customer-operated OCP** (`red-hat-openshift`) while sharing the **Kubernetes / OpenShift** API family (`DOCUMENTED` / `INFERRED`).
