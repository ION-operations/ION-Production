# ION_VNEXT Route Map

Status: M33 candidate route map

This map chooses the next bounded packet after the vNext front door is bound.
Do not combine these routes without a new approval packet.

## Open Routes

### M34 Kernel Dependency Expansion

Purpose: expand `02_kernel/ion_core` from the M31 control surface into the next
dependency-closed kernel slice.

Use when the next priority is kernel capability, import closure, or broader
control tests.

Must not include runtime/current-state JSON, source-pool bulk copy, private
material, or product/carrier migration.

### M35 Product And Carrier Source-Pool Audit

Purpose: audit product and carrier source pools before any promotion.

Candidate pools include:

- `ION_GPT` -> `03_products/custom_gpt`
- `dAimon` -> `03_products/daimon`
- `browser_extension` -> `04_carriers/browser_extension`
- `mcp` -> `04_carriers/mcp`
- `Cursor` -> `04_carriers/cursor` if present
- `.github` -> `04_carriers/github_actions`

This route is audit first, not copy first.

### M36 Runtime And Context Lifecycle Design

Purpose: design the split between runtime state, context state, receipts,
capsules, ledgers, and next-context indexes.

Use when the next priority is preventing runtime/current-state JSON from being
bulk-copied or hand-patched.

### M37 Release And Export Hygiene

Purpose: define release candidates, validated bundles, local exports, package
hygiene, and private-material exclusion.

Use when the next priority is release/export readiness rather than source
promotion.

## Selection Rule

Pick one route, declare the authority ceiling, list allowed write paths, and
require validation plus receipt before any state-bearing claim.
