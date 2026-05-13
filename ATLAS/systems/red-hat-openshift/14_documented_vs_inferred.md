---
atlas_package: system
system_slug: red-hat-openshift
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- OCP role + Kubernetes as core (`ocp-001`).  
- **Kubernetes API** positioning and **`oc`/`kubectl`** relationship (`ocp-002`, `ocp-003`).  
- **On-prem / multi-cloud** positioning (`ocp-004`).  
- **Conformance artifact** path for **`openshift`** (`ocp-005`; program `src-cncf-certified-kubernetes-program`).  
- **OpenShift Dedicated** adjacency — managed OCP clusters (`ocp-015`).

## INFERRED

- Substitution vs **OpenShift Dedicated** (`ocp-016`), **TKG**, **public/regional managed Kubernetes** (`ocp-006`–`ocp-014`).  
- **Linux-class nodes** typical (`depends_on` `linux-kernel`).

## Open questions

- Add **ROSA** (OpenShift on AWS) if AWS-only managed OpenShift claims need a separate package.  
- Pin **SR-IOV / edge** install variants only when atlas edges require them.

## Forbidden until sourced

- Red Hat-internal SRE topology.  
- “Always more secure than vanilla Kubernetes” — evaluative without methodology.
