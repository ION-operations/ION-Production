---
atlas_package: system
system_slug: alpine-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Alpine Linux — Identity

**Kind:** **Minimal** **Linux** **distribution** **shipping** **`musl`** **as** **the** **default** **C** **library** **on** **supported** **architectures**, **`apk`** **packages**, **and** **OpenRC** **as** **the** **default** **init** **system** **in** **mainline** **releases** (`DOCUMENTED`, `src-alpine-about`, `src-alpine-wiki-musl`).

## Boundaries

- **Not** **`linux-kernel`** — **Alpine** **consumes** **upstream** **kernels** **via** **packaging** (`DOCUMENTED`).  
- **Not** **`musl`** **alone** — **the** **libc** **implementation** **is** **a** **separate** **ATLAS** **package** (`DOCUMENTED`).  
- **Not** **`docker`** — **Alpine** **is** **often** **used** **as** **a** **container** **base** **image** **OS** **userland**, **not** **the** **container** **engine** (`DOCUMENTED`).

## Why this system matters

- **Ubiquitous** **OCI** **image** **base** **for** **small** **footprint** **and** **`musl`** **ABI** (`OBSERVED` **field** **+** **`DOCUMENTED`** **musl** **story**).  
- **Contrasts** **with** **glibc-centric** **distros** **on** **linking** **and** **debugging** **assumptions** (`INFERRED` **ops** **theme**).

## What this system teaches the atlas

**Separate** **distro** **policy** **(`linux-distribution`)** **from** **kernel** **and** **from** **libc** **when** **auditing** **container** **bases** **and** **cross-build** **sysroots.**
