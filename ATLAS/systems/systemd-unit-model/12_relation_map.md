---
atlas_package: system
system_slug: systemd-unit-model
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `systemd`:** this package is the **documented unit grammar** consumed by the **systemd** suite (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** directives express cgroup/namespace **intent** enforced with the kernel (`DOCUMENTED` / `INFERRED`).  
- **`integrates_with` `systemd-boot` / `unified-kernel-image`:** boot flow **targets** and **generators** interact at OS image boundary (`INFERRED`).
