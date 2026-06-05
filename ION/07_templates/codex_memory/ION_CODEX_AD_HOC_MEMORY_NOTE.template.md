# <Memory Title>

schema_id: ion.codex_memory_ad_hoc_note.v0_1
created_at: <iso8601>
source: <operator_or_curator>
memory_classes:
  - <stable_workflow_fact|user_preference|project_convention|rollout_evidence|ad_hoc_note|stale_path_or_blocker>
contribution_lane: extensions/ad_hoc
memory_is_recall_not_authority: true
accepted_state_claim: false
production_authority: false
live_execution_authority: false

## Memory

<Concise memory contribution. Prefer stable facts, explicit user preferences,
and project conventions. Do not include secrets or unverified accepted-state
claims.>

## Curator Notes

- This note is input for Codex memory consolidation, not generated memory output.
- Verify generated `MEMORY.md` and `memory_summary.md` after consolidation.
- If generated memory overstates the note, add a corrective contribution rather
  than editing generated output first.
