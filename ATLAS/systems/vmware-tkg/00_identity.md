---
atlas_package: system
system_slug: vmware-tkg
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# VMware Tanzu Kubernetes Grid (TKG) — Identity

**Kind:** **Tanzu Kubernetes Grid (TKG)** is a **VMware** (now **Broadcom** documentation) offering that deploys Kubernetes using an **opinionated configuration** of **open-source Kubernetes** software **supported by VMware**, with **validated Kubernetes component binaries** and **packaged services** (networking, authentication, ingress, logging) for production use (`DOCUMENTED`, `src-broadcom-tkg-about`).

## Boundaries

- **Not** bare **upstream kubernetes** — **TKG distribution + services + lifecycle tooling** (`DOCUMENTED`).  
- **Not** **Tanzu Kubernetes Grid Integrated Edition** — Broadcom documents that as a **separate product** not covered by the TKG 2.5 publication (`DOCUMENTED`, same hub).  
- **Not** full **vSphere Supervisor** operations — cross-linked but **out of scope** for this TKG doc set (`DOCUMENTED` scope note).

## Why this system matters

- **Hybrid / datacenter** Kubernetes platform pattern vs **fully managed public-cloud** control planes (`INFERRED` positioning).  
- **Cluster API**–centric management cluster model (`DOCUMENTED`).

## What this system teaches the atlas

- Split **vendor-managed public SKU** packages (EKS, AKS, …) from **customer-operated platform** distributions (`INFERRED` structural contrast).
