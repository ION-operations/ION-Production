# Consolidation Findings Board 12 - 2026-03-14

## Scope

Synthesis of evidence produced by:

- `CONSOLIDATION_WORK_PACKAGE_13_2026-03-14.md`
- `CONSOLIDATION_FINDINGS_BOARD_11_2026-03-14.md`

This board is descriptive only.
It does not reopen decisions.

## High-Confidence Findings

### F-054 - The control and comms doctrine family now has a clean comparative role answer

The direct comparison now gives a stable rule-layer map:

- `AGENTS.md` anchors host-based identity routing and lane binding
- `.agent/STARTUP.md` anchors startup sequencing and boot discipline
- `.agent/COMMS_DOCTRINE.md` anchors response discipline and chain-of-command behavior
- `.agent/CONTEXT_CAPSULE_PROTOCOL.md` anchors capsule invariants and drift detection
- `.agent/comms/COMMS_PROTOCOL.md` anchors durable filesystem comms mechanics and identity-safe routing
- `.agent/comms/COMMS_CANONICAL.md` anchors the shortest high-clarity comms flow

### F-055 - The doctrine family is overlapping but not redundant

The local collisions are real, especially around:

- startup precedence
- MCP versus filesystem comms precedence
- first-response behavior
- capsule rule shape

But the comparison shows that each sibling preserves a different control value:

- routing
- boot gating
- behavior law
- anti-drift continuity law
- persistence mechanics
- compressed operator flow

### F-056 - The next unresolved family is not doctrine role, but continuity-truth precedence

The rule layer is now comparatively legible enough to move one layer down into
the surfaces that actually carry current state and recovery context:

- dated chat docs
- dated capsules
- status files
- per-agent `current_priorities.md`
- MCP-backed memory, messages, and timeline reads

Early local reads already show visible split risk:

- `sev.status.md` still reflects the earlier Aether-era frame
- `.agent/genomes/sev/context/current_priorities.md` still reflects 2026-03-13 onboarding priorities
- `antigravity.status.md` and `.agent/genomes/opus/context/current_priorities.md` are also older than today's consolidation progression
- OPUS does not currently show a 2026-03-14 chat or capsule trail in the expected local paths

### F-057 - Comparative consolidation has now crossed from rule law into continuity law

The consolidation has now produced direct comparative answers for:

1. JOC-adjacent surfaces
2. genome-surface families
3. host-adapter and console surfaces
4. Echo Forge sub-surfaces
5. the core runtime spine
6. the transport and execution cluster
7. the control and comms doctrine family

The next coherent move is to compare where live continuity actually resides,
not to make cleanup decisions yet.

## Current Best Reading

The visible local organism now looks split across two related but distinct
layers:

- doctrine surfaces that tell agents how to behave
- continuity surfaces that preserve what is actually current

The doctrine layer is now comparatively resolved.
The continuity layer still appears distributed across static files, rolling
docs, and MCP-backed surfaces with no settled local precedence answer.

## Next Evidence Priority

Open a direct comparison package for the continuity-surface family and answer
what each continuity surface does best locally, where live current state is
actually strongest, and where the organism currently risks drift between static
and rolling surfaces.
