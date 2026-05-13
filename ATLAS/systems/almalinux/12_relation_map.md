---
atlas_package: system
system_slug: almalinux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **kernel** **packages** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **userland** **and** **PID** **1** (`DOCUMENTED`).  
- **`rhel` `influences` `almalinux`:** **documented** **downstream** **alignment** **with** **RHEL** **streams** **(separate** **governance)** (`DOCUMENTED`).  
- **`competes_with` `rocky-linux`:** **substitutable** **RHEL**-**compatible** **rebuild** (`INFERRED`).  
- **`competes_with` `alpine-linux`:** **glibc**/**systemd** **vs** **musl**/**OpenRC** (`INFERRED`).
