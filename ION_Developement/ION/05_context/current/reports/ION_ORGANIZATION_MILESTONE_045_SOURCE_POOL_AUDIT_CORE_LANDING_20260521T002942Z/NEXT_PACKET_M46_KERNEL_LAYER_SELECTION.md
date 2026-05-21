# M46 Kernel Layer Selection

Recommended next packet:

```text
M46_KERNEL_LAYER_SELECTION
```

M46 should remain read-only investigation and candidate-package generation unless explicitly converted into a landing packet.

Candidate directions to evaluate after M45:

- promotion decision integration using `ion_source_pool_audit_core.py`
- context package + receipt + source-pool linkage
- package/profile boundary core if it can be made vNext-native and dependency-light
- reference/archive classifier only if it does not duplicate source-pool audit core

Hard exclusions remain:

- runtime/current-state JSON
- active queues/ledgers
- ACTIVE_* defaults
- GPT Builder schemas
- Actions/MCP runtime wrappers
- browser execution/capture
- private/vault/session material
- source-pool bulk copy
