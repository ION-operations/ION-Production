---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

## Structural overview

- **kube-apiserver:** REST API front door; authn/z, admission (`DOCUMENTED`).  
- **etcd:** typical backing store for cluster state (`DOCUMENTED` default architecture).  
- **kube-scheduler:** assigns pods to nodes (`DOCUMENTED`).  
- **kube-controller-manager / cloud-controller-manager:** reconciliation loops (`DOCUMENTED`).  
- **kubelet:** node agent enforcing pod lifecycle via CRI (`DOCUMENTED`).  
- **kube-proxy:** service load balancing datapath (implementation varies) (`DOCUMENTED`).

## Control vs data plane

- **Control plane:** API + controllers + scheduler (`DOCUMENTED`).  
- **Data plane:** pod network (CNI), container runtime, service proxying (`DOCUMENTED`).
