---
atlas_package: system
system_slug: systemd-sysext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `systemd`:** **implemented** **by** **the** **systemd** **suite** (`DOCUMENTED`).  
- **`integrates_with` `systemd-unit-model`:** **units** **may** **ship** **inside** **extensions** (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** **overlayfs** **and** **mount** **primitives** (`DOCUMENTED`).  
- **`competes_with` `docker` / `oci-image-spec`:** **host** **`/usr`** **merge** **vs** **container** **image** **delivery** (`INFERRED`).  
- **`integrates_with` `systemd-confext`:** **sibling** **extension** **merge** **for** **`/etc`**-**class** **trees** (`DOCUMENTED`).
