# ION Runtime — System Summary

> **Source:** `operation-victus/victus/ion/` (103 Python files, 19MB)
> **Status:** Partially functional — bootstrap hangs, data/ions/ missing
> **Authority:** A4_RUNTIME

## What ION Is

ION is the cognitive filesystem — the core runtime that manages knowledge as typed, bonded, governed objects called **ions**. It implements the Aether Constitution's rules in code.

## Core Components

| Module | Lines | Role |
|--------|-------|------|
| **model.py** | ~800 | Ion data model: 14 types, 8 authority classes, 5 gate classes, CapsulePhase, AgentRole, Priority, Provenance |
| **governed_write.py** | 444 | 10-stage validation pipeline (W1-W10). No ion enters the network unvalidated. |
| **navigator.py** | 625 | §7 cognitive loop: contextualize→reflect→plan→gate→execute→audit→deliver. LLM augments §7.2, §7.3, §7.6. |
| **context_compiler.py** | 446 | Three-tier context: Pinned (A0-A1 always), Working (budget-managed), Long-term (summary only). Per-cognitive-step compilation. |
| **context.py** | 100 | BFS radial context assembly from ion graph. |
| **capsule.py** | 245 | PRE/POST capsule lifecycle via GovernedWritePipeline. |
| **manifest.py** | ~300 | ManifestManager: loop position, active/future branches, evidence trail, system confidence. |
| **graph.py** | ~200 | IonGraph: NetworkX topology, predecessors/successors, bond queries. |
| **index.py** | ~400 | IonIndex: all_ions(), stale_ions(), low_confidence_ions(), ions_by_type(). |
| **store.py** | ~300 | IonStore: CRUD for ions on filesystem with YAML frontmatter. |
| **threshold.py** | ~200 | ThresholdEvaluator: gate condition evaluation. |

## Known Issues
1. **Bootstrap hang** — `bootstrap.py` singleton bridge import chain
2. **Missing data/ions/** — no seed ions on disk
3. **~20 legacy enum refs** — pre-V5 naming
4. **LLM adapter not wired** — AetherEngine exists but can't call LLMs

## Integration Points
- Workspace sections map to ion types (see AIMOS_CONTEXT_INTEGRATION.md)
- Navigator produces CognitiveContext/ReflectionResult/ExecutionPlan/AuditResult
- GovernedWrite enforces authority permissions (braden=ALL, executive=A2+, standard=A4+)
