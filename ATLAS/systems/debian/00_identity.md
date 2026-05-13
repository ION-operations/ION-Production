---
atlas_package: system
system_slug: debian
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Debian — Identity

**Kind:** **Community** **Linux** **distribution** **shipping** **`glibc`** **and** **GNU** **toolchain**-**class** **userlands** **on** **supported** **architectures**, **`dpkg`** **/** **`apt`** **packaging**, **and** **`systemd`** **as** **the** **default** **init** **on** **current** **stable** **releases** (`DOCUMENTED`, `src-debian-releases`, `src-debian-systemd-wiki`).

## Boundaries

- **Not** **`linux-kernel`** — **Debian** **packages** **upstream** **kernels** **and** **maintains** **patches** **in** **distribution** **trees** (`DOCUMENTED`).  
- **Not** **`glibc`** **or** **`systemd`** **alone** — **those** **are** **separate** **ATLAS** **packages** **consumed** **by** **the** **distro** (`DOCUMENTED`).  
- **Not** **`docker`** — **Debian** **is** **a** **common** **host** **and** **OCI** **base** **userland**, **not** **the** **container** **engine** (`DOCUMENTED`).

## Why this system matters

- **Reference** **glibc** **+** **`systemd`** **field** **pattern** **for** **servers** **and** **cloud** **images** **contrasting** **`musl`** **/** **`alpine-linux`** (`DOCUMENTED` **/** `OBSERVED`).  
- **Upstream** **for** **many** **derivatives** **(Ubuntu,** **etc.)** **—** **policy** **and** **packaging** **law** **matter** **for** **supply** **chain** **audits** (`DOCUMENTED` **themes**).

## What this system teaches the atlas

**Model** **`linux-distribution`** **separately** **for** **glibc-centric** **vs** **musl-centric** **defaults** **when** **reasoning** **about** **ABI,** **images,** **and** **node** **OS** **choices.**
