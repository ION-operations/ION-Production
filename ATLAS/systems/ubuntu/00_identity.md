---
atlas_package: system
system_slug: ubuntu
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Ubuntu — Identity

**Kind:** **Debian**-**derived** **Linux** **distribution** **shipping** **`glibc`** **and** **GNU** **toolchain**-**class** **userlands** **on** **supported** **architectures**, **`dpkg`** **/** **`apt`** **packaging**, **and** **`systemd`** **as** **the** **default** **init** **/** **service** **manager** **on** **current** **releases** (`DOCUMENTED`, `src-ubuntu-release-cycle`, `src-ubuntu-server-systemd`).

## Boundaries

- **Not** **`linux-kernel`** — **Ubuntu** **packages** **upstream** **kernels** **with** **distribution** **patches** (`DOCUMENTED`).  
- **Not** **`debian`** **alone** — **Ubuntu** **is** **a** **separate** **governance** **and** **release** **cadence** **while** **sharing** **packaging** **heritage** (`DOCUMENTED`).  
- **Not** **`glibc`** **or** **`systemd`** **alone** — **those** **are** **separate** **ATLAS** **packages** **consumed** **by** **the** **distro** (`DOCUMENTED`).  
- **Not** **`docker`** — **Ubuntu** **is** **a** **common** **host** **and** **OCI** **base** **userland**, **not** **the** **container** **engine** (`DOCUMENTED`).

## Why this system matters

- **Dominant** **cloud** **/** **CI** **/** **desktop** **glibc**+**systemd** **field** **pattern** **alongside** **`debian`** **bases** (`OBSERVED` **/** **`DOCUMENTED`** **themes**).  
- **Derivative** **lineage** **from** **`debian`** **must** **stay** **explicit** **when** **auditing** **supply** **chain** **and** **CVE** **backport** **policy** (`DOCUMENTED`).

## What this system teaches the atlas

**Keep** **`fork_of`** **`debian`** **distinct** **from** **collapsing** **Ubuntu** **into** **`debian`** **—** **policy,** **cadence,** **and** **image** **defaults** **differ.**
