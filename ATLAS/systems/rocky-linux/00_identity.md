---
atlas_package: system
system_slug: rocky-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Rocky Linux — Identity

**Kind:** **Community** **enterprise** **Linux** **distribution** **shipping** **`glibc`** **and** **GNU** **toolchain**-**class** **userlands**, **`rpm`** **/** **`dnf`** **packaging**, **and** **`systemd`** **as** **the** **default** **init** **/** **service** **manager**, **positioned** **as** **a** **downstream** **rebuild** **aligned** **with** **RHEL** **major** **/** **minor** **streams** (`DOCUMENTED`, `src-rocky-about`).

## Boundaries

- **Not** **`rhel`** **—** **Rocky** **is** **a** **separate** **project** **without** **Red** **Hat** **subscription** **entitlements** (`DOCUMENTED`).  
- **Not** **`red-hat-openshift`** **—** **OpenShift** **product** **grain** **is** **separate** **(often** **RHEL**-**backed)** (`DOCUMENTED`).  
- **Not** **`glibc`** **or** **`systemd`** **alone** (`DOCUMENTED`).  
- **Not** **`docker`** (`DOCUMENTED`).

## Why this system matters

- **Common** **subscription**-**free** **RHEL**-**compatible** **server** **and** **cloud** **image** **choice** **alongside** **`almalinux`** (`OBSERVED` **/** **`DOCUMENTED`** **themes**).

## What this system teaches the atlas

**Model** **RHEL**-**compatible** **rebuilds** **separately** **from** **`rhel`** **and** **from** **each** **other** **when** **reasoning** **about** **support** **/** **governance.**
