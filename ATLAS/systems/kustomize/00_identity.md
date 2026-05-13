---
atlas_package: system
system_slug: kustomize
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Kustomize — Identity

**Kind:** **Kubernetes** **native** **configuration** **tool** **for** **building** **manifests** **from** **bases** **and** **overlays** **(kustomization.yaml)** **without** **template** **languages** **in** **the** **core** **model** (`DOCUMENTED`, `src-kustomize-docs`, `src-kustomize-github`).

## Boundaries

- **Not** **`kubernetes`** **itself** **—** **Kustomize** **emits** **API** **objects;** **it** **does** **not** **run** **the** **control** **plane.**  
- **Not** **`helm`** **as** **the** **same** **packaging** **model** **—** **Helm** **charts** **are** **a** **different** **distribution** **and** **templating** **story** **(often** **composed** **with** **Kustomize** **via** **post-render).**  
- **Not** **`oci-runtime-spec`** **—** **Kustomize** **does** **not** **execute** **OCI** **bundles.**

## Why this system matters

- **Captures** **the** **“overlay** **/** **patch”** **declarative** **path** **alongside** **Helm** **charts** **in** **real** **Kubernetes** **delivery** **pipelines.**

## What this system teaches the atlas

**Configuration** **composition** **(Kustomize)** **and** **package** **templating** **(Helm)** **are** **different** **edges** **even** **when** **chained** **in** **one** **pipeline.**
