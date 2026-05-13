# AIM-OS Core System Live Verification Card

Work package: `CONSOLIDATION_WORK_PACKAGE_03_2026-03-13`

This card records bounded local verification only. It does not make remediation or architecture decisions.

| System | Direct evidence path | Verification method used | Result | Observed note |
| --- | --- | --- | --- | --- |
| APOE | `packages/apoe/__init__.py`<br>`packages/apoe/acl_parser.py`<br>`packages/apoe/tests/test_acl_parser.py` | Package-native smoke probe using `ACLParser.parse(...)` on a one-step ACL plan; MCP `create_plan` tool-path probe | `live` | Package-native probe parsed `test_plan` with role `validator` and 1 step. MCP `create_plan` returned success and generated plan `plan_995c33dd`. |
| SEG | `packages/seg/__init__.py`<br>`packages/seg/seg_graph.py`<br>`packages/seg/tests/test_seg_graph.py` | Package-native smoke probe using `SEGraph.add_entity(...)`; MCP `synthesize_knowledge` tool-path probe via HTTP bridge | `live` | Package-native probe added 1 entity. MCP `synthesize_knowledge` returned success for 3 topics, with 0 entities and 0 relations in the current runtime graph. |
| SIS | `packages/sis/__init__.py`<br>`packages/sis/sis_core.py`<br>`packages/sis/tests/test_sis_core.py` | Import-time package-native probe plus static import/path check | `unavailable` | Import failed immediately with `No module named 'sis.system_usage_auditor'`. `__init__.py` and `sis_core.py` reference five submodules that are not present on disk. |
| SDF-CVF | `packages/sdfcvf/parity.py`<br>`packages/sdfcvf/tests/test_parity.py` | Package-native smoke probe using `calculate_parity(...)` on a workspace-local quartet | `live` | Repo-local parity probe returned `parity_score=1.0`, `complete=true`, `passes_gate_90=true`, `warning_count=0`. |
| VIF | `packages/vif/__init__.py`<br>`packages/vif/kappa_gate.py`<br>`packages/vif/tests/test_kappa_gate.py`<br>`.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | Package-native `KappaGate.check(...)` probe plus MCP `track_confidence` tool-path probe | `degraded` | Package-native probe passed at `confidence=0.87` for `IMPORTANT` with threshold `0.85` and `should_escalate=true`. MCP `track_confidence` also returned success for `IMPORTANT`, witness `vif_00714f9a9cf44ca8850f609f2c71c65c`, and `current_ece=0.0`. Prior runtime truth still marks VIF functional but unused. |
| HHNI | `packages/hhni/__init__.py`<br>`packages/hhni/hierarchical_index.py`<br>`packages/hhni/tests/test_hierarchical_index.py`<br>`.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | Package-native `HierarchicalIndex.index_document(...)` and `query(...)` probe plus MCP `get_hhni_status` tool-path probe | `degraded` | Package-native probe indexed a sample doc, created `51` nodes, and returned `2` paragraph query results. MCP `get_hhni_status` simultaneously reported `hhni_index_initialized=false`, `retriever_available=false`, and `index_nodes=0` for the live runtime. |
| CAS | `packages/cas/__init__.py`<br>`packages/cas/activation.py`<br>`packages/cas/tests/test_activation.py`<br>`.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | Package-native `ActivationTracker` probe plus prior runtime-truth cross-check | `degraded` | Package-native probe recorded principle use and captured state with `19` principles tracked, `128` context tokens, and `load_level=0.4`. Prior runtime truth still records 5 core principles cold and overall CAS health degraded. |

## Boundary

- `live` here means a bounded local check executed successfully on this machine.
- `degraded` here means at least one live path worked, but current runtime-state evidence still shows missing health, missing usage, or missing initialization.
- `unavailable` here means the target could not be imported or exercised from the local package surface.
