# ION Organization Milestone 041 - vNext Receipt Core Landing

## Posture

Bounded vNext kernel-layer landing. Applied only the M40 vNext-native receipt core candidate into `ION_VNEXT`. No legacy receipt module, source pool, runtime/current-state JSON, queue, ledger, GPT Builder schema, Actions/MCP wrapper, private material, generated report, or broad runtime automation was promoted.

## Source Evidence

- `ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_040_KERNEL_LAYER_SELECTION_20260520T142452Z/`
- `ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_039_OPERATOR_ARTIFACT_HYGIENE_LANDING_20260520T140702Z/`
- `ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_037_CARRIER_MOUNT_RECEIPT_LANDING_20260520T132123Z/`
- `ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_035_RETURN_PROOF_GATES_LANDING_20260520T122601Z/`
- `ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_033_ION_VNEXT_FRONT_DOOR_BINDING_20260520T040027Z/`
- `ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_031_M27_CONTROL_PROMOTION_LANDING_20260520T022258Z/`
- `ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml`
- `ION_VNEXT/02_kernel/ion_core/pyproject.toml`

## M40 Inheritance Check

M40 decision:

```text
READY_FOR_M41_SMALL_KERNEL_LAYER_REVIEW
```

M40 validation:

```text
PASS_M40_PLAN_AND_CANDIDATE_VALIDATED
```

The M40 candidate file hashes matched the M40 manifest exactly, and source-law witness hashes still matched current on-disk evidence. The two M41 target files were absent before landing.

## Actions Taken

Promoted only:

- `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_receipt_core.py`
- `ION_VNEXT/02_kernel/ion_core/tests/control/test_kernel_ion_receipt_core.py`

Updated only:

- `ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml`

Created:

- `ION_VNEXT/01_canon/PROMOTION_WAVE_M41.yaml`

## Validation Summary

Current vNext pytest from `ION_VNEXT/02_kernel/ion_core`:

```text
66 passed in 0.17s
```

Additional checks passed:

- M41 Python AST parse
- vNext YAML/TOML parse
- report JSON parse
- no runtime/current-state JSON copied
- no queues or ledgers copied
- no private/secret/cache/git paths touched by M41
- no source-pool bulk copy
- `git diff --check`

## Decision

`PASS_READY_FOR_BOUNDED_COMMIT`

## Next Packet

`M42_KERNEL_LAYER_SELECTION`
