---
atlas_package: system
system_slug: linux-capabilities
schema_version: "1.0"
last_reviewed: "2026-04-22"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **capability** **credential** **model** (`DOCUMENTED`).  
- **`integrates_with` `linux-namespaces` + `linux-cgroups` + container** **stack** **(INFERRED):** **composed** **hardening** **on** **Linux** — **capabilities** **are** **not** **namespaces** **or** **cgroups**.  
- **`integrates_with` `linux-security-modules`:** **LSM** **policy** **layers** **with** **capability** **checks** (`INFERRED`).
