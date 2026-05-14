---
type: architecture_protocol
schema_id: ion.ai_git_branch_containment_protocol.v0_1
status: CANDIDATE
authority: A2_DESIGN_CANDIDATE
created: 2026-05-14T17:02:32Z
purpose: Keep AI-authored edits durable, reviewable, and recoverable by forcing all material work into isolated Git branches/worktrees until approved.
connections:
  - ION/02_architecture/README_BRANCH_CONTEXT_PROTOCOL.md
  - ION/02_architecture/CODEX_BRANCH_SPECIALIST_PROTOCOL.md
  - ION/02_architecture/BRANCH_DELEGATION_ROUTER_PROTOCOL.md
  - ION/02_architecture/BRANCH_BUDGET_RECURSION_AND_DRIFT_CONTROL_PROTOCOL.md
  - ION/02_architecture/ION_GITHUB_DATA_PLANE_PROTOCOL.md
---

# AI Git Branch Containment Protocol v0.1

## Principle

AI work must be durable without being trusted.

The main checkout is not the AI's scratchpad. Every material AI edit belongs in a named isolated branch or worktree that can be inspected, tested, recovered, abandoned, or merged only after explicit approval.

This preserves both sides of the operator's requirement:

- no work is lost,
- and broken work cannot poison the main tree.

## Core law

An AI agent, carrier, automation, or delegated specialist must not perform material edits in a protected branch or protected checkout.

The lawful edit surface is:

```text
clean protected base -> isolated AI branch/worktree -> checkpoint commits -> review receipt -> approval -> merge/squash/cherry-pick
```

If the agent cannot prove it is in an isolated branch/worktree, it must degrade to read-only or produce a patch file instead of editing the checkout.

## Protected surfaces

Protected branches include, by default:

- `main`
- `master`
- `trunk`
- `production`
- `release`
- `stable`

The protected checkout is the operator's main working tree. It must remain clean or intentionally operator-owned. AI agents may read it and create candidate patch artifacts, but they may not treat it as their edit workspace.

## Isolated work surface

The preferred work surface is a Git worktree outside the main checkout:

```bash
git worktree add -b ion/<agent>/<branch-node>/<objective>/<stamp> ../ion-worktrees/<branch-id> <base-ref>
```

A normal branch checkout is acceptable only when the protected checkout will not be mutated and the branch identity is recorded in a start receipt.

## Branch naming

Branch names should be stable enough to route and audit:

```text
ion/<agent>/<branch-node>/<objective-slug>/<YYYYMMDDTHHMMSSZ>
```

Examples:

```text
ion/codex/browser-extension/receipt-tags/20260514T170232Z
ion/mason/kernel/git-containment/20260514T170232Z
ion/nemesis/architecture/recovery-review/20260514T170232Z
```

## Start receipt law

Before material edits, the agent must emit a branch start receipt containing:

- receipt id,
- agent or carrier,
- objective,
- branch name,
- worktree path,
- base branch/ref,
- base commit,
- local branch node path,
- mounted README/AGENTS/capsule surfaces,
- authority posture,
- protected-branch check result,
- and initial test or status posture when feasible.

No start receipt means no claim that the work was lawfully contained.

## Checkpoint law

AI work should be saved as frequent checkpoint commits on the isolated branch.

Checkpoint commits are allowed to be messy. They are not accepted state. Their job is recovery and auditability.

Each checkpoint should have one of these meanings:

- `checkpoint`: coherent partial progress,
- `test-pass`: local tests passed,
- `test-fail`: failure captured intentionally,
- `recovery-note`: mistake captured without landing it,
- `review-ready`: branch is ready for human or Steward review.

Commit messages should include the receipt id or packet id when available.

## Damaged branch law

A broken branch is evidence, not trash.

When a branch is damaged:

1. mark it quarantined,
2. record failing tests and observed defect,
3. preserve the branch and receipts,
4. create a repair branch from the last known-good checkpoint or clean base,
5. import only the useful context: diff summaries, error receipts, failing tests, and lessons,
6. do not silently continue destructive edits on the damaged branch.

This lets ION move to a previous working branch while retaining the knowledge of the damaged attempt.

## Recovery branch law

Recovery branches must record their parentage:

```yaml
recovery_source:
  damaged_branch: ion/codex/browser-extension/receipt-tags/20260514T170232Z
  last_known_good_ref: <sha-or-tag>
  recovered_from:
    - failing_test_summary
    - diff_summary
    - operator_notes
    - receipt_context
  excluded:
    - unsafe_generated_files
    - secrets
    - unreviewed_binary_blobs
```

The recovery branch is a new candidate, not a hidden continuation of the damaged branch.

## Review and merge law

Merge to a protected branch requires:

- operator or authorized Steward approval,
- clean diff summary,
- tests or explicit test waiver,
- secret scan posture,
- receipt export,
- and no unreviewed generated artifacts outside the scope.

Allowed landing modes:

- squash merge with receipt reference,
- merge commit with receipt reference,
- cherry-pick selected commits with receipt reference,
- patch apply after review.

Disallowed landing modes:

- unreceipted direct commit to main,
- force-push to protected branch,
- merge of branch that cannot identify its base,
- accepting "state" from chat text alone.

## Branch delegation relationship

Under the README Branch Context Protocol and Codex Branch Specialist Protocol, the current directory selects the specialist. Under this protocol, the current directory does not authorize edits. It selects the context; the isolated branch/worktree authorizes the edit surface after proof.

## Automation hooks

ION tools should expose a guard that answers:

```yaml
git_edit_posture:
  cwd: <path>
  repo_root: <path>
  branch: <branch>
  base_commit: <sha>
  protected_branch: true|false
  dirty_status: clean|dirty|unknown
  isolated_worktree: true|false|unknown
  verdict: allow_edit|read_only|patch_only|blocked
```

Agents must call or emulate that guard before material edits.

## Success condition

This protocol succeeds when an operator can always:

- inspect what each AI agent changed,
- return to the last working branch,
- keep broken work as evidence,
- launch a repair branch with the mistake context preserved,
- and approve main-tree landing only after proof.
