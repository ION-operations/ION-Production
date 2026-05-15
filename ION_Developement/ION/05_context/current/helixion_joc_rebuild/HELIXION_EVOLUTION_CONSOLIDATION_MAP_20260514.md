# Helixion Evolution Consolidation Map - 2026-05-14

package_id: helixion_evolution_consolidation_map_20260514
status: candidate_consolidation_map
created_at: 2026-05-14T20:26:28Z
called_by: operator_consolidation_request
manager_agent: codex_local
authority_scope: local_candidate_planning_and_bounded_source_patch_only
production_authority: false
live_execution_authority: false
secrets_authority: false
unrestricted_browser_control: false

## Purpose

Consolidate the fast-moving ION, Helixion, Cosmos, worker cockpit, fanout, Needs_Routed, ION_GPT, and ephemeral preview lane changes into one actionable map. This is not a production acceptance record. It identifies what is settled, what is candidate, what is runtime evidence, and what must be gated next.

## Current Roots

| Root | Branch | Head | Current state |
|---|---:|---:|---|
| `/home/sev/ION - Production/ION_Developement` | `codex/ion-custom-gpt-front-door-carrier-v4` | `0585c278` | Model-override/project-context source lane committed locally; runtime/context changes still in progress |
| `/home/sev/Cosmos/earth-forge` | `main` | `8fd8e02` | `vite.config.ts` remains locally modified for Helixion preview base/HMR behavior |

## Active Consolidation Buckets

| Bucket | Status | Evidence | Consolidation decision |
|---|---|---|---|
| Model routing and queue runner | locally committed candidate source lane | `0585c278`, `Needs_Routed/ion_gateway_project_context_model_override_lane_receipt_20260515T005503Z.yaml` | Source/test blocker resolved locally. Live-listener reload and proof-repair retest remain separate follow-up work. |
| Helixion Ephemeral Preview Lane | source discovery complete | `ION/05_context/current/helixion_preview_lane/PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-SOURCE-DISCOVERY-REPORT-20260514T201359Z.md` | Implement packet 1 first: status/policy/schema. Do not jump to install/build/preview mutation yet. |
| Cosmos project workbench | candidate working precedent | project workbench tools, live proxy, browser capture receipts, Cosmos `vite.config.ts` preview base | Keep Cosmos as the precedent project, then generalize the registry after preview policy exists. |
| Worker cockpit JOC UI | locally settled candidate with handoff | worker cockpit settlement and retest artifacts under `ION/05_context/current/worker_cockpit/` | Needs external reload/retest. Do not restart `ion-mcp-preview.service` from inside a preview-hosted worker lane. |
| Kernel fanout scheduler | candidate tested surfaces | `ION/05_context/current/kernel_fanout_scheduler/` | Keep as a control-plane fanout/dryrun lane until model override and preview policy are settled. |
| Needs_Routed and branch containment | committed source lane plus loose artifacts | branch delegation and AI git branch containment package refs; untracked Needs_Routed artifacts | Use as routing input, not as direct mutation authority. Classify imports before applying more packages. |
| ION_GPT upload set | refreshed package lane | `ION_GPT/99_WORKER_DETAILS/gpt_upload_set_worker_details/` | Refresh again only after model override and preview-lane policy settle, otherwise upload set trails active source. |
| Runtime and context state | active evidence, not source product | queue state, Capsule/Mini/HOT/STATUS, connector runtime ledgers | Preserve for continuity; do not treat runtime churn as product source. |

## Recently Resolved Source Blocker

The active queue showed a model-routing blocker: a GPT-5.5/medium proof-repair experiment was routed through the default model path instead. The candidate integration for bounded model overrides was isolated and locally committed as:

```text
0585c278 ION: route project context and Codex model override lane
```

The source lane now provides:

- connector work requests can persist `codex_model_override`, `requested_model`, `requested_reasoning_effort`, and `model_override_reason`;
- the HTTP MCP tool schema exposes those fields;
- the queue runner validates overrides against `CODEX_MODEL_PROFILES`;
- invalid model or effort fails closed before launching Codex;
- `run.json` records `codex_model_override_receipt`;
- `codex_command` reflects the requested model and reasoning effort.

Focused validation from the active ION_Developement shell root:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q \
  ION/tests/test_kernel_ion_chatgpt_browser_mcp_connector_contract.py \
  ION/tests/test_kernel_ion_chatgpt_browser_mcp_http_preview.py \
  ION/tests/test_kernel_ion_chatops_bridge_policy.py \
  ION/tests/test_kernel_ion_codex_queue_runner.py \
  ION/tests/test_kernel_ion_custom_gpt_action_gateway.py \
  ION/tests/test_kernel_ion_project_workbench.py

127 passed in 1.30s
```

## Next Packet Order

1. `PCKT-ION-CODEX-QUEUE-RUNNER-MODEL-OVERRIDE-PROOF-REPAIR-RETEST-20260515`
   - After live listener reload, rerun a proof-repair retest packet requesting `gpt-5.5` plus `medium` and confirm the runner records the override receipt.

2. `PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-STATUS-POLICY-SCHEMA-20260514`
   - Add the read-only policy/schema layer for registered ephemeral preview projects.

3. `PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-WORKTREE-SNAPSHOT-SURFACE-20260514`
   - Add worktree snapshot metadata and rollback manifest receipts without install/build.

4. `PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-BUILD-DRYRUN-RECEIPT-SURFACE-20260514`
   - Add dry-run build/test/lint planner receipts before any execution hook.

5. `PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-PREVIEW-HOST-CAPTURE-RECEIPT-SURFACE-20260514`
   - Generalize Cosmos preview proxy and Playwright capture to the policy-backed project registry.

6. `PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-GIT-AGENT-PROPOSAL-SURFACE-20260514`
   - Add non-authorizing git diff/commit proposal artifacts. No commit, push, or deploy authority.

7. `PCKT-ION-HELIXION-EPHEMERAL-PREVIEW-LANE-PROMOTION-GATE-AND-ROLLBACK-SETTLEMENT-20260514`
   - Require build, capture, rollback-ready, and git proposal receipts before promotion.

## Dirty-State Handling

Preserve user and worker changes. Do not reset runtime/context files. Classify them:

- Source candidate: model override files and tests.
- Context/evidence: Capsule, Mini, HOT, STATUS, queue files, worker/fanout/project receipts.
- External package inputs: Needs_Routed and ION_GPT artifacts.
- Cosmos local source: `vite.config.ts` preview-base/HMR change remains a separate Cosmos repo settlement item.

## Boundaries

- No service restart in this consolidation packet.
- No deployment or git push.
- No GPT Builder update.
- No accepted-state claim.
- Browser automation remains bounded to allowlisted preview/capture tools with receipts.
