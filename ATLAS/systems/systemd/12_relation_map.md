---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** cgroups, namespaces, syscalls (`DOCUMENTED`).  
- **`integrates_with` `docker`:** host daemon often a systemd service (`DOCUMENTED` common pattern).  
- **`manages` `kubernetes`:** optional — kubelet as systemd unit (`INFERRED` operational).
