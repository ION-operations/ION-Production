---
atlas_package: system
system_slug: rhel
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **supported** **kernel** **streams** (`DOCUMENTED`).  
- **`integrates_with` `glibc` / `systemd`:** **default** **glibc** **userland** **and** **systemd** **PID** **1** **on** **default** **installs** (`DOCUMENTED`).  
- **`integrates_with` `red-hat-openshift`:** **documented** **platform** **/** **node** **OS** **pairing** **for** **OpenShift** **Container** **Platform** (`DOCUMENTED`).  
- **`integrates_with` `docker` / `oci-image-spec`:** **UBI** **/** **vendor** **RHEL**-**class** **OCI** **bases** (`OBSERVED` **+** **`DOCUMENTED`**).  
- **`competes_with` `alpine-linux`:** **glibc**+**systemd** **enterprise** **vs** **musl**+**OpenRC** **defaults** **for** **image** **/** **node** **choices** (`INFERRED`).  
- **`centos-stream` `influences` `rhel`:** **documented** **upstream** **development** **branch** **for** **RHEL** **minor** **streams** (`DOCUMENTED`).  
- **`influences` `rocky-linux` / `almalinux`:** **RHEL**-**stream** **alignment** **for** **community** **rebuild** **distros** **with** **separate** **governance** (`DOCUMENTED`).  
- **`influences` `centos-linux`:** **historical** **RHEL**-**compatible** **fixed**-**minor** **rebuild** **line** **prior** **to** **the** **CentOS** **Stream** **pivot** (`DOCUMENTED`).  
