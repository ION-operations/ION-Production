---
atlas_package: system
system_slug: argo-cd
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: B
---

# Argo CD — Identity

**Kind:** **Declarative,** **GitOps** **continuous** **delivery** **tool** **for** **Kubernetes** **that** **reconciles** **desired** **application** **state** **from** **Git** **(and** **other** **sources)** **into** **the** **cluster** (`DOCUMENTED`, `src-argo-cd-docs`, `src-argo-cd-github`).

## Boundaries

- **Not** **`kubernetes`** **itself** **—** **Argo** **CD** **is** **controllers** **+** **UI/CLI** **that** **drive** **the** **Kubernetes** **API.**  
- **Not** **`helm`** **alone** **—** **Helm** **is** **a** **packaging** **tool;** **Argo** **CD** **is** **a** **delivery** **controller** **that** **can** **consume** **Helm** **among** **other** **source** **types.**  
- **Not** **`fluxcd`** **as** **the** **same** **implementation** **—** **both** **are** **GitOps** **controllers** **with** **different** **projects** **and** **surfaces.**

## Why this system matters

- **Provides** **a** **second** **major** **CNCF** **GitOps** **reference** **pattern** **alongside** **Flux** **for** **explicit** **comparison** **of** **delivery** **controllers.**

## What this system teaches the atlas

**“GitOps”** **is** **not** **one** **slug** **—** **name** **the** **controller** **and** **its** **source** **/** **sync** **model.**
