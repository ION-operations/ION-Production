---
atlas_package: system
system_slug: centos-stream
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **kernel** **packages** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **userland** **and** **PID** **1** (`DOCUMENTED`).  
- **`fedora` `influences` `centos-stream`:** **documented** **ecosystem** **pipeline** **themes** (`DOCUMENTED`).  
- **`influences` `rhel`:** **documented** **upstream** **development** **branch** **for** **RHEL** **minor** **streams** (`DOCUMENTED`).  
- **`competes_with` `alpine-linux`:** **glibc**/**systemd** **vs** **musl**/**OpenRC** (`INFERRED`).
