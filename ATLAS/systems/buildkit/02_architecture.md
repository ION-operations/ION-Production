---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Architecture

- **Frontend** **(Dockerfile/LLB)** **→** **solver** **/** **cache** **→** **worker** **execution** **→** **exporter** **(OCI** **tar,** **registry** **push)** **per** **upstream** **architecture** **docs** (`DOCUMENTED`, `src-buildkit-docs`).  
- **Contrasts** **with** **kubelet/CRI** **execution** **paths** **that** **consume** **finished** **images** **rather** **than** **authoring** **layers** (`INFERRED` **comparative**).
