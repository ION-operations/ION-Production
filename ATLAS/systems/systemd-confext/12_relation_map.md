---
atlas_package: system
system_slug: systemd-confext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `systemd`:** **suite** **component** (`DOCUMENTED`).  
- **`integrates_with` `systemd-sysext`:** **sibling** **extension** **merge** **mechanism** **for** **different** **roots** (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** **overlay** **mount** **primitives** (`DOCUMENTED`).  
- **`competes_with` `docker` / `oci-image-spec`:** **host** **config** **merge** **vs** **container** **image** **delivery** (`INFERRED`).
