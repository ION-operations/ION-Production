---
atlas_package: system
system_slug: rhel
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Red Hat Enterprise Linux — Identity

**Kind:** **Enterprise** **Linux** **distribution** **shipping** **`glibc`** **and** **GNU** **toolchain**-**class** **userlands** **on** **supported** **architectures**, **`rpm`** **/** **`dnf`** **/** **`yum`**-**class** **packaging**, **and** **`systemd`** **as** **the** **default** **init** **/** **service** **manager** **on** **supported** **releases** (`DOCUMENTED`, `src-rhel-product`, `src-rhel-systemd-admin`).

## Boundaries

- **Not** **`linux-kernel`** — **RHEL** **ships** **maintained** **kernel** **streams** **with** **distribution** **and** **vendor** **support** **policy** (`DOCUMENTED`).  
- **Not** **`fedora`** **—** **RHEL** **is** **a** **separate** **subscription** **/** **support** **product** **with** **longer** **life** **cycles** **while** **sharing** **technology** **heritage** **with** **Fedora** (`DOCUMENTED`).  
- **Not** **`red-hat-openshift`** — **OpenShift** **is** **a** **Kubernetes** **platform** **that** **typically** **runs** **on** **RHEL** **nodes** (`DOCUMENTED`).  
- **Not** **`glibc`** **or** **`systemd`** **alone** — **those** **are** **separate** **ATLAS** **packages** (`DOCUMENTED`).  
- **Not** **`docker`** — **RHEL** **is** **a** **host** **and** **image** **base** **userland**; **container** **engines** **are** **separate** (`DOCUMENTED`).

## Why this system matters

- **Default** **enterprise** **glibc**+**systemd**+**SELinux**-**heavy** **node** **pattern** **for** **OpenShift** **and** **regulated** **datacenters** (`DOCUMENTED` **themes**).  
- **Subscription** **and** **errata** **policy** **(ESA** **/** **life** **cycle)** **shape** **patch** **and** **compliance** **audits** (`DOCUMENTED`).

## What this system teaches the atlas

**Keep** **`rhel`** **distinct** **from** **`fedora`** **(cadence** **/** **support)** **and** **from** **`red-hat-openshift`** **(distro** **vs** **K8s** **platform).**
