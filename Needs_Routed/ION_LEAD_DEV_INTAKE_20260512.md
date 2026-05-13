# ION Lead-Dev Intake — 2026-05-12

## Posture

**Proof posture:** CONSERVATIVE.

This intake was performed by ION-through-this-ChatGPT-carrier against visible uploaded files in the sandbox. It used scratch extraction, read-only scans, git inspection, patch applicability checks, and focused pytest runs. It does **not** claim local daemon state, live connector state, GitHub state, user-PC state, accepted ION state, or production deployment.

## Visible packages

- `ION FULL.zip`: current ION repo package inspected under `/mnt/data/ionfull_extract/ION_CODEX FULL`.
- `Pasted markdown.md`: worker recommendation and warnings.
- `dAimon.zip`: inspected as product/lineage/reference package. Contains `.env`/`.venv`; treat as secret-bearing/local-runtime material until repackaged.
- `_ui_canon.zip`: inspected as binding UI/JOC canon for UI work.
- `ATLAS.zip`: inspected as external-system/reference library, not ION workflow authority.
- `AIM-ION.zip`: inventoried as lineage/witness material; not deeply reconciled in this intake.

## High-confidence findings

1. ION source lanes are candidate evidence, not accepted runtime state. `diffs/README.md` and `workpackets/README.md` define patch/workpacket material as bounded source-lane input until routed by packet/receipt/operator decision.
2. The current extracted repo is dirty/candidate-rich: `git status --short` showed 482 entries: 416 untracked, 65 unstaged modified, and 1 index-modified path. `git diff --stat` showed 66 tracked files changed, 48,385 insertions, and 6,373 deletions.
3. Existing front-door indexes are stale relative to current source-lane content. The read-only ingest found 54 workpacket files and 25 diff files, while older reconstructed indexes cover fewer entries.
4. The read-only ingestion script completed and produced content-proof reports only. Its own non-claims are: no patch application, no source mutation, no accepted-state promotion, and no live connector invocation.
5. The B00 queue contamination is real. `codex_work_requests/` contains 211 request files, including 154 B00 spawn-contract repair files. The idempotency ledger path expected by the repair stack is absent in the current extracted tree.
6. The bootstrap patch stack is coherent but not already landed:
   - `ion_action_idempotency_no_receipt_repair_001.diff`
   - `ion_direct_bounded_patch_lane_002.diff`
   - `ion_codex_queue_duplicate_cleanup_003.diff`
   `001` applies cleanly to the current extracted tree. `002` and `003` require the preceding patches. In a scratch copy, applying `001 -> 002 -> 003` succeeded cleanly.
7. Focused connector tests passed before and after the bootstrap stack:
   - Current extracted tree: `22 passed`.
   - Scratch tree after `001 -> 002 -> 003`: `29 passed`.
   The stderr contained artifact-tool spreadsheet warmup noise unrelated to the pytest result.
8. Agent branch capsule material is important but not a clean blind-apply stack. Parts are already present; some diffs fail due partial landing, context drift, or absolute path problems. This needs consolidation/rebase, not direct application.
9. `ION_EXTENSION_SELECTED_REQUEST_START_REPAIR_CANDIDATE_20260511.diff` appears path-prefix drifted. `ion_extension_codex_daimon_candidate_improvements.patch` checks cleanly, but should wait behind bootstrap and branch-capsule stabilization.
10. UI work must obey the `_ui_canon`/JOC/OPUS requirements: matte-black DXL instrument-panel direction, no generic Material/purple-blue defaults, dense operational UI, and visual proof gates for UI claims.

## Immediate consolidation recommendation

### Phase 0 — Freeze live mutation lane
Do not rely on live Action/connector mutation, queue runner restart, or new worker spawn until the idempotency/direct bounded patch/duplicate cleanup stack is settled and tested.

### Phase 1 — Land source-lane witness reports as candidates
Use the generated ingest outputs as B00/B01/B02 witness evidence:
- root/file proof,
- source-lane inventory,
- diff/workpacket registries,
- settlement queue draft.

These outputs should not be promoted to accepted state without Steward/human settlement.

### Phase 2 — Bootstrap connector/queue repair
Apply the patch stack locally in order:

1. `diffs/ion_action_idempotency_no_receipt_repair_001.diff`
2. `diffs/ion_direct_bounded_patch_lane_002.diff`
3. `diffs/ion_codex_queue_duplicate_cleanup_003.diff`

Then run:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=ION/04_packages \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q ION/tests/test_kernel_ion_chatgpt_browser_mcp_connector_contract.py
```

Expected focused result from sandbox scratch proof: `29 passed`.

### Phase 3 — Preserve-and-supersede duplicate B00 requests
Run cleanup as a preservation/supersession process, not deletion. Desired state: one canonical B00 request remains actionable; duplicate B00 records are marked/superseded with receipt evidence.

### Phase 4 — Consolidate agent branch capsules
Create a new normalized consolidation patch rather than applying the existing capsule diffs blindly. Recommended candidate name:

`agent_branch_capsule_consolidated_006.diff`

This should reconcile:
- existing provisional protocols and registries,
- partial landed files,
- missing helper/tests,
- absolute path drift in `agent_branch_capsule_guard_003.diff`,
- settlement inbox/claim surfaces,
- startup identity-card enforcement.

### Phase 5 — Re-enable parallel workers only after capsule guard
Once bootstrap and branch capsules are tested, spawn named agent branches with explicit write scopes and settlement requirements.

## Suggested active branch tags

- `ion_orchestrator_steward_vizier`: plan, settlement sequencing, no direct code edits.
- `ion_patchwright_mason`: bounded patch production, no accepted-state claims.
- `ion_proof_nemesis`: read-only adversarial proof/audit.
- `ion_runtime_cartographer`: connector, queue, Action, extension, and local-runtime mapping.
- `ion_ui_joc_opus_canonist`: UI/JOC/OPUS canon review and visual-proof requirements.
- `ion_lineage_atlas_daimon_cartographer`: ATLAS/dAimon/AIM-ION lineage/reference review.

Each branch should carry at minimum:

```yaml
AGENT_TAG:
CONVERSATION_TAG:
TASK_TAG:
CONTEXT_INSTANCE_ID:
BRANCH_ID:
PARENT_CONTEXT_ID:
MODEL_LANE:
AUTHORITY:
WRITE_SCOPE:
LOADED_REFS:
CURRENT_PACKET:
SETTLEMENT_REQUIRED: true
ACCEPTED_STATE_AUTHORITY: false
```

## Recommended next packet

`PCKT-ION-BOOTSTRAP-IDEMPOTENCY-SETTLE-001`

Objective: locally apply `001 -> 002 -> 003`, run focused connector tests, run duplicate audit/supersession, and write candidate settlement receipts for B00/B01/B02. No live connector invocation. No accepted-state claim without human/Steward settlement.

## Generated artifact links

- `/mnt/data/ion_ingest_out/CONTENT_PROOF_MANIFEST.json`
- `/mnt/data/ion_ingest_out/LOCAL_CONTENT_PROOF_REPORT.md`
- `/mnt/data/ion_ingest_out/SETTLEMENT_QUEUE_CONTENT_PROVEN.json`
- `/mnt/data/ion_ingest_out/DIFF_REGISTRY_CONTENT_PROVEN.json`
- `/mnt/data/ion_ingest_out/WORKPACKET_REGISTRY_CONTENT_PROVEN.json`
