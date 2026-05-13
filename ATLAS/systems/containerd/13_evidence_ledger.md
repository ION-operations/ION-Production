---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| ctrd-001 | containerd provides a CRI implementation for Kubernetes | DOCUMENTED | `src-containerd-docs`, `src-k8s-cri` | |
| ctrd-002 | Daemon exposes gRPC API for clients | DOCUMENTED | `src-containerd-docs` | |
| ctrd-003 | containerd was contributed to CNCF as Docker-extracted runtime (2017) | HISTORICAL | `src-cncf-containerd-donation` | Docker blog also announced; optional secondary |
