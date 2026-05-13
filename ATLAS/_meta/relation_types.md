# Relation Types

**Status:** DOCUMENTED

Used in `relations.json` (`type` field) and in comparative/graph notes.

| Type | Semantics |
|------|-----------|
| `influences` | Design or conceptual ancestry (may be partial). |
| `fork_of` | Repository or code lineage with identifiable fork point. |
| `implements` | Conforms to a standard or protocol (system → standard). |
| `hosts` | Runtime hosts workloads (host OS → container runtime; k8s → workload). |
| `depends_on` | Hard dependency for typical operation. |
| `integrates_with` | Common operational pairing; not a hard dependency. |
| `competes_with` | Substitutable in some deployment class. |
| `exposes_surface` | Presents API/ABI/UX to another class of actor (kernel → userspace). |
| `manages` | Control relationship (orchestrator → workload; service manager → daemon). |
| `documents` | Meta: external doc corpus primarily about target (rare). |

## Edge shape (`relations.json`)

```json
{
  "edges": [
    {
      "type": "depends_on",
      "target": "linux-kernel",
      "notes": "DOCUMENTED: runs as privileged process on Linux in typical deployments.",
      "evidence_tier": "DOCUMENTED"
    }
  ]
}
```

Required fields: `type`, `target`, `evidence_tier`.  
Optional: `notes`, `id`, `bidirectional_hint` (boolean; informational only).
