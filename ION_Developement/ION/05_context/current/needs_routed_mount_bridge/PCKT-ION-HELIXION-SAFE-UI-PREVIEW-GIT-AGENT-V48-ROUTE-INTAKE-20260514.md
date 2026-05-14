# PCKT-ION-HELIXION-SAFE-UI-PREVIEW-GIT-AGENT-V48-ROUTE-INTAKE-20260514

POSTURE: sandbox-candidate route-intake proof only
ACCEPTED_STATE_CLAIM: false
PRODUCTION_AUTHORITY: false
LIVE_EXECUTION_AUTHORITY: false
SECRETS_AUTHORITY: false

## Objective

Accept only the route/intake proof for the v4.8 UI Preview Action + Guarded Git
Lane candidate. Do not apply v4.8, do not deploy, do not update GPT Builder, do
not push main, and do not mutate live queues.

This packet exists because one carrier view could see only the active
`ION_Developement/` subroot and reported `Needs_Routed/` as missing. The
repo-root paths are present on GitHub and in the local repo; this bridge gives a
subroot-mounted carrier the proof references needed to request/remount the
repo-root view.

## Repo Proof

```text
repo: ION-operations/ION-Production
branch: codex/ion-custom-gpt-front-door-carrier-v4
commit: d111d96373280526c8e4b511fe07e46b92e889b2
```

Repo-root paths verified in commit `d111d963`:

```text
Needs_Routed/workpackets/PCKT-ION-HELIXION-SAFE-UI-PREVIEW-GIT-AGENT-V48-CANDIDATE-RECONCILE-20260514.md
sha256: cfb02752e5331cac9f48341f8d5fac0e7142ac7d233df2293af377ee991cb183
git_blob_sha: 586996d799e5dc46544854a321217b6d6f66b0f0

Needs_Routed/receipts/helixion_safe_ui_preview_v4_8_candidate_route_20260514T193227Z.yaml
sha256: 787ee7e37dd027a465a6ede287854555141a3f93771bc540dd4703fee3a645aa
git_blob_sha: 6cebb3aae0d9f6230a33d95e06e65c5da392c310

Needs_Routed/ION_CUSTOM_GPT_V4_8_UI_PREVIEW_ACTION_GIT_CANDIDATE_20260514T010500Z.zip
sha256: 115f1425afb23d14456515c33e7402def8778dcca8d0272682579c13227d514e
```

## Mount Requirement

The consuming carrier should mount:

```text
repo: ION-operations/ION-Production
ref: codex/ion-custom-gpt-front-door-carrier-v4
root: repo root
```

It should not mount only:

```text
ION_Developement/
default branch
stale workspace snapshot
```

## Route-Intake Acceptance

Accept only these facts:

```text
v4.8 candidate bundle exists at repo root under Needs_Routed
v4.8 route workpacket exists at repo root under Needs_Routed/workpackets
v4.8 route receipt exists at repo root under Needs_Routed/receipts
route posture is candidate only
route blocks raw patch apply, deploy, push, GPT Builder update, and accepted-state claim
```

Do not accept or perform:

```text
v4.8 patch application
source reconciliation
project workbench mutation
browser extension mutation
runtime JSON promotion
live MCP queue write
service restart
production deploy
```

## Preview Lane Split To Preserve

```text
Static ChatGPT Mock Preview Lane:
  small HTML/CSS/JS sketches only;
  no dependency install;
  no real project build claim.

Helixion Ephemeral App Preview Lane:
  isolated project checkout/worktree;
  bounded dependency install only after approval;
  build/test/lint receipts;
  bounded preview server;
  Playwright/browser capture;
  screenshot/HTML/model receipts;
  rollback snapshot;
  git-agent proposal;
  promotion only after receipts and explicit approval.
```

## Next Packet After Route Intake

After route-intake proof is accepted and the repo-root mount is available,
proceed to source discovery only:

```text
PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-SOURCE-DISCOVERY-20260514
```

Source discovery should inspect:

```text
project workbench preview/capture
bounded patch preview/apply
git status / git-agent proposal surfaces
rollback snapshot receipts
preview host/service adapter
Action/MCP payload limits
Cosmos browser capture precedent
worker cockpit UI proof surfaces
```

It should produce the build plan for:

```text
Actions-driven UI edit
-> bounded patch
-> temporary dependency install/build
-> ephemeral preview URL
-> screenshot/model receipt
-> rollback snapshot
-> git-agent commit proposal
-> approval gate
```

## Return Format

Return:

```text
POSTURE
MOUNT_PROOF
ROUTE_PROOF
ACCEPTED_FACTS
REJECTED_ACTIONS
NEXT
```
