# Consolidation Findings Board 03 - 2026-03-13

## Scope

Synthesis of evidence produced by:

- `CONSOLIDATION_WORK_PACKAGE_04_2026-03-13.md`
- `CONSOLIDATION_FINDINGS_BOARD_01_2026-03-13.md`
- `CONSOLIDATION_FINDINGS_BOARD_02_2026-03-13.md`

This board is descriptive only.
It does not reopen decisions.

## High-Confidence Findings

### F-011 - AIM-OS control is distributed across multiple authority layers

Direct control claims now exist at the root, `.agent` canon layer,
lane-specific instruction/genome surfaces, and session-bound continuity
surfaces.

There is no single locally visible control file that fully governs identity,
startup, transport, communication, capsule behavior, and continuity by itself.

### F-012 - Startup and transport precedence are not globally singular

The repo now contains evidence for overlapping precedence claims across:

- `AGENTS.md`
- `.agent/STARTUP.md`
- `.agent/COMMS_DOCTRINE.md`
- `.agent/comms/COMMS_PROTOCOL.md`
- `.agent/comms/COMMS_CANONICAL.md`
- `docs/MCP_RUNBOOK.md`

The sharpest collision is transport truth: MCP-first, filesystem-first, and
hybrid comms guidance all exist simultaneously.

### F-013 - OPUS continuity is split across two route names

OPUS currently spans both `antigravity` and `opus` route families.

This is not a cosmetic naming issue only. It affects status, inbox, chat,
capsule, and continuity reads, which means file-path precedence is not locally
unambiguous for that lane.

### F-014 - Continuity stacks are uneven across the active agents

SEV and OPUS have comparatively rich continuity stacks.
CODEX and COMPOSER have thinner stacks with stale status surfaces.
COMPOSER-SEV currently has only a partial route set with no full status or
inbox support.

The organism does not yet provide one symmetrical continuity model across the
active team.

### F-015 - Current-state truth has no universal winning surface

Current-state information is spread across:

- chat docs
- capsules
- status files
- per-agent context files
- MCP-backed messages and memory

The repo does not yet contain one explicit universal precedence rule for which
surface wins when these disagree.

## Current Best Reading

The consolidation now has local proof for eight things:

1. AIM-OS spans all four major axes on disk
2. stale canon has drifted from visible repo reality
3. important truth exists outside the visible branch and machine boundary
4. core-system health is mixed across live, degraded, and unavailable states
5. package viability, runtime initialization, and operational usage are not the
   same truth surface
6. control authority is distributed across multiple file families
7. continuity is uneven across active agents and routes
8. local control precedence is not fully singular yet

## Next Evidence Priority

The strongest remaining ambiguity is now the boundary between:

- what the local repo can still settle on its own
- what depends on off-branch, off-machine, or operator-only truth
- what gates must still be satisfied before consolidation can be honestly
  considered complete

That points next toward an external-truth and completion-gate work package.
