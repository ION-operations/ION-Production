---
atlas_package: system
system_slug: fluxcd
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# Flux (fluxcd) — Identity

**Kind:** **CNCF** **GitOps** **toolkit** **for** **Kubernetes** **that** **continuously** **reconciles** **desired** **state** **from** **Git** **and** **registry** **sources** **into** **the** **cluster** **API** (`DOCUMENTED`, `src-fluxcd-docs`, `src-fluxcd-github`).

## Boundaries

- **Not** **`kubernetes`** **itself** **—** **Flux** **is** **controllers** **+** **CRDs** **that** **drive** **the** **Kubernetes** **API.**  
- **Not** **`helm`** **alone** **—** **Helm** **is** **chart** **packaging;** **Flux** **orchestrates** **reconciliation** **and** **can** **embed** **Helm** **releases** **as** **one** **path.**  
- **Not** **`oci-runtime-spec`** **—** **Flux** **does** **not** **execute** **OCI** **runtime** **bundles** **directly.**

## Why this system matters

- **Makes** **“desired** **state** **in** **Git”** **a** **first-class** **delivery** **path** **distinct** **from** **ad-hoc** **`kubectl`** **apply** **and** **from** **image** **build** **alone.**

## What this system teaches the atlas

**Separate** **reconciliation** **controllers** **(GitOps)** **from** **package** **managers** **(Helm** **CLI)** **and** **from** **the** **orchestrator** **API** **(Kubernetes)** **even** **when** **they** **compose** **in** **one** **cluster.**
