---
atlas_package: system
system_slug: azure-container-apps
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| aca-001 | Container Apps is a serverless platform for containerized applications | DOCUMENTED | `src-azure-container-apps-overview` | |
| aca-002 | Scaling can use KEDA-supported scalers | DOCUMENTED | `src-azure-container-apps-overview` | |
| aca-003 | Powered by Kubernetes; no direct Kubernetes API access; use AKS for full API | DOCUMENTED | `src-azure-container-apps-compare` | |
| aca-004 | Supports Kubernetes-style apps (service discovery, traffic splitting) | DOCUMENTED | `src-azure-container-apps-compare` | |
| aca-005 | Run containers from public/private registries including Docker Hub and ACR | DOCUMENTED | `src-azure-container-apps-overview` | |
| aca-006 | Substitutable with ACI for lower-level Azure container hosting | INFERRED | `relations.json` → `competes_with` azure-aci | Microsoft positions ACI as building block in compare article. |
