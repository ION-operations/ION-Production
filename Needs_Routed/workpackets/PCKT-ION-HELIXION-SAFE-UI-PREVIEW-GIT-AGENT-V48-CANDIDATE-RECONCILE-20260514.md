# PCKT-ION-HELIXION-SAFE-UI-PREVIEW-GIT-AGENT-V48-CANDIDATE-RECONCILE-20260514

POSTURE: sandbox-candidate
ACCEPTED_STATE_CLAIM: false
PRODUCTION_AUTHORITY: false
LIVE_EXECUTION_AUTHORITY: false
SECRETS_AUTHORITY: false

## Objective

Reconcile the v4.8 Custom GPT UI Preview Action + Guarded Git Lane candidate
against the current ION workspace without raw-applying the patch, deploying,
starting live services, updating GPT Builder, pushing Git, or claiming accepted
state.

Source bundle:

```text
Needs_Routed/ION_CUSTOM_GPT_V4_8_UI_PREVIEW_ACTION_GIT_CANDIDATE_20260514T010500Z.zip
sha256: 115f1425afb23d14456515c33e7402def8778dcca8d0272682579c13227d514e
```

Candidate bundle posture:

```text
base: v4.7 final_candidate_tree
tests: 61 passed in source sandbox
patch_apply: pass against intended v4.7 base
production_authority: false
live_execution_authority: false
accepted_state_claim: false
```

## Preview Lane Contract

Preserve two distinct preview lanes:

```text
1. Static ChatGPT Mock Preview Lane
   - small HTML/CSS/JS mockups only
   - no dependency install
   - no real project build claim
   - no production authority

2. Helixion Ephemeral App Preview Lane
   - project checkout or isolated worktree
   - bounded dependency install only when explicitly authorized
   - build/test/lint gates
   - bounded preview server
   - Playwright/browser capture
   - screenshot/HTML/model receipts
   - rollback snapshot and git-agent proposal
   - promotion only after receipts and explicit approval
```

Do not describe the second lane as generic "safe preview on Helixion website"
without the isolation, receipt, rollback, and approval gates.

## Allowed Scope

Primary reconciliation scope:

```text
ION_CONTEXT_CAPSULE.yaml
ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md
ION_GPT/04_CURRENT_SANDBOX_CARRIER/UI_PREVIEW_ACTION_GIT_LANE_SUMMARY.md
ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/
ION_GPT/ION_CONTEXT_CAPSULE.yaml
Needs_Routed/ion_custom_gpt_v4_8_ui_preview_action_git_lane_receipt_20260514T010500Z.yaml
Needs_Routed/ion_ui_preview_build_request_example_20260514T010500Z.yaml
Needs_Routed/ion_git_agent_ui_preview_packet_example_20260514T010500Z.yaml
```

Reference-only current ION implementation surfaces:

```text
ION_Developement/ION/04_packages/kernel/ion_project_workbench.py
ION_Developement/ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py
ION_Developement/ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py
ION_Developement/ION/03_registry/ion_chatgpt_browser_mcp_tool_policy.yaml
ION_Developement/ION/05_context/current/helixion_joc_rebuild/HELIXION_COSMOS_PROJECT_WORKBENCH_BROWSER_CAPTURE_RECEIPT_20260513.json
```

## Hard Exclusions

Do not touch in this reconciliation packet:

```text
browser_extension/
Cosmos/project source
runtime/current queue JSON
codex_solo live state files
production deployment config
secrets, vaults, credentials, browser profiles, token files
live MCP queue mutation
service restart/deploy paths
Git push/merge/main update
GPT Builder update
```

## Reconciliation Strategy

1. Inspect the v4.8 ZIP manifest, report, queue packets, and final_candidate_tree.
2. Compare current Custom GPT/context-package files against the v4.8
   final_candidate_tree.
3. If the branch still matches the v4.7 reconciled Custom GPT lane, a scoped
   `git apply --check` may be used for diagnostics only.
4. If patch check fails, do not force it. Reconcile manually from
   `final_candidate_tree`, preserving newer active-branch laws and local
   return-contract hardening.
5. Keep v4.8 as a Custom GPT/context-package layer. Do not mix it with runtime
   project-workbench source changes or browser-extension work.

## Contracts To Preserve

```text
UI_PREVIEW_BUILD_LANE_LAW
GUARDED_GIT_AGENT_LAW
UI_PREVIEW_BUILD_ROUTE
ion.ui_preview_build_request.v1
ion.ui_preview_build_receipt.v1
ion.preview_deployment_policy.v1
Helixion ephemeral preview surface registry
preview-only default posture
no push/merge/production deploy without approval receipt
no secret/vault export
queue-ready Git agent packet when live Actions are unavailable
```

## Required Validation

After reconciliation, run:

```bash
python -m pytest -q ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/tests

python -m py_compile \
  ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/tools/ion_custom_gpt_ui_preview_guard.py
```

Run YAML/JSON parse over:

```text
ION_GPT
ION_CONTEXT_CAPSULE.yaml
Needs_Routed/ion_custom_gpt_v4_8_ui_preview_action_git_lane_receipt_20260514T010500Z.yaml
Needs_Routed/ion_ui_preview_build_request_example_20260514T010500Z.yaml
Needs_Routed/ion_git_agent_ui_preview_packet_example_20260514T010500Z.yaml
```

Run scoped diff check over only the allowed reconciliation paths.

Static checks:

```bash
rg "UI_PREVIEW_BUILD_LANE_LAW|GUARDED_GIT_AGENT_LAW" \
  ION_GPT/01_GPT_BUILDER_INPUTS \
  ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier

rg "UI_PREVIEW_BUILD_ROUTE|ion.ui_preview_build_request.v1|ion.ui_preview_build_receipt.v1" \
  ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier

rg "production_deploy_allowed: false|main_push_allowed: false|push_allowed: false" \
  ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier
```

## Required Receipt

Write:

```text
Needs_Routed/ion_custom_gpt_v4_8_ui_preview_action_git_reconciliation_receipt_<timestamp>.yaml
```

Include:

```text
schema_id: ion.custom_gpt.v4_8.ui_preview_action_git.reconciliation_receipt.v1
posture: sandbox-candidate
accepted_state_claim: false
production_authority: false
live_execution_authority: false
source_bundle: Needs_Routed/ION_CUSTOM_GPT_V4_8_UI_PREVIEW_ACTION_GIT_CANDIDATE_20260514T010500Z.zip
source_bundle_sha256: 115f1425afb23d14456515c33e7402def8778dcca8d0272682579c13227d514e
preview_lanes:
  static_chatgpt_mock_preview: pass|fail
  helixion_ephemeral_app_preview: pass|fail
contracts:
  ui_preview_build_lane: pass|fail
  guarded_git_agent: pass|fail
  helixion_preview_policy: pass|fail
  no_production_deploy: pass|fail
  no_main_push: pass|fail
  no_secret_export: pass|fail
files_changed: [...]
tests_run: [...]
blockers: [...]
next: [...]
```

## Return Format

Return exactly:

```text
POSTURE
BRANCH
RECONCILIATION_STRATEGY
WHAT_CHANGED
VALIDATION
FILES_CHANGED
RECEIPT
BLOCKERS
NEXT
```

## Next Packet After Reconciliation

Only after v4.8 reconciles and validates, create a separate implementation
packet for the real Helixion ephemeral app preview adapter. That later packet
must review project workbench security, temporary dependency install policy,
preview server lifecycle, Playwright capture receipts, rollback manifests, and
git-agent branch containment before enabling broader project preview workflows.
