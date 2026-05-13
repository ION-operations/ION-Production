---
atlas_package: system
system_slug: debian
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **kernel** **packages** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **glibc** **userland** **and** **systemd** **PID** **1** **on** **current** **stable** (`DOCUMENTED`).  
- **`integrates_with` `docker` / `oci-image-spec`:** **pervasive** **`debian`** **OCI** **bases** (`OBSERVED` **+** **`DOCUMENTED`**).  
- **`competes_with` `alpine-linux`:** **glibc**+**systemd** **vs** **musl**+**OpenRC** **defaults** **for** **image** **/** **node** **choices** (`INFERRED`).  
- **`influences` `ubuntu`:** **Debian**-**derived** **distribution** **with** **distinct** **governance** **and** **release** **cadence** (`DOCUMENTED`).
