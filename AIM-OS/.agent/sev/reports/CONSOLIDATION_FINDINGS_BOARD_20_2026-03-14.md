# Consolidation Findings Board 20 - 2026-03-14

## Scope

Synthesis of evidence produced by:

- `CONSOLIDATION_WORK_PACKAGE_21_2026-03-14.md`
- `CONSOLIDATION_FINDINGS_BOARD_19_2026-03-14.md`

This board is descriptive only.
It does not reopen decisions.

## High-Confidence Findings

### F-086 - The operational-proof family now has a clean comparative role answer

The direct comparison now gives a stable operational-proof map:

- README surfaces are best at declaring capability
- implementation surfaces are best at encoding capability
- automated test surfaces are best at controlled proof of capability
- synthesized reports are best at summarizing bounded proof
- live probes are best at current-host proof

### F-087 - Operational proof is role-mapped, but still compositional rather than canonical

The comparison shows no single proof family covers all needed dimensions at
once:

- broad intended scope
- exact mechanics
- repeatable controlled assertions
- operator-readable bounded verification
- fresh host-state proof

So the organism is no longer unclear about what these proof families are for,
but it still depends on combining them rather than relying on one settled
proof layer.

### F-088 - The sharpest remaining ambiguity is activation and adoption, not proof role

WP21 makes the local tension explicit:

- capabilities can be declared richly in README surfaces
- mechanisms can exist concretely in code
- controlled tests can prove selected slices
- reports can summarize bounded checks
- yet the current host can still show uneven or partial activation

The unresolved ambiguity is now how AIM-OS capabilities move from declared and
implemented potential into actually wired, started, reachable, and exercised
runtime behavior on this host.

### F-089 - The next coherent evidence family is activation and wiring

The direct operational-proof comparison points to a deeper layer that has not
yet been compared directly:

- startup or runbook surfaces
- bootstrap or control-script surfaces
- bridge or server surfaces
- host-adapter or client surfaces
- live readiness probe surfaces

These are the visible families that appear to say:

- how a host is supposed to start
- how the bridge is actually launched or recovered
- where the transport surface really lives
- how host clients try to reach it
- what readiness looks like right now

## Current Best Reading

The organism is now comparatively legible in how it claims, encodes, tests,
summarizes, and live-proves behavior.

The next unresolved ambiguity is activation and wiring: AIM-OS still needs a
direct comparison of the surfaces that start, wire, expose, consume, and
confirm runtime capability before any canon, cleanup, or remediation move can
be discussed.

## Next Evidence Priority

Open a direct comparison package for activation and wiring surfaces and answer
what startup or runbook surfaces, bootstrap or control scripts, bridge or
server surfaces, host-adapter or client surfaces, and live readiness probes
each do best locally before any activation canon, cleanup, or remediation
decision is discussed.
