# Codex Memory Curator Protocol v0.1

Status: candidate
Date: 2026-05-15
Packet: PCKT-ION-CODEX-MEMORY-CURATOR-V0_1

## Purpose

Codex memory is visible and editable at the artifact layer, but the memory
engine remains a black box. ION may observe and shape contribution lanes, then
verify generated memory artifacts, without claiming knowledge of Codex's hidden
scoring, selection, consolidation, or future injection rules.

## Core Law

```text
WRITE MEMORY THROUGH CONTRIBUTION LANES, NOT BY EDITING GENERATED OUTPUT FIRST
```

Default flow:

```text
observe
-> classify
-> propose
-> write ad_hoc note
-> watch consolidation
-> verify generated MEMORY.md / memory_summary.md
-> reconcile with ION truth
```

## Layers

ION truth layer:

- receipts
- packets
- capsules
- source files
- branch context
- AGENTS.md
- skills

Codex native recall layer:

- `/home/sev/.codex/memories/MEMORY.md`
- `/home/sev/.codex/memories/memory_summary.md`
- `/home/sev/.codex/memories/raw_memories.md`
- `/home/sev/.codex/memories/extensions/ad_hoc/`
- `/home/sev/.codex/memories/rollout_summaries/`

Carrier sync layer:

- Codex hooks
- ION skills
- MCP/Action branch leaders
- compaction checkpoints
- turn receipts

## Authority Boundary

Memory is recall, not authority.

Codex memory never grants:

- accepted state
- production authority
- live execution authority
- secrets authority
- ION identity
- STEWARD / RELAY / PERSONA authority
- hidden reasoning authority

When memory conflicts with current repo authority, receipts, packets, tests, or
explicit operator instructions, current proof and authority win.

## Memory Classes

stable_workflow_fact:
  Reusable process knowledge that is likely stable across future sessions.

user_preference:
  Explicit operator preference about collaboration, evidence, tone, or workflow.

project_convention:
  Durable convention about ION workspace roots, packets, capsules, receipts, or
  carrier boundaries.

rollout_evidence:
  Summary of a prior session or implementation run. Useful for retrieval, but
  time-specific facts must be reverified.

ad_hoc_note:
  Reviewed contribution note written under `extensions/ad_hoc/`.

stale_path_or_blocker:
  Known stale paths, path migrations, listener drift, or historical blockers.
  These require recency checks before use.

unsafe_secret_like_content:
  A redaction warning class. Do not print matched values. Move to review rather
  than promoting into generated memory.

generated_summary:
  Generated `MEMORY.md` or `memory_summary.md` content. Treat as carrier recall.

generated_raw_memory:
  Generated or consolidated raw memory source. Treat as evidence input, not final
  authority.

unknown:
  Needs curator review before promotion.

## Contribution Lanes

Preferred input lane:

```text
/home/sev/.codex/memories/extensions/ad_hoc/
```

Evidence input lane:

```text
/home/sev/.codex/memories/rollout_summaries/
```

Generated output lane:

```text
/home/sev/.codex/memories/MEMORY.md
/home/sev/.codex/memories/memory_summary.md
/home/sev/.codex/memories/raw_memories.md
```

Generated output should be inspected and diffed. Direct edits to generated files
are not the default path because they may fight consolidation.

## Curator Loop

1. Snapshot memory repo.
2. Add one controlled ad-hoc note.
3. Run or wait for a Codex session / consolidation trigger.
4. Snapshot memory repo again.
5. Diff generated and contribution paths.
6. Record whether the note was useful, distorted, ignored, overpromoted, or
   unsafe.
7. Reconcile generated recall against ION truth.

## Promote, Downgrade, Delete

Promote:
  Write a concise ad-hoc contribution note when the fact is stable, non-secret,
  and useful across sessions.

Downgrade:
  Add a corrective ad-hoc note when generated memory overstates authority,
  embeds stale facts, or collapses inference into proof.

Delete:
  Do not delete generated memory as the first move. For unsafe secret-like
  content, stop, avoid printing values, and route to operator review. Deletion
  requires explicit operator approval.

## Integration

Codex Carrier Sync:
  Stop and PreCompact receipts can include memory-curator snapshot references
  when memory changed materially.

ION skills:
  `ion-memory-curator` should guide memory inventory, contribution, and
  verification steps.

MCP/Actions:
  Future branch leader tools can expose read-only memory inventory and diff
  summaries, not secret contents.

ION truth:
  Memory summaries may point to receipts and packets, but do not replace them.
