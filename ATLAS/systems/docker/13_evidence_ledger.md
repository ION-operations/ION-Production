---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| dkr-001 | Engine uses a daemon with documented HTTP API | DOCUMENTED | `src-docker-docs` | |
| dkr-002 | Linux containers use namespaces/cgroups | DOCUMENTED | `src-docker-docs` + kernel docs | |
| dkr-003 | OCI governs image/runtime interoperability (ecosystem) | DOCUMENTED | `std-oci` | |
| dkr-004 | Desktop macOS/Windows use VM/virtualization layers | DOCUMENTED | `src-docker-desktop` | |
| dkr-005 | AWS ECS documentation names Docker as an integrated third-party tool | DOCUMENTED | `systems/aws-ecs/sources.yaml` → `src-aws-ecs-developer-guide` | Cross-vendor citation. |
| dkr-006 | Azure Container Apps documentation names Docker Hub among container image sources | DOCUMENTED | `systems/azure-container-apps/sources.yaml` → `src-azure-container-apps-overview` | Cross-vendor citation. |
| dkr-007 | Azure Container Instances documentation names Docker Hub among image sources | DOCUMENTED | `systems/azure-aci/sources.yaml` → `src-azure-aci-overview` | Cross-vendor citation. |
