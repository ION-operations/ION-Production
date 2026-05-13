---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# BuildKit — Identity

**Kind:** **OCI-oriented** **container** **image** **build** **engine** **(DAG** **frontend,** **cacheable** **llb,** **export/push)** **from** **the** **Moby** **ecosystem,** **commonly** **deployed** **as** **`buildkitd`** (`DOCUMENTED`, `src-buildkit-docs`, `src-buildkit-github`).

## Boundaries

- **Not** **`oci-runtime-spec`** **—** **BuildKit** **produces** **images** **and** **layers;** **it** **does** **not** **define** **the** **runtime** **bundle** **execution** **contract.**  
- **Not** **`runc`** **—** **low-level** **OCI** **runtimes** **execute** **bundles;** **BuildKit** **builds** **artifacts** **that** **later** **feed** **CRI/containerd** **paths.**  
- **Not** **`oci-image-spec`** **alone** **—** **the** **spec** **is** **format** **law;** **BuildKit** **is** **an** **implementation** **that** **emits** **conforming** **manifests** **and** **blobs.**

## Why this system matters

- **Separates** **“build** **graph** **/** **cache”** **from** **“run** **bundle”** **in** **the** **OCI** **mental** **model** **—** **both** **are** **required** **for** **end-to-end** **containers.**

## What this system teaches the atlas

**Treat** **image** **construction** **and** **workload** **execution** **as** **different** **relation** **targets** **even** **when** **the** **same** **vendor** **ships** **both** **tools.**
