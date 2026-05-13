---
atlas_package: system
system_slug: systemd-sysext
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# systemd system extensions (sysext)

**Kind:** **systemd** subsystem for **system extensions** — **immutable** **read-only** **images** **merged** **into** **`/usr`** **(and** **related)** **hierarchies** **via** **overlay** **semantics**, **operated** **by** **`systemd-sysext`** **and** **`systemd-sysext.service`** (`DOCUMENTED`, `src-sysext-man`, `src-sysext-service`).

## Boundaries

- **Not** **the** **full** **`systemd`** **suite** — **feature** **slice** **for** **extension** **merge** **only** (`DOCUMENTED`).  
- **Not** **`systemd-portable`** — **`portablectl`** **attaches** **portable** **service** **trees** **with** **different** **workflow** **and** **manuals** (`DOCUMENTED`).  
- **Not** **`systemd-confext`** — **`confext`** **merges** **configuration** **trees** **(`/etc`**-**class)** **per** **its** **manuals** (`DOCUMENTED`).  
- **Not** **OCI** **images** — **`oci-image-spec`** **/** **`docker`** **use** **container** **runtimes** **and** **layer** **semantics** **distinct** **from** **host** **`/usr`** **merge** (`DOCUMENTED` **contrast**).  
- **Not** **`systemd-unit-model`** **alone** — **units** **may** **live** **inside** **extensions**, **but** **grammar** **is** **the** **separate** **package** (`DOCUMENTED`).

## Why this system matters

- **Immutable** **OS** **bases** **plus** **optional** **extension** **layers** **for** **drivers,** **agents,** **or** **stacks** **without** **rebuilding** **the** **host** **image** (`DOCUMENTED` **themes**).  
- **Boot** **and** **initrd** **contexts** **can** **consume** **sysext** **where** **enabled** (`DOCUMENTED` **/** `INFERRED` **by** **distro**).

## What this system teaches the atlas

**Separate** **`systemd`** **(suite),** **`systemd-portable`** **(portable** **services),** **`systemd-sysext`** **(merged** **`/usr`** **extensions),** **and** **`systemd-unit-model`** **(unit** **grammar).**
