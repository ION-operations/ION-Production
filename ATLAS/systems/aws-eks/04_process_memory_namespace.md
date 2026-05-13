---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Process, memory, and namespace model

- **Kubernetes pod/container isolation** on workers follows Kubernetes + CRI + OS semantics (`DOCUMENTED` upstream pattern; EKS-specific defaults vary by AMI/runtime).  
- **Host-level details** under Auto Mode or Fargate-style paths — follow AWS compute docs; **UNKNOWN** at this seed’s depth.
