---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Relation map (narrative)

- **Hosts `systemd`:** typical PID 1 pairing on major distros (`DOCUMENTED` deployment pattern).  
- **Hosts `docker`:** namespaces/cgroups substrate (`DOCUMENTED`).  
- **Influences `android-aosp`:** device kernel lineage (`DOCUMENTED` pending AOSP package depth).  
- **Competes with `windows-nt`:** deployment substitution (`INFERRED` edge note).
