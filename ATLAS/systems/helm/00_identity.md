---
atlas_package: system
system_slug: helm
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Helm — Identity

**Kind:** **Kubernetes** **package** **manager** **for** **charts** **(templated** **manifests** **and** **release** **lifecycle)** **operating** **against** **the** **Kubernetes** **API** (`DOCUMENTED`, `src-helm-docs`, `src-helm-github`).

## Boundaries

- **Not** **`kubernetes`** **itself** **—** **Helm** **is** **a** **client** **/** **operator** **pattern** **for** **installing** **workloads** **on** **a** **cluster** **API** **server.**  
- **Not** **`oci-runtime-spec`** **—** **Helm** **does** **not** **execute** **OCI** **runtime** **bundles** **directly.**  
- **Not** **`oci-image-spec`** **alone** **—** **charts** **describe** **Kubernetes** **resources** **and** **may** **reference** **images** **as** **strings** **rather** **than** **being** **the** **image** **format** **law.**

## Why this system matters

- **Separates** **“release** **packaging** **/** **templating”** **from** **“container** **image** **layout”** **and** **from** **“kubelet** **runtime** **path”** **in** **the** **delivery** **story.**

## What this system teaches the atlas

**Chart** **delivery** **(including** **OCI** **registries)** **is** **a** **distinct** **edge** **from** **CRI** **image** **pulls** **even** **when** **the** **same** **registry** **hostname** **appears.**
