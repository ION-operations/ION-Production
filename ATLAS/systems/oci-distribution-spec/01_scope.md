---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- Registry **HTTP API** semantics for **manifests** and **blobs** (pull/push flows) (`DOCUMENTED`, `src-oci-distribution-spec-repo`).  
- **Conformance** themes and versioned API evolution in the OCI distribution project (`DOCUMENTED`).

## Out of scope

- **Image JSON schema** — **`oci-image-spec`**.  
- **Runtime** bundle execution — **`oci-runtime-spec`** (law); **`runc`** **implements** it.  
- Vendor-specific **authentication** extensions beyond what the spec class covers (`INFERRED` per registry).

## Versioning note

**Distribution** spec releases independently of **image** spec; clients must handle **capability** differences (`INFERRED`).
