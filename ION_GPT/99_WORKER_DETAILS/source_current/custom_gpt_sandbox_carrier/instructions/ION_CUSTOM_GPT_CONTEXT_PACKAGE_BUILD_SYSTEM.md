# ION Custom GPT Context Package Build System

## Context package definition

An ION context package is a portable, proof-aware bundle that tells a future
carrier what a project/folder means and what sequence should continue. It is
not accepted state unless separately receipted and accepted.

## Required package layers

- `package_manifest`: identity, posture, hashes, created_at, source tree.
- `context_mesh`: folder capsules and parent/child inheritance.
- `workflow_state`: active route, objective, current phase, continuation.
- `persona_state`: selected persona/profile and visible envelope boundaries.
- `domain_agent_state`: candidate domains/agents and registry boundary.
- `architecture_signals`: important operator/project ideas still active.
- `fanout_state`: ordered fan-out plans, batons, unresolved alerts.
- `transfer_profile`: include/omit rules, non-exportable boundaries.
- `proof`: receipts, tests, checksums, validation report.
- `next_chat`: prompt and mount instructions.

## Build modes

- `minimal_continuity`: package only the state needed to continue in a new chat.
- `working_handoff`: include touched files, capsules, reports, tests, patches.
- `full_reproducible`: include enough to reproduce local state, never secrets.
- `public_safe`: sanitize local paths/private material and include public context.

## Non-exportable boundary

The package builder must never include vaults, tokens, credentials, browser
sessions, local caches, hidden chain-of-thought, or unredacted private secrets.
Ignored relevant files must be recorded in an omitted-files manifest with reason.
