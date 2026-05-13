# AIM-OS Runtime Degraded Feature Register

Work package: `CONSOLIDATION_WORK_PACKAGE_03_2026-03-13`

This register captures degraded, partial, or weakly-proven runtime surfaces observed during bounded verification.

| Surface | Degraded or weak feature | Direct evidence | Current observation |
| --- | --- | --- | --- |
| SIS package surface | Package entrypoint unavailable | `packages/sis/__init__.py`<br>`packages/sis/sis_core.py` | Import fails before any runtime behavior: `No module named 'sis.system_usage_auditor'`. Referenced sibling modules `system_usage_auditor`, `performance_monitor`, `gap_identifier`, `improvement_implementer`, and `continuous_learner` are not present on disk. |
| HHNI runtime bridge surface | Runtime retrieval/index not initialized | MCP `get_hhni_status`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | Live runtime reports `hhni_index_initialized=false`, `hhni_retriever_initialized=false`, `index_nodes=0`, `retriever_available=false`, even though the package-native hierarchical index can build/query locally. |
| CAS runtime health surface | Introspection runtime health remains degraded | `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md`; package-native `ActivationTracker` probe | Local tracker works, but prior runtime truth still records 5 core principles cold and overall CAS not healthy. |
| VIF runtime usage surface | Confidence system is live but still low-evidence operationally | MCP `track_confidence`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `track_confidence` returned a valid witness and passed the kappa gate, but `current_ece=0.0` and prior runtime truth records zero real tracked predictions / unused operational state. |
| SEG runtime content surface | Knowledge synthesis path is live but current runtime graph was empty in the bounded probe | MCP `synthesize_knowledge`; package-native `SEGraph` probe | Tool-path returned success, but the runtime synthesis for `WP03`, `SEG`, `verification` observed `0` entities, `0` relations, `0` contradictions, and `0` provenance chains. |
| HHNI package-side environment | Package-native probe emitted host-side cache write noise outside workspace | Package-native `HierarchicalIndex` probe output | The package-native run succeeded, but also emitted permission warnings while attempting Hugging Face cache writes under `C:\Users\bombe\.cache\huggingface\...`. This did not block the bounded local query result. |
| SDF-CVF verification environment | Initial non-workspace temp-path probe was noisy | Package-native parity probe sequence | The first parity attempt used a non-workspace temp location and did not give usable evidence. A repo-local rerun under `.agent/tmp/` succeeded cleanly and is the only SDF-CVF result counted in this work package. |

## Notes

- APOE is not listed here because both the package-native probe and MCP `create_plan` probe returned usable success results in this pass.
- SDF-CVF is listed only for method-sensitivity, not because the repo-local parity calculation failed.
