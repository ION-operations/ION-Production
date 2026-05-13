---
atlas_package: system
system_slug: centos-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# CentOS Linux — Identity

**Kind:** **Historical** **fixed**-**minor** **Linux** **distribution** **line** **in** **the** **Red** **Hat** **ecosystem**, **shipping** **`glibc`**, **`rpm`** **/** **`yum`**/**`dnf`**, **and** **`systemd`** **on** **supported** **releases**, **positioned** **as** **a** **downstream** **rebuild** **compatible** **with** **RHEL** **major**/**minor** **streams** **prior** **to** **the** **CentOS** **Stream** **pivot** **and** **documented** **EOL** **timelines** (`DOCUMENTED`, `src-centos-faq-eol`).

## Boundaries

- **Not** **`centos-stream`** **—** **rolling** **upstream** **branch** **vs** **legacy** **fixed** **minor** **lines** (`DOCUMENTED`).  
- **Not** **`rhel`** **—** **CentOS** **Linux** **was** **a** **separate** **community** **project** **without** **Red** **Hat** **subscription** **support** (`DOCUMENTED`).  
- **Not** **`red-hat-openshift`** (`DOCUMENTED`).  
- **Not** **`glibc`** **or** **`systemd`** **alone** (`DOCUMENTED`).  
- **Not** **`docker`** (`DOCUMENTED`).

## Why this system matters

- **Migration** **and** **CVE** **backport** **reasoning** **for** **remaining** **long**-**tail** **install** **bases** **and** **image** **registries** (`OBSERVED` **/** **`DOCUMENTED`** **themes**).

## What this system teaches the atlas

**Keep** **EOL** **distros** **explicit** **when** **contrasting** **rebuild** **successors** (**`rocky-linux`**, **`almalinux`**) **and** **upstream** **successors** (**`centos-stream`**).
