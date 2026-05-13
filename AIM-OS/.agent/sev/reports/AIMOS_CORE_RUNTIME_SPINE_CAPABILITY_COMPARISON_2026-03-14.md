# AIMOS Core Runtime Spine Capability Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_11_2026-03-14`
Status: evidence-only comparative capability analysis

## Comparative Table

| Comparison axis | `packages/cmc_service/` | `packages/hhni/` | `packages/seg/` | `packages/vif/` | `packages/apoe/` | `packages/sdfcvf/` |
| --- | --- | --- | --- | --- | --- | --- |
| Memory or state role | Strongest state substrate: atom storage, snapshots, bitemporal queries, and durable memory persistence | Secondary state role through retrieval indexes, search state, and retrieval budgets rather than primary persistence | Graph-state layer for entities, relations, evidence, and lineage over time | Witness and confidence state layer rather than general memory storage | Plan and execution state layer for workflows, budgets, gates, and step progress | Validation-state layer for parity scores, gate results, blast radius, and DORA metrics |
| Retrieval or graph role | Supports retrieval indirectly as the memory base HHNI and others consume | Strongest retrieval and indexing surface in the cluster | Strongest evidence-graph and contradiction-aware synthesis surface in the cluster | Uses retrieval context and graph context to qualify confidence, but is not the main retrieval or graph engine | Uses retrieval roles and graph/trust integrations, but is not itself the main retrieval or graph surface | Uses retrieval and graph integrations only to support parity/quality calculations |
| Planning or execution role | Provides memory substrate for execution context, but does not own plan execution | Supplies context to planners and executors via retrieval | Supplies evidence structure for downstream synthesis and reasoning, but not direct orchestration | Supplies abstention and replay hooks around execution, but not the orchestration engine itself | Strongest planning and execution surface in the cluster | Supplies quality gates to execution, but not the core planner or executor |
| Verification or confidence role | Stores witness stubs and history, but is not the primary confidence or gate engine | Retrieval quality matters, but confidence and gates are secondary here | Contradiction detection and provenance help evidence quality, but not the main confidence system | Strongest confidence, provenance, calibration, replay, and kappa-gating surface in the cluster | Provides execution gates and witness hooks, but leans on VIF and SDF-CVF for deeper trust or parity semantics | Strongest parity, blast-radius, and quality-gate surface for change validation in the cluster |
| Dependency centrality | Highest visible centrality with `13` dependents | Very high centrality with `11` dependents | High centrality with `10` dependents | High centrality with `9` dependents and multiple outward dependencies into the same spine | Mid-level centrality with `5` dependents | Lower centrality with `4` dependents, but still reused by execution and confidence surfaces |
| Current live vs degraded reading | `alive` in prior runtime truth | `degraded`: package works, runtime bridge still uninitialized | `live`, but current runtime graph content was empty in the bounded probe | `degraded`: tooling works, operational evidence remains weak | `live` in bounded checks | `live` in repo-local parity verification |

## Direct Comparative Reading

### `cmc_service` vs `hhni` vs `seg`

- `cmc_service` is the strongest persistence and bitemporal memory base.
- `hhni` is the strongest retrieval and indexing layer.
- `seg` is the strongest evidence-graph and contradiction-aware synthesis layer.

### `vif` vs `sdfcvf`

- `vif` owns uncertainty, provenance, replay, and abstention logic.
- `sdfcvf` owns parity, blast-radius, and validation-gate logic around change quality.

### `apoe` vs the rest of the spine

- `apoe` is the strongest execution and orchestration surface.
- It sits on top of memory, retrieval, graph, confidence, and parity primitives rather than replacing them.

## Net Comparative Answer

1. `cmc_service` anchors state.
2. `hhni` anchors retrieval.
3. `seg` anchors evidence graph and synthesis structure.
4. `vif` anchors provenance and confidence.
5. `apoe` anchors orchestration and executable planning.
6. `sdfcvf` anchors parity and validation math.

These are comparative role answers only. They do not declare a single master core or propose remediation.
