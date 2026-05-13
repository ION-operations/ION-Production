# APOE↔CMC v1 PR Operations

Author: Aether/Codex  
Branch: `feature/apoe-cmc-v1`

## 1. Branch & PR Checklist
- Target branch: `feature/apoe-cmc-v1` → `clean-master`.
- PR template must:
  - Link to `agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md`.
  - Link to `agents/alex/APOE_CMC_TEST_CHECKLIST.md`.
  - Attach at least one payload sample from `packages/apoe/samples/apoe_cmc_sample_payloads.json`.
- Description should call out:
  - What changed (clean-room module + refreshed tests).
  - Sample atom snippet (modality/tags/metadata) for Atlas/Sev review.

## 2. Required Reviewers
- Manually add **Atlas** and **Sev** as required reviewers when opening the PR.
- Block merge until both approvals are recorded.

## 3. CI Gate
- Add a lightweight CI step (pre-merge script or pytest) that:
  1. Loads the emitted atom fixture(s) or the new sample payload file.
  2. Verifies `modality == "plan_execution"`.
  3. Ensures `tags` contains `apoe`, `plan`, `execution`, and both `plan_name:<name>` + `status:<status>`.
- Fail the build if any condition is unmet.

## 4. Artifacts & Samples
- Keep sample payloads in `packages/apoe/samples/apoe_cmc_sample_payloads.json` (start/partial/complete).
- Reference the same payloads in the PR description and in any board updates to Atlas/Sev.

## 5. Coordination Hooks
- Mirror every new R-CONS-002 readiness acknowledgement into:
  - `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_ROUTER.md`.
  - `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_INDEX.md`.
- Once 8/8 acks are logged, immediately post the synthesis agenda + anchor reminders (target 2025-01-28 15:00 UTC) and include the payload snippet.

## 6. After Merge
- Reply on Atlas + Sev boards with:
  - Final payload example.
  - Link to merged PR + test results.
- Update registry/digest entries so the takeover is reflected in daily summaries.
