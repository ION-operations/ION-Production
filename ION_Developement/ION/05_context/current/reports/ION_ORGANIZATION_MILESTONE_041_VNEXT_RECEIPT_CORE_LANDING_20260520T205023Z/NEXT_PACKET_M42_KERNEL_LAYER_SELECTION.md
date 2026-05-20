# Next Packet - M42 Kernel Layer Selection

## Objective

Select the next minimal vNext kernel layer after M41 receipt core.

## Starting State

M41 landed a stdlib-only receipt core that can build, validate, classify, and hash source-bound receipt records without runtime queues, ledgers, current-state defaults, or file IO.

## Candidate Areas To Re-evaluate

- receipt hydration without current-state defaults
- package/profile boundaries
- branch context or capsule primitives
- clean export or release hygiene follow-on
- status/read-only visibility only if dependency closure is small

## Hard Boundaries

- no runtime/current-state JSON
- no active queues or ledgers
- no Actions/MCP runtime wrappers
- no GPT Builder schemas
- no browser execution/capture
- no Supabase/cockpit/provider/API integrations
- no private/vault/session material
- no source-pool bulk copy

## Expected Decision Values

- `READY_FOR_M43_SMALL_KERNEL_LAYER_REVIEW`
- `NEEDS_SMALLER_SCOPE`
- `NEEDS_LAYOUT_REVISION`
- `BLOCKED_BY_DEPENDENCY_EXPLOSION`
- `BLOCKED_BY_STALE_OR_CONFLICTING_SOURCE`
- `BLOCKED_BY_TEST_FAILURE`
