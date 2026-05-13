---
atlas_package: system
system_slug: ibm-iks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed Kubernetes + master ownership claims (`iks-001`–`iks-004`).

## INFERRED

- Multi-vendor substitution vs other managed Kubernetes (`relations.json`; `iks-005`–`iks-010`).

## Open questions

- Add stable `cloud.ibm.com/docs/containers` deep links when batch-fetchable for curator tooling.  
- Separate **IBM Cloud Code Engine** package if serverless claims need isolation.

## Forbidden until sourced

- IBM-internal control plane topology.  
- “Always more secure than hyperscaler X” — evaluative.
