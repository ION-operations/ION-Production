---
atlas_package: system
system_slug: aws-eks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- EKS standard vs Auto Mode (as named in AWS docs), hybrid / anywhere pointers, IAM + Kubernetes access integration (`DOCUMENTED` at overview depth).  
- Documented related AWS services (EC2, ECR, ELB, CloudWatch, …) as cross-links only (`DOCUMENTED`).

## Out of scope

- Per-account service implementation topology — **UNKNOWN**.  
- Non-AWS Kubernetes distros — separate packages.

## Versioning note

Kubernetes version support policies (standard vs extended) are AWS-documented and time-bounded (`DOCUMENTED`).
