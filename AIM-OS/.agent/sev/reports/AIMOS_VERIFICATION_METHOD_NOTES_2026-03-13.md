# AIM-OS Verification Method Notes

Work package: `CONSOLIDATION_WORK_PACKAGE_03_2026-03-13`

## What Counted As A Live Check

| Method | Counted as live check | Used for | Notes |
| --- | --- | --- | --- |
| Package-native smoke probe | Yes | APOE, SEG, SIS, SDF-CVF, VIF, HHNI, CAS | Probes used repo-local `PYTHONPATH` and called package surfaces in shapes aligned to the local tests. |
| MCP tool-path probe | Yes | APOE, SEG, VIF, HHNI | These checks exercised the live HTTP bridge via `scripts/mcp_call.py` or `Invoke-RestMethod` with JSON bodies. |
| Static import/path inspection | No | SIS, supporting evidence for all targets | Used to confirm missing files, referenced imports, and entrypoint shape. Static presence alone did not count as a live result. |
| Prior runtime-truth cross-check | No | VIF, HHNI, CAS | Existing truth-map statements were used only to classify currently degraded runtime state after a bounded local check had already succeeded. |

## Method Execution Notes

- APOE package verification used the same `ACLParser.parse(...)` shape shown in `packages/apoe/tests/test_acl_parser.py`, then cross-checked the MCP `create_plan` path.
- SEG package verification used `SEGraph.add_entity(...)`. MCP verification used a direct JSON-body `synthesize_knowledge` request so list arguments were passed as a real list rather than a shell-coerced string.
- SIS did not reach behavioral verification. The import failed immediately, and static path inspection was used only to confirm that the referenced sibling modules are absent.
- SDF-CVF verification used `calculate_parity(...)`, not `verify_parity(...)`. The first probe attempted a non-workspace temp path and was discarded. Only the repo-local rerun under `.agent/tmp/` counts.
- VIF package verification and MCP verification were aligned to `task_criticality=IMPORTANT` so the kappa threshold matched across both checks.
- HHNI package verification succeeded locally, but MCP `get_hhni_status` still reported the live runtime as uninitialized. Both statements are true because package-local execution is not the same thing as bridge/runtime initialization.
- CAS does not expose a dedicated MCP runtime check in this packet, so the bounded live check was package-native and the degraded classification came from cross-checking the existing runtime truth map.

## Weak Or Incomplete Conclusions

- SEG tool-path success does not prove a populated evidence graph. This pass proved execution, not data richness.
- SDF-CVF package-native success does not prove a larger orchestration or migration path. This pass proved the parity calculator entrypoint only.
- HHNI package-native success does not overturn the current runtime-truth claim that the live retriever/index is not initialized.
- VIF tool success does not prove production calibration quality; `current_ece=0.0` in the live probe remains a weak-usage signal, not proof of calibrated operational use.

## Excluded From Conclusion Strength

- Shell argument marshalling failures in early `scripts/mcp_call.py` attempts were treated as invocation noise, not as system failures.
- Host-environment permission warnings outside the workspace were recorded when observed, but they were not counted as package failures if the bounded repo-local probe still completed successfully.
