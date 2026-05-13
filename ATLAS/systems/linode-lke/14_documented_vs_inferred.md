---
atlas_package: system
system_slug: linode-lke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed Kubernetes product framing (`lke-001`, `lke-002`).  
- **Public conformance artifacts** under **`linode`** in CNCF’s versioned submission tree (`lke-003`; program context `src-cncf-certified-kubernetes-program`).

## INFERRED

- Multi-vendor substitution vs other managed Kubernetes (`relations.json`; `lke-004`–`lke-013`).  
- **Linux-class workers** as typical node hosts (`depends_on` `linux-kernel` in `relations.json`).

## Open questions

- Pin child pages (node pools, upgrades, networking) when comparative matrices need depth.  
- If Akamai adds explicit **marketing conformance** copy on the LKE landing page, align `lke-001`–`lke-002` without dropping `lke-003`.

## Forbidden until sourced

- Akamai-internal control-plane topology.  
- Benchmark superiority without methodology.
