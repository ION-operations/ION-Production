# ION Needs Routed Intake Protocol

POSTURE: sandbox-candidate
ACCEPTED_STATE_CLAIM: false
PRODUCTION_AUTHORITY: false
LIVE_EXECUTION_AUTHORITY: false
SECRETS_AUTHORITY: false

`Needs_Routed/` is the workspace inbox for packets, patches, bundles, and
branch-candidate artifacts that are not yet active ION state. This protocol
turns that folder into a governed intake lane without making broad staging,
commit, queue, deploy, or settlement claims.

## Product Requirement

The operator must be able to place files or folders from other branches,
ChatGPT/Sev sandboxes, workers, or manual exports into `Needs_Routed/` and have
a bounded Codex carrier classify them, propose a route, produce a receipt, and
archive the original once intake is explicitly confirmed.

The intake lane must preserve important candidate systems before they are lost
in chat, while keeping runtime evidence, private material, generated bundles,
and source patches out of unsafe mixed commits.

## Folder Contract

```text
Needs_Routed/
  drop/      operator drop zone for new intake artifacts
  intake/    reserved for future in-progress intake state
  routed/    reserved for future routed work-packet projections
  history/   archived originals after confirmed intake
  blocked/   artifacts requiring operator/security review
  receipts/  timestamped intake receipts
  indexes/   current machine-readable route indexes
  diffs/     existing source lane for patch evidence
  workpackets/ existing source lane for workpacket evidence
```

Existing top-level files and existing `diffs/` / `workpackets/` source lanes are
treated as legacy backlog by default. The intake tool may classify them in
read-only mode, but it must not move them unless a future packet explicitly
authorizes legacy backlog migration.

## Route Classes

| Route class | Meaning | Default action |
| --- | --- | --- |
| `apply_candidate_patch` | Patch/diff artifact that may be replayed in a scoped branch | propose review packet |
| `branch_context_package_review` | Branch delegation, README/AGENTS/capsule, or AI git containment package | propose branch-context review |
| `browser_extension_package_review` | Browser extension / ChatOps Bridge packet, tag contract, or UI/action lane artifact | propose extension review packet |
| `queue_codex_workpacket` | Workpacket or packet suitable for Codex carrier planning | propose queue packet only |
| `queue_hygiene_patch_review` | Codex queue/runner hygiene patch or validation packet | propose queue hygiene review |
| `custom_gpt_package_review` | Custom GPT/front-door/carrier bundle or patch | propose Custom GPT review |
| `context_package_ingest` | Capsule, continuity, transfer, or context package | propose context ingest |
| `source_lane_archive` | Report, receipt, or branch evidence worth preserving | preserve/index |
| `runtime_evidence_archive` | Runtime/receipt/log artifact not source code | preserve separately |
| `duplicate_or_superseded` | Same digest or obvious duplicate in current scan | preserve, avoid routing |
| `secret_or_private_blocked` | Filename/path indicates secret/private risk | block for operator review |
| `owner_review_required` | Unknown or ambiguous artifact | require owner classification |

## Authority Boundaries

The intake classifier may read file names, sizes, hashes, and short text
excerpts for route hints. It must not print or promote raw private context. It
must not inspect credential stores, browser profiles, vault material, or secret
payloads.

Read-only scan mode performs no moves and no queue mutation. Confirmed write
mode may write receipts and indexes. It may move artifacts only from
`Needs_Routed/drop/` into `history/` or `blocked/`. It must not move existing
top-level backlog or existing source-lane files by default.

Queue integration is proposal-only in this slice. Active Codex queue mutation
requires a later packet and explicit operator approval.

## Receipt Requirements

Every write-mode intake produces:

- timestamped receipt under `Needs_Routed/receipts/`
- current index under `Needs_Routed/indexes/`
- per-item source path, digest, size, route class, confidence, status, reasons
- explicit false authority flags
- queue proposal metadata when applicable
- moved target path only when a drop-zone artifact was archived

## Non-Claims

This protocol does not accept ION state, settle packets, stage Git paths, commit,
push, update GPT Builder, deploy services, mutate active queues, or grant live
execution authority.
