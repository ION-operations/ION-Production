---
atlas_package: system
system_slug: linux-overlayfs
schema_version: "1.0"
last_reviewed: "2026-04-23"
evidence_grade: B
---

# Linux OverlayFS — Identity

**Kind:** **Linux** **kernel** **union** **filesystem** **(OverlayFS)** **stacking** **a** **read-only** **“lower”** **tree** **with** **a** **read-write** **“upper”** **and** **exposing** **a** **merged** **view** **per** **documented** **kernel** **semantics** (`DOCUMENTED`, `src-linux-overlayfs-kernel-docs`).

## Boundaries

- **Not** **`oci-image-spec`** **—** **that** **specifies** **image** **layer** **manifests** **and** **layout;** **OverlayFS** **is** **a** **kernel** **driver** **for** **mounting** **union** **views** (`DOCUMENTED` **boundary**).  
- **Not** **`docker`** **or** **`containerd`** **by** **themselves** **—** **those** **are** **engines/runtimes** **that** **may** **use** **overlay** **mounts** **on** **Linux**.  
- **Not** **`linux-namespaces`** **—** **mount** **namespaces** **change** **what** **mounts** **are** **visible;** **OverlayFS** **is** **a** **filesystem** **implementation** **choice** **inside** **a** **mount**.

## Why this system matters

- **Explains** **how** **container** **image** **layers** **are** **often** **materialized** **as** **overlay** **mounts** **without** **conflating** **manifest** **law** **with** **VFS** **behavior**.

## What this system teaches the atlas

**Separate** **kernel** **union** **mount** **mechanics** **from** **OCI** **image** **format** **and** **from** **runtime** **process** **lifecycle.**
