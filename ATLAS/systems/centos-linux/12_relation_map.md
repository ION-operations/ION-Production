---
atlas_package: system
system_slug: centos-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **shipped** **kernel** **packages** **on** **supported** **releases** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **userland** **and** **PID** **1** **where** **systemd** **applied** (`DOCUMENTED`).  
- **`rhel` `influences` `centos-linux`:** **documented** **downstream** **RHEL**-**compatible** **rebuild** **heritage** (`DOCUMENTED`).  
- **`competes_with` `rocky-linux` / `almalinux`:** **substitutable** **successor** **rebuild** **choices** **post**-**EOL** (`INFERRED`).  
- **`competes_with` `alpine-linux`:** **glibc**/**systemd** **vs** **musl**/**OpenRC** (`INFERRED`).  
- **Not** **`centos-stream`:** **fixed** **minor** **EOL** **line** **vs** **rolling** **upstream** **branch** (`DOCUMENTED`).
