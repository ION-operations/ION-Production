# Repository State Summary

schema_id: ion.repository_state_summary.v0_1_candidate  
owner_domain: domain.context_graph_branch_fabric  
owner_role: role.monolith_decomposition_cartographer  
materialized_at: 2026-07-26T00:16:00Z  
packet_id: PCKT-ION-LEAD-ORCHESTRATION-BRANCH-FABRIC-LIVE-INVENTORY-AND-SNAPSHOT-MANIFEST-20260725  
state: candidate  
live_execution_authority: false

## Identity

| Field | Value |
| --- | --- |
| Repository ID | `ion-production-ion-developement` |
| Git toplevel | `/home/sev/ION - Production/ION_Developement` |
| Workspace root | `/home/sev/ION - Production` |
| Primary remote | `origin` → `https://github.com/ION-operations/ION-Production.git` |
| Active branch | `codex/ion-custom-gpt-front-door-carrier-v4` |
| HEAD | `60255b26a290276c465b937708f2552e400363f6` |
| Upstream divergence | ahead 0 / behind 0 (aligned) |
| Merge base with `origin/main` | `14b617e1c210c688e2bc9c380503ca756eed941e` |
| Divergence vs `origin/main` | 115 commits ahead, 0 behind (`ahead_only`) |

## Working tree posture

Evidence source: parent carrier `live_parent_carrier_evidence` (2026-07-25 issue). Carrier shell blocked independent read-only git verification in this turn.

| Class | Count |
| --- | --- |
| Total porcelain entries | 217,151 |
| Untracked | 197,991 |
| Deleted | 18,915 |
| Modified | 245 |

**Classification:** very large preexisting dirty tree — `immediate_blanket_commit_safe: false`.

### Dominant top-level path counts (porcelain rollup)

| Prefix | Entries |
| --- | --- |
| `projects/` | 110,643 |
| `ION/` | 67,808 |
| `ION_GPT_STATE/` | 17,950 |
| `AIM-OS/` | 11,846 |
| `ION_Developement/` | 6,703 |

### Filename-risk signals (presence-only; no content reads)

| Risk class | Count |
| --- | --- |
| Binary or archive name patterns | 9,247 |
| Secret-name-risk paths | 1,714 |

## Open blockers affecting snapshot

| ID | Status | Gate |
| --- | --- | --- |
| BLK-REBASE12-FORENSIC | open | `GATE-FORENSIC-HOLD` — no L2 commit until forensic closure |
| BLK-WORKING-TREE-UNCLASSIFIED | closing via this packet | tier manifest required before staging wave |
| BLK-OPERATOR-PUSH-AUTH | standing | no remote push without operator authorization receipt |

## Proposed backup posture (proposal only — no git mutation this turn)

| Surface | Proposal |
| --- | --- |
| Execution model | Separate clean backup worktree from current HEAD; never stage from dirty active worktree |
| Proposed backup branch | `backup/ion-governance-snapshot-wave0-20260725` |
| Base commit | `60255b26a290276c465b937708f2552e400363f6` (current HEAD) |
| Remote backup target | `origin/backup/ion-governance-snapshot-wave0-20260725` (operator push only) |
| Draft PR base | `main` (after remote backup + Nemesis non-block) |

## First snapshot scope (narrow governance wave)

Smallest coherent boundary: **repository governance domain assembly + provenance-hold witness surfaces only**. See mount-local `COMMIT_BOUNDARY_MANIFEST.candidate.yaml` for exact pathspecs, tiers, and excludes.

**Included when provenance permits:** GitHub platform governance domain charter, repository-governance evolution packets, governing Nemesis/runtime forensic receipts, rebase-12 provenance-hold marker evidence (not reconstructed builder source).

**Explicitly excluded:** reconstructed rebase-12 builder, runtime `ACTIVE_*` state, broad receipt dumps, `projects/` corpus, archives/binaries, secret-risk paths, unrelated deletions.

## Authority ladder reminder

Local git save ≠ remote backup ≠ draft PR ≠ accepted merge ≠ production release. Staging requires L1 manifest + gates; commit requires L2 operator authorization + Nemesis non-block; push requires L3 operator receipt.

## Non-claims

Candidate-only inventory and manifest proposal. No git add, commit, push, branch, or worktree creation performed. No secret content reads. No accepted state.
