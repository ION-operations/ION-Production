# ATLAS Ontology

**Status:** DOCUMENTED (constitution of this repository)  
**Scope:** Defines the conceptual vocabulary used across packages, indexes, and graphs.

## Entity kinds

| Kind | Definition |
|------|------------|
| **System** | A bounded technical artifact or product family with identifiable interfaces, components, and lifecycle (OS kernel, service manager, orchestrator, IDE, public API surface, protocol specification). |
| **Component** | A named subsystem within a system (scheduler, VFS, control plane API server). |
| **Interface** | A contract surface: syscall ABI, IPC schema, REST/gRPC API, extension API, CLI. |
| **Artifact** | Build output or distributable (image, package, firmware). |
| **Standard** | Normative external specification (POSIX, OCI, CNI). |
| **Claim** | A single assertable statement about a system, always tagged with an evidence tier. |

## Claim classification (orthogonal to evidence tier)

- **Structural:** Components exist and connect in a described topology.  
- **Behavioral:** Observable or specified runtime behavior.  
- **Historical:** Past releases, forks, deprecations.  
- **Lineage:** Influences, forks, successors, shared DNA.  
- **Comparative:** Cross-system pattern (lives primarily under `/comparative`).

## Package boundaries

A **system package** is the unit of curatorial integrity. Cross-package pointers use `relation_types` and `relations.json`. No package may silently absorb another system’s identity.

## Provenance chain

```
Source → Excerpt/Pointer → Claim → Package section → Ledger entry
```

Every non-trivial claim should be recoverable to a ledger row or an explicit UNKNOWN/INFERRED boundary statement.

## Forbidden moves

- Collapsing DOCUMENTED and INFERRED without marking the shift.  
- Treating marketing names as architectural kinds without definition.  
- Importing unverified third-party diagrams as “architecture” without relabeling as OBSERVED (screenshot) or INFERRED.
