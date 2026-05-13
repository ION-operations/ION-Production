---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** KVM path (`DOCUMENTED`).  
- **`integrates_with` `kubernetes`:** via higher-level runtimes/stacks (`INFERRED`).  
- **`competes_with` `docker`:** only in the weak sense of isolation mechanism tradeoffs (`INFERRED`).
