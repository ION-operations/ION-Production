---
atlas_package: system
system_slug: fedora
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **kernel** **packages** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **glibc** **userland** **and** **systemd** **PID** **1** **on** **default** **installs** (`DOCUMENTED`).  
- **`integrates_with` `docker` / `oci-image-spec`:** **common** **`fedora`** **OCI** **bases** (`OBSERVED` **+** **`DOCUMENTED`**).  
- **`competes_with` `alpine-linux`:** **glibc**+**systemd** **vs** **musl**+**OpenRC** **defaults** **for** **image** **/** **node** **choices** (`INFERRED`).  
- **`influences` `centos-stream`:** **documented** **ecosystem** **pipeline** **into** **the** **public** **RHEL** **upstream** **branch** (`DOCUMENTED`).  
- **`influences` `rhel`:** **technology** **feeder** **into** **enterprise** **RHEL** **streams** **with** **separate** **support** **policy** (`DOCUMENTED`).
