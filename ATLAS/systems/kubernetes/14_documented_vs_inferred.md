---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Documented vs inferred

## DOCUMENTED claims

- Control plane/node split; CRI/CNI/CSI extension model (`k8s-001`–`k8s-004`).  
- **Managed offering link:** Amazon EKS described as Kubernetes-conformant managed service (`k8s-008`).  
- **Managed offering links:** Azure AKS (`k8s-009`) and Google GKE (`k8s-010`) as vendor-managed Kubernetes surfaces.  
- **Embedded Kubernetes:** Azure Container Apps (`k8s-011`) — substrate without kube-apiserver access.  
- **Oracle OKE** managed Kubernetes link (`k8s-012`).  
- **IBM IKS** managed Kubernetes link (`k8s-013`).  
- **ACI-backed Kubernetes capacity** via AKS virtual nodes (`k8s-014`).  
- **DigitalOcean DOKS** managed Kubernetes link (`k8s-015`).  
- **Civo managed Kubernetes** link with conformance language (`k8s-016`).  
- **Akamai LKE** managed Kubernetes link (`k8s-017`).  
- **VMware TKG** distribution link (`k8s-018`).  
- **Red Hat OpenShift** platform link (`k8s-019`).  
- **OpenShift Dedicated** managed offering link (`k8s-020`).

## INFERRED claims

- **systemd packaging** prevalence — operational pattern, not API guarantee.  
- **Orchestrator substitution** with Nomad-class systems in some on-prem / edge footprints (`k8s-005`) — not mutual exclusion in the knowledge model.  
- **Managed cloud orchestrator** substitution framing vs ECS (`k8s-006`) — AWS-specific control plane and APIs.

## HISTORICAL

- **Mesos-era** cluster-manager discourse vs Kubernetes adoption (`k8s-007`) — Mesos is retired; no ongoing API competition claim.

## OBSERVED

- Distribution-specific defaults (CNI choice, ingress) — record per environment.

## Open questions

- Windows node datapath differences — expand with Microsoft Kubernetes on Windows docs.  
- etcd vs alternative stores in custom distros — mark per distribution.

## Forbidden until sourced

- Internal cloud provider placement algorithms.  
- Undocumented API behaviors.
