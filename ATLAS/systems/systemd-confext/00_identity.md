---
atlas_package: system
system_slug: systemd-confext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# systemd configuration extensions (confext)

**Kind:** **systemd** subsystem for **configuration** **extensions** — **immutable** **read-only** **images** **merged** **into** **`/etc`** **(and** **related** **configuration** **hierarchies)** **via** **overlay** **semantics**, **operated** **by** **`systemd-confext`** **and** **`systemd-confext.service`** (`DOCUMENTED`, `src-confext-man`, `src-confext-service`).

## Boundaries

- **Not** **the** **full** **`systemd`** **suite** — **feature** **slice** **for** **config** **merge** **only** (`DOCUMENTED`).  
- **Not** **`systemd-sysext`** — **`sysext`** **targets** **`/usr`**-**class** **trees** **per** **its** **manuals**; **`confext`** **targets** **configuration** **trees** (`DOCUMENTED`).  
- **Not** **`systemd-portable`** — **`portablectl`** **workflow** **is** **distinct** (`DOCUMENTED`).  
- **Not** **OCI** **/** **`docker`** **container** **roots** — **different** **delivery** **and** **runtime** **model** (`DOCUMENTED` **contrast**).

## Why this system matters

- **Immutable** **base** **images** **plus** **layered** **configuration** **without** **mutating** **the** **base** **`/etc`** **directly** (`DOCUMENTED` **themes**).  
- **Pairs** **with** **`systemd-sysext`** **in** **extension**-**heavy** **Linux** **distro** **designs** (`INFERRED` **field** **pattern**).

## What this system teaches the atlas

**Split** **`systemd-sysext`** **(system** **/** **`/usr`)** **from** **`systemd-confext`** **(configuration** **/** **`/etc`)** **—** **same** **family,** **different** **merge** **roots** **and** **manuals.**
