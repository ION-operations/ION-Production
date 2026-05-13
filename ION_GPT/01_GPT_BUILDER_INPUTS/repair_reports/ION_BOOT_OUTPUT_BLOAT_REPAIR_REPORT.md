# ION Boot Output Bloat Repair Report

Status: local reproduction of sandbox repair because sandbox download links were unavailable.

## Problem

Boot/status replies exposed internal safety doctrine as public clutter.

## Repair

- Created v0.3 instructions.
- Made compact boot contract the public default.
- Moved BOOT-SEED/source-order/role-sequence/machine blocks to artifact/on-request detail.
- Compressed non-claims into `AUTHORITY`.

## Current public boot contract

```text
BOOT :: mounted | blocked
POSTURE :: CLEAN | CONSERVATIVE | DEGRADED | BLOCKED
SOURCES :: <one-line source summary>
OBJECTIVE :: <current objective or none found>
BLOCKER :: <only if actionable>
NEXT :: <one next route>
AUTHORITY :: read-only | sandbox-candidate-write | approved-bounded-write | live-authorized
```
