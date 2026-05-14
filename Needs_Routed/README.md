# Needs Routed

`Needs_Routed/` is the workspace inbox for branch packets, patches, context
packages, generated bundles, and operator-supplied artifacts that need ION
routing before they can become active state.

## Current Contract

- posture: sandbox-candidate
- accepted_state_claim: false
- production_authority: false
- live_execution_authority: false
- secrets_authority: false

Place new artifacts in `drop/` when you want a bounded intake worker to classify
and archive them. Existing top-level files are treated as legacy backlog and are
not moved by the first intake slice.

## Lanes

```text
drop/       new operator drops for confirmed intake
intake/     reserved in-progress lane
routed/     reserved routed-work projections
history/    archived originals after confirmed intake
blocked/    secret/private-risk or owner-blocked artifacts
receipts/   timestamped intake receipts
indexes/    current machine-readable indexes
diffs/      existing patch evidence source lane
workpackets/existing workpacket source lane
```

## Commands

Read-only classification:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages python3 -S -m kernel.ion_needs_routed_intake \
  --ion-root . \
  --json
```

Confirmed intake write for items under `drop/`:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages python3 -S -m kernel.ion_needs_routed_intake \
  --ion-root . \
  --write \
  --confirmation ION_NEEDS_ROUTED_INTAKE_WRITE_CONFIRMED \
  --json
```

The write command writes `receipts/` and `indexes/`, and only moves artifacts
from `drop/` into `history/` or `blocked/`. It does not mutate active queues,
stage Git paths, commit, push, deploy, or settle ION state.

## Specialist Routes

Current intake recognizes these specialist review lanes:

```text
branch_context_package_review     branch delegation, README/AGENTS/capsule, git containment
browser_extension_package_review  browser extension / ChatOps Bridge packets
queue_hygiene_patch_review        Codex queue runner and no-receipt hygiene patches
custom_gpt_package_review         Custom GPT/front-door/carrier packages
context_package_ingest            capsules, continuity exports, transfer packages
```

If another worker owns a lane, leave its source files alone and use the intake
index/receipt as the coordination surface.
