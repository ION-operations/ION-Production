---
atlas_package: system
system_slug: digitalocean-doks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Managed Kubernetes framing; HA/autoscaling claims; integration bullets (`doks-001`–`doks-003`).  
- **Public conformance artifacts** for the DigitalOcean product family under CNCF’s versioned submission tree (`doks-004`; program context `src-cncf-certified-kubernetes-program`).

## INFERRED

- Multi-vendor substitution vs other managed Kubernetes (`relations.json`; `doks-005`–`doks-014`).

## Open questions

- Pin a single **“Concepts/overview”** child page if the docs index is too volatile for long-term citation.  
- If product marketing adds explicit **CNCF conformance** copy on the DOKS landing page, mirror that language in `doks-001`–`doks-003` without dropping `doks-004`.

## Forbidden until sourced

- DigitalOcean-internal control plane topology.  
- Benchmark superiority without methodology.
