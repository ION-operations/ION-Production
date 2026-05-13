---
atlas_package: system
system_slug: openshift-dedicated
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed **OCP** on **AWS/GCP** (`osd-001`).  
- **CCS** vs **Red Hat–owned** account models (`osd-002`, `osd-003`).  
- **Conformance** artifact path **`openshift-dedicated`** (`osd-004`; program `src-cncf-certified-kubernetes-program`).  
- **Product-line link** to **`red-hat-openshift`** via `integrates_with` in `relations.json` (OCP clusters as managed service).

## INFERRED

- Substitution vs **self-managed OCP** and other **managed Kubernetes** platforms (`osd-005`–`osd-014`).  
- **Linux-class workers** (`depends_on` `linux-kernel`).

## Open questions

- Add **`rosa`** (OpenShift on AWS) package if AWS-only managed OpenShift claims need isolation from OSD.  
- Pin **introduction_to_openshift_dedicated** chapter when the getting-started hub is too coarse.

## Forbidden until sourced

- Red Hat–internal SRE incident workflows.  
- “Always cheaper than EKS” — evaluative.
