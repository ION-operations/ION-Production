---
atlas_package: system
system_slug: red-hat-openshift
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Red Hat OpenShift Container Platform — Identity

**Kind:** **OpenShift Container Platform (OCP)** is Red Hat’s platform for **developing and running containerized applications** with **Kubernetes as a core component**; Red Hat documents **extension** to **on-premise** and **multi-cloud** environments (`DOCUMENTED`, `src-redhat-ocp-kubernetes-overview`).

## Boundaries

- **Not** bare **upstream kubernetes** — **OCP platform** adds enterprise tooling and opinions (`DOCUMENTED`).  
- **Not** **OpenShift Dedicated** or **ROS** as this package’s primary subject — separate offerings (`UNKNOWN` at seed depth unless split).  
- **Not** undocumented OpenShift control-plane internals — **UNKNOWN** at depth.

## Why this system matters

- Strong **Kubernetes API compatibility** claims (**100% Kubernetes** API for the cluster in Red Hat’s overview copy) (`DOCUMENTED`).  
- **`oc`** / **`kubectl`** relationship documented for operator ergonomics (`DOCUMENTED`).

## What this system teaches the atlas

- Contrast **enterprise distribution** (`red-hat-openshift`) vs **hyperscaler-managed** SKUs vs **TKG-style** Cluster API management (`INFERRED` structural comparison).
