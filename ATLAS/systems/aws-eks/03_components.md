---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Components

| Layer | Role | Evidence |
|-------|------|----------|
| Managed control plane | Kubernetes control plane operated by AWS (standard EKS) | DOCUMENTED |
| Data plane / nodes | EC2 (and related compute options); Auto Mode manages nodes | DOCUMENTED |
| APIs / interfaces | Console, EKS API, SDKs, CDK, CLI, eksctl, IaC tools (as listed) | DOCUMENTED |
| EKS Capabilities | Managed add-ons (Argo CD, ACK, kro, … per capabilities doc) | DOCUMENTED |
