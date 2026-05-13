# Atlas V1 Preserved Content — Artifact Pack (Machine-Readable Drafts)

> **Source:** `docs/SeedOS/atlas.txt` lines 4540-7227
> **Status:** Lost in atlas_v2.md — preserved here as schema seeds
> **Disposition:** A3 Lineage Archive — feed into AETHER_INTERFACE or `schemas/` dir

---

## Overview

The Artifact Pack is the first conversion of the atlas from prose doctrine into
machine-readable YAML artifact drafts. It contains initial versions of:

1. `CANONICAL_OBJECT_REGISTRY.yaml` — all 32 canonical objects with authority/ontology class
2. `ALIASES_AND_SUPERSESSIONS.yaml` — naming history
3. `RUNTIME_TRUTH_REGISTER.yaml` — ALIVE/DEGRADED/PARTIAL/DOCTRINAL status per object
4. `EXTERNAL_TRUTH_BOUNDARY_REGISTER.yaml` — off-branch, credential, host-runtime boundaries
5. `CONTINUITY_SURFACE_REGISTER.yaml` — survival-critical data surfaces
6. `CANON_COLLISION_REGISTER.yaml` — known naming/authority conflicts
7. `ATLAS_CHANGE_LOG.yaml` — revision history
8. `ATLAS_DEBT_REGISTER.yaml` — sovereign package gaps

## Suggested File Layout (From V1)

```
atlas/
  CANONICAL_OBJECT_REGISTRY.yaml
  ALIASES_AND_SUPERSESSIONS.yaml
  RUNTIME_TRUTH_REGISTER.yaml
  EXTERNAL_TRUTH_BOUNDARY_REGISTER.yaml
  CONTINUITY_SURFACE_REGISTER.yaml
  CANON_COLLISION_REGISTER.yaml
  ATLAS_CHANGE_LOG.yaml
  ATLAS_DEBT_REGISTER.yaml

schemas/
  continuity/
    checkpoint.yaml
    capsule.yaml
    continuity_manifest.yaml
  context/
    working_context_manifest.yaml
  authority/
    authority_descriptor.yaml
  capability/
    capability_record.yaml
  sync/
    sync_manifest.yaml
  verification/
    verification_result.yaml
    witness_envelope.yaml
  plan/
    execution_gate_result.yaml
```

## Implementation Order

### First
- Add package root `CANONICAL.md` files for strong current owners
- Add `atlas/` registry files to the repo

### Second
- Create schema directories and stub files as placeholders

### Third
- Implement sovereign packages for missing owners (constitution, canon, continuity, authority, capability, sync, embodiment, improvement)

### Fourth
- Build the ingestion pipeline (governed write plane)

---

## Note on Full YAML Content

The complete YAML for all 8 registry files spans ~1,600 lines in atlas.txt (lines 4565-6120).
The full content includes detailed field definitions for all 32 canonical objects with:
- `authority_class`, `ontology_class`, `runtime_truth`
- `owned_state`, `emitted_artifacts`
- `primary_runtime_owner`, `secondary_runtime_owners`
- `dependencies` (upstream/downstream)
- `boundary_flags`, `open_gaps`

If needed, extract the raw YAML from `docs/SeedOS/atlas.txt` lines 4565-6120.

---

*This content is preserved from atlas.txt (v1) and was not fully carried into atlas_v2.md.*
*The schema stubs should inform AETHER_INTERFACE.md extensions in future phases.*
