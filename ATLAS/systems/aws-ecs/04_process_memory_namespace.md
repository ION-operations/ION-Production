---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Process, memory, and namespace model

- **Isolation and resource semantics** follow AWS-documented task/Fargate/EC2 models (`DOCUMENTED` at product level).  
- **Host-level namespace layout** on Fargate and managed capacity is **not** specified in this seed — **UNKNOWN** at internal depth.
