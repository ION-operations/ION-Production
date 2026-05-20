# Next Packet - M44 Kernel Layer Selection

## Objective

Select the next minimal vNext kernel layer after M43 context package core.

## Starting State

M43 landed a stdlib-only context package core that can build, validate, classify, and hash bounded context-package records without runtime/current-state coupling, queues, ledgers, `ACTIVE_*` defaults, file IO, source-pool traversal, or branch materialization.

## Candidate Areas To Re-evaluate

- package/profile boundary core
- receipt indexing/query primitive without live ledgers or hydration defaults
- source-pool audit primitive without traversal/mutation
- branch/context primitive only if it remains stdlib-only and non-materializing
- docs/context projection gates after context package primitives mature

## Hard Boundaries

- no runtime/current-state JSON
- no active queues or ledgers
- no `ACTIVE_*` defaults
- no Actions/MCP runtime wrappers
- no GPT Builder schemas
- no browser execution/capture
- no Supabase/cockpit/provider/API integrations
- no private/vault/session material
- no source-pool bulk copy
- no legacy root mutation

## Expected Decision Values

- `READY_FOR_M45_SMALL_KERNEL_LAYER_REVIEW`
- `NEEDS_SMALLER_SCOPE`
- `NEEDS_LAYOUT_REVISION`
- `BLOCKED_BY_DEPENDENCY_EXPLOSION`
- `BLOCKED_BY_STALE_OR_CONFLICTING_SOURCE`
- `BLOCKED_BY_TEST_FAILURE`
