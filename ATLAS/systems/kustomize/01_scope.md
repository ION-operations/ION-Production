---
atlas_package: system
system_slug: kustomize
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Scope

## In scope

- **`kustomization.yaml`** **schema,** **bases/overlays,** **patches,** **images,** **configMapGenerator,** **and** **`kubectl`** **-k** **integration** (`DOCUMENTED`).  
- **Composition** **with** **Helm** **post-render** **and** **GitOps** **controllers** **at** **survey** **grain** (`DOCUMENTED`/`INFERRED`).

## Out of scope

- **Every** **third-party** **Kustomize** **plugin** **unless** **ledgered.**  
- **Non-Kubernetes** **targets.**

## Versioning note

**Kustomize** **is** **versioned** **with** **`kubectl`** **and** **standalone** **releases** **per** **upstream** **release** **notes** (`DOCUMENTED`).
