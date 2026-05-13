---
atlas_package: system
system_slug: ubuntu
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **kernel** **packages** (`DOCUMENTED`).  
- **`fork_of` `debian`:** **derivative** **distribution** **model** **with** **shared** **`dpkg`**/**`apt`** **heritage** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **glibc** **userland** **and** **systemd** **PID** **1** **on** **default** **installs** (`DOCUMENTED`).  
- **`integrates_with` `docker` / `oci-image-spec`:** **pervasive** **`ubuntu`** **OCI** **bases** (`OBSERVED` **+** **`DOCUMENTED`**).  
- **`competes_with` `alpine-linux`:** **glibc**+**systemd** **vs** **musl**+**OpenRC** **defaults** **for** **image** **/** **node** **choices** (`INFERRED`).
