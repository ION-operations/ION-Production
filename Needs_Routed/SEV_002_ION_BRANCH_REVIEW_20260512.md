# SEV-002 ION Local Branch Review — 2026-05-12

## MOUNT RECEIPT

```yaml
AGENT_TAG: sev_002
CARRIER: chatgpt_sandbox_zip_review
BRANCH_ID: branch_sev_002_plan_evolution_review_20260512
CONTEXT_INSTANCE_ID: ctx_sev_002_ion_local_branch_review_20260512
CURRENT_PACKET: operator_request_familiarize_with_ion_and_evolve_multi_branch_plan
SOURCE_POSTURE:
  package_observed:
    - /mnt/data/ION_CODEX FULL(1).zip
    - /mnt/data/Pasted markdown(17).md
    - /mnt/data/README.md
    - /mnt/data/CONTRIBUTING.md
    - /mnt/data/SECURITY.md
  repo_observed:
    - extracted clean branch: /mnt/data/ion_clean/ION_CODEX FULL
    - extracted patched branch: /mnt/data/ion_patched/ION_CODEX FULL
  live_mcp_observed: []
  github_observed: []
AUTHORITY:
  production_authority: false
  live_execution_authority: false
  accepted_state_authority: false
WRITE_SCOPE:
  - sandbox-only review artifacts under /mnt/data
  - sandbox-only patch proposal for Python 3.11 f-string unblock
RETURN_TARGET: current_chat
SETTLEMENT_REQUIRED: true
ACCEPTED_STATE_AUTHORITY: false
```

## WHAT I CAN PROVE

- Zip extracted successfully: 27,841 entries, about 358 MB uncompressed.
- Branch observed: `feature/codex-capsule-chat-active-root...origin/feature/codex-capsule-chat-active-root`.
- HEAD observed: `4527c6e B00: preserve bounded patch confirmation through MCP adapter`.
- `ion_status` on the clean extraction returned `ION_STATUS_READY`.
- Active state integrity returned `ION_ACTIVE_STATE_INTEGRITY_READY` with `missing_state_surfaces: []`.
- Authority ceilings observed from status: `production_authority: False`, `live_execution_authority: False`.
- Targeted packet tests passed: `50 passed in 2.56s`.
- Clean full suite did not collect. Exit code: `2`. Failure class: Python 3.11 f-string syntax error in `ION/04_packages/kernel/ion_codex_chat_memory_visualization_ui.py`.
- Minimal syntax-unblock patch was generated: `/mnt/data/SEV_002_python311_fstring_unblock.patch`.
- After applying the patch in a fresh extraction, the full suite collected and ran: `532 passed, 18 failed, 2 skipped`. Exit code: `1`.
- `kernel.ion_carrier_mount_receipt render-startup` returned `ok: true` in sandbox.
- `kernel.ion_agent_branch_capsule reconcile` blocked in sandbox due to root mismatch between the branch record and extraction path: `[{'branch_id': 'branch_codex_local_ion_mason_branch_capsule_006', 'code': 'branch_record_validation', 'finding': {'actual_root': '/mnt/data/ion_clean/ION_CODEX FULL', 'code': 'root_mismatch', 'declared_root': '/home/sev/ION - Production/ION_CODEX FULL'}}]`.
- Changed-path secret scan reported 3 redacted findings across 92 candidate paths.

## WHAT I INFER

- The plan's immediate priority order is directionally correct: branch-capsule consolidation should land before carrier mount/persona, and both should land before broader Codex Carrier OS work.
- The candidate branch-capsule and carrier mount/persona code is strong enough for controlled review because the targeted tests pass and the design keeps `accepted_state_authority: false`.
- The branch is not globally commit-ready as-is, because the full test suite cannot even collect on Python 3.11 until the f-string issue is repaired.
- The sandbox root-mismatch failure is probably caused by absolute operator paths embedded in candidate branch records and Codex hooks. That is expected for a zip replay, but it is also a portability/control-plane design issue.
- The branch is mixing durable candidate code, runtime state projections, test residue, and large UI/chat state files. Controlled commit segmentation is mandatory.

## FINDINGS / DESIGN REVIEW

### 1. Branch capsule consolidation

Verdict: `commit_candidate_after_global_test_unblock_and_commit_scoping`.

Strengths:

- Defines explicit `context_instance_id`, `branch_id`, `agent_tag`, `conversation_tag`, parent context, loaded refs, write scope, settlement requirement, and accepted-state ceiling.
- Blocks direct shared Capsule/Mini/HOT_CONTEXT write scope.
- Provides material-work preflight, settlement-intake preflight, registry reconciliation, and cockpit snapshot support.
- Enforces `accepted_state_authority: false` and settlement flow.

Issues to resolve or document before commit:

- Sandbox replay blocks on root mismatch because records bind to `/home/sev/ION - Production/ION_CODEX FULL`. Decide whether absolute root binding is intentional, or add an explicit `sandbox_replay_root_alias` mode for review packages.
- `create_branch_capsule()` writes files even when validation is blocked. That may be acceptable as candidate evidence, but the return should make the blocked write semantics explicit.
- Settlement packet uses `schema` while other nearby surfaces use `schema_id`. Not fatal, but schema-key consistency should be resolved before this becomes cockpit/Supabase input.

### 2. Carrier mount/persona presentation

Verdict: `commit_candidate_after_branch_capsule_commit_and_mcp_tool_completion`.

Strengths:

- Correctly separates mount receipt authority from persona presentation.
- Receipt-only fallback is valid and tested.
- Loaded refs include SHA-256 proof for repo/package/MCP source types.
- Hidden reasoning exposure is explicitly forbidden.

Issues to resolve or document before commit:

- The plan says to add a read-only `ion_carrier_mount_receipt` MCP tool next; current `ion_mcp_local_bridge.py` adds Codex carrier/GitHub comms tools but not the mount receipt read-only tool.
- `write_mount_receipt_candidate()` returns `ok` as a string (`"true"`/`"false"`) rather than a boolean. Tests currently encode that behavior, but cross-surface consumers will expect booleans.
- Persona `hidden_reasoning_exposed=True` still builds a persona object and relies on validation to block it. That is acceptable for testability, but public presentation call-sites must always call validation before rendering.

### 3. Codex Carrier OS / raw context / GitHub fallback work

Verdict: `valuable_but_should_not_be_committed_before_the_two_immediate_packets_unless_separately scoped`.

Observed read-only projections:

- `build_codex_carrier_domain_registry()` returned `ok: true` / `ION_CODEX_CARRIER_DOMAIN_READY`.
- `build_codex_carrier_os_source_map()` returned `ok: true` / `ION_CODEX_CARRIER_OS_READY`.
- `build_raw_context_sync_lane_status()` returned `ok: true` / `ION_CODEX_RAW_CONTEXT_SYNC_LANE_READY`.
- `build_github_comms_fallback_status()` returned `ok: true` / `ION_GITHUB_COMMS_FALLBACK_STATUS_READY`.

Concern:

- This work is valuable but broad. It should not be folded into the branch-capsule or carrier-mount commits unless the operator explicitly accepts a larger phase-one Codex Carrier OS commit.

### 4. Full-suite failures after syntax unblock

After the Python 3.11 f-string unblock, failures grouped into these clusters:

- Codex project config/hook contract: tests expect `features.codex_hooks`; branch config uses `features.hooks`. Hook also hard-binds active root to `/home/sev/ION - Production/ION_CODEX FULL`, which blocks zip/sandbox replay.
- Parent `.codex` bridge files are expected by tests but are absent from the extracted package parent.
- `validate_ai_assistant_work_template_instances.py` runs under `python -S` and imports `yaml`; this fails without dependency visibility.
- ChatGPT connector/Codex chat acceptance and hydration tests fail after collection is unblocked.
- Codex solo context readiness is blocked in temp test roots.
- GitHub data-plane audit expects accepted current repo posture, but the tree is dirty by design.
- Operator queue classification test now returns `status_request` instead of `new_work_directive`.
- Skill activation recovery selection returns no `skill_id` for a recovery objective.

## IMPLEMENTATION PACKETS

### PCKT-SEV002-B00-PY311-FSTRING-UNBLOCK-001

Objective: make the full test suite collect on Python 3.11 before controlled commits.

Touched path:

- `ION/04_packages/kernel/ion_codex_chat_memory_visualization_ui.py`

Patch:

- `/mnt/data/SEV_002_python311_fstring_unblock.patch`

Validation:

- `python3 -m py_compile ION/04_packages/kernel/ion_codex_chat_memory_visualization_ui.py` passed.
- Full suite advanced from 12 collection errors to `532 passed, 18 failed, 2 skipped`.

### PCKT-SEV002-BRANCH-CAPSULE-COMMIT-GATE-001

Objective: controlled commit review for `PCKT-ION-BRANCH-CAPSULE-CONSOLIDATION-006`.

Required before commit:

- Apply/commit the Python 3.11 syntax unblock or prove a different interpreter baseline.
- Run targeted branch capsule tests.
- Run branch registry reconcile on the real operator root, not a zip replay root.
- Separate branch-capsule files from Codex Carrier OS/GDrive/GitHub fallback changes.
- Record settlement request and commit receipt.

### PCKT-SEV002-CARRIER-MOUNT-MCP-TOOL-001

Objective: complete the next stated action for carrier mount/persona.

Required work:

- Add read-only MCP tool for startup/current carrier mount receipt projection.
- Tool must return receipt, identity card, validation verdict, source posture, authority, and non-claims.
- Tool must not write files, start workers, expose hidden reasoning, or grant accepted state.
- Add unit tests in `test_kernel_ion_mcp_local_bridge.py`.

### PCKT-SEV002-COMMIT-SEGMENTATION-001

Objective: prevent one oversized commit from mixing runtime projections and durable protocol/code.

Proposed commit order:

1. B00 syntax/test-collection unblock.
2. Branch capsule consolidation only.
3. Carrier mount/persona presentation only, including MCP read-only receipt tool.
4. Codex Carrier OS cartography phase one.
5. Raw context sync lane policy/manifests.
6. GDrive mirror package.
7. GitHub comms fallback.

### PCKT-SEV002-QUEUE-COMPACT-VIEW-001

Objective: implement the plan's queue tooling requirement.

Required output fields:

- status counts
- canonical vs superseded counts
- latest returns
- oldest queued
- next actionable request
- response-size-safe limit behavior
- duplicate audit summary

## RISKS

- Full-suite collection failure can mask unrelated regressions until the f-string unblock lands.
- Absolute path binding makes branch capsules and Codex hooks precise on the operator machine but brittle in Drive/zip/sandbox mirrors.
- Runtime JSON state files are large and mutable; committing them with code changes risks accepting UI/chat projections as durable state by accident.
- Token-like literals in tests/patch artifacts can trigger external secret scanners even when they are synthetic.
- Codex config key drift (`codex_hooks` vs `hooks`) needs an explicit compatibility decision.
- Pending dAimon/operator queue residue can pollute next-action selection unless compact queue tooling lands.

## NEXT ACTION

Perform a controlled B00 syntax-unblock commit first, then rerun the full suite. After that, commit branch-capsule consolidation as the first state-bearing candidate packet, followed by carrier mount/persona with the missing read-only MCP mount receipt tool included.

## NON-CLAIMS

- I did not verify live MCP, Action Gateway, local cockpit, dAimon bridge, GitHub remote, Drive, Supabase, or Slack services.
- I did not commit, push, stage, or mutate the user's repository outside sandbox extraction paths.
- I did not treat any candidate branch output as accepted state.
- I did not prove that the full suite passes; it does not pass in this sandbox after the syntax unblock.
- I did not perform a complete repository secret audit; I performed a changed-path redacted scan only.
