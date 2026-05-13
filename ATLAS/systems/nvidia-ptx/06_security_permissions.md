---
atlas_package: system
system_slug: nvidia-ptx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Driver trust

**GPU** **code** **execution** **is** **driver**-**mediated** — **trust** **model** **is** **platform** **/** **API** (`DOCUMENTED` CUDA security docs when load-bearing).

## Untrusted PTX

**Not** **a** **typical** **threat** **model** **surface** **like** **web** **shaders** — **context**-**dependent** (`INFERRED`).
