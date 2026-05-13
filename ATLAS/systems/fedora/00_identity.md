---
atlas_package: system
system_slug: fedora
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Fedora — Identity

**Kind:** **Community** **Linux** **distribution** **shipping** **`glibc`** **and** **GNU** **toolchain**-**class** **userlands** **on** **supported** **architectures**, **`rpm`** **/** **`dnf`** **packaging**, **and** **`systemd`** **as** **the** **default** **init** **/** **service** **manager** **on** **current** **releases** (`DOCUMENTED`, `src-fedora-releases`, `src-fedora-systemd-quick-docs`).

## Boundaries

- **Not** **`linux-kernel`** — **Fedora** **packages** **upstream** **kernels** **with** **distribution** **patches** (`DOCUMENTED`).  
- **Not** **`red-hat-openshift`** **or** **enterprise** **RHEL** **—** **this** **package** **is** **the** **Fedora** **Project** **distro** **grain** **only** (`DOCUMENTED`).  
- **Not** **`glibc`** **or** **`systemd`** **alone** — **those** **are** **separate** **ATLAS** **packages** **consumed** **by** **the** **distro** (`DOCUMENTED`).  
- **Not** **`docker`** — **Fedora** **is** **a** **common** **host** **and** **OCI** **base** **userland**, **not** **the** **container** **engine** (`DOCUMENTED`).

## Why this system matters

- **Reference** **rpm**/**dnf**+**glibc**+**systemd** **field** **pattern** **contrasting** **`dpkg`**/**`apt`** **(Debian** **line)** **and** **`musl`** **/** **`alpine-linux`** (`DOCUMENTED` **/** `OBSERVED`).  
- **Upstream** **innovation** **feeder** **for** **RHEL**-**family** **products** **—** **policy** **and** **SELinux** **defaults** **matter** **for** **supply** **chain** **and** **hardening** **surveys** (`DOCUMENTED` **themes**).

## What this system teaches the atlas

**Model** **`linux-distribution`** **separately** **for** **rpm**/**dnf** **vs** **`dpkg`**/**`apt`** **packaging** **law** **when** **reasoning** **about** **images,** **nodes,** **and** **toolchain** **bootstrap.**
