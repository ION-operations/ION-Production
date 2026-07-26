# Lead Steward Return — First Git Snapshot Precommit Gate Spec

packet_id: PCKT-ION-LEAD-ORCHESTRATION-FIRST-GIT-SNAPSHOT-PRECOMMIT-GATE-SPEC-20260725  
from_role: role.nemesis  
from_domain: domain.artifact_provenance_and_gate_legitimacy  
from_mount: role_nemesis__domain_artifact_provenance_and_gate_legitimacy  
to_role: role.steward  
to_domain: domain.current_phase_orchestration_management  
return_channel: steward_ops  
state: candidate_task_return  
observed_at: 2026-07-26T00:16:00Z  
terminal_verdict: **FIRST_GIT_SNAPSHOT_PRECOMMIT_GATE_SPEC_READY**

### CONTEXT PROOF

| path | lines / note | excerpt |
|---|---|---|
| `.ion/ION_CONTEXT_CAPSULE.yaml` | 8 | `agent_role_id: "role.nemesis"` |
| `.ion/CONTEXT_IDENTITY.json` | 75 | `"verdict": "WORKING_CAPSULE_IDENTITY_READY"` |
| `.ion/HOT_CONTEXT.md` | 6 | `role_id: role.nemesis` |
| `.ion/ACTIVE_CONTEXT_PACKAGE.md` | 66 | `Return contract: The worker must begin with ### CONTEXT PROOF` |
| `.ion/inbox/PCKT-ION-LEAD-ORCHESTRATION-FIRST-GIT-SNAPSHOT-PRECOMMIT-GATE-SPEC-20260725_TASK.candidate.yaml` | 37 | `terminal_verdict: FIRST_GIT_SNAPSHOT_PRECOMMIT_GATE_SPEC_READY` |
| `ION/05_context/current/repository_governance/GITHUB_PLATFORM_READMODEL.candidate.yaml` | 31 | `head_sha: 60255b26a290276c465b937708f2552e400363f6` |
| `.../COMMIT_BOUNDARY_AND_STAGING_LAW.candidate.yaml` | 31 | `pre_commit_gates:` |
| `.../PCKT-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725_DECISION.candidate.yaml` | 133 | `first_snapshot_blockers:` |
| `hygiene/GIT_SOURCE_BOUNDARY_GUARD_20260608.candidate.json` | 124 | `No untracked candidate directory may be staged without an explicit path allowlist` |
| PROVENANCE_HOLD marker | 11 | `"classification": "reconstructed_non_authoritative"` |

## Findings

| Severity | Category | Evidence | Impact | Required fix or gate |
|---|---|---|---|---|
| note | continuity | Standing blockers BLK-REBASE12-FORENSIC, BLK-WORKING-TREE-UNCLASSIFIED, BLK-OPERATOR-PUSH-AUTH remain open per assembly decision | Execution blocked until manifest materialized; push blocked until operator receipt | Follow gate packet execution_status |
| note | authority | Parent tree reports 217151 dirty entries outside manifest | Blanket staging forbidden | GATE-MANIFEST-ALLOWLIST exact equality |
| note | provenance | Reconstructed rebase-12 builder under PROVENANCE_HOLD | Must never enter snapshot | GATE-FORENSIC-HOLD always_exclude |

No blocker defects in the specification artifacts themselves.

## Deliverables

| artifact | path |
|---|---|
| Reusable precommit gate template | `.ion/candidate_deliverables/GIT_SNAPSHOT_PRECOMMIT_GATE.template.candidate.yaml` |
| First snapshot gate packet | `.ion/candidate_deliverables/PCKT-ION-LEAD-ORCHESTRATION-FIRST-GIT-SNAPSHOT-PRECOMMIT-GATE-SPEC-20260725_GATE_PACKET.candidate.yaml` |

## Gate chain summary (14 gates, ordered)

1. **GATE-WORKTREE-ROOT** — separate clean backup worktree at `base_sha`; empty porcelain before copy  
2. **GATE-MANIFEST-ALLOWLIST** — copied files == manifest paths exactly; fail on any extra or missing  
3. **GATE-PROVENANCE-ENTRY** — per-path owner, reason, sha256, size; manifest integrity hash  
4. **GATE-SECRET-SCAN** — filename + redacted content scan; never emit secret values  
5. **GATE-LARGE-FILE** — warn 1 MiB, block 5 MiB, absolute block 100 MiB; archives blocked in wave 1  
6. **GATE-RUNTIME-STATE** — forbid ACTIVE_*, runtime/, caches, bytecode, vault-adjacent paths  
7. **GATE-SYMLINK-DEVICE** — no escaping symlinks; no device/socket/FIFO  
8. **GATE-FORENSIC-HOLD** — exclude reconstructed builder + PROVENANCE_HOLD paths  
9. **GATE-DELETION-ZERO** — zero deletions unless individually declared + nemesis review  
10. **GATE-STAGING-EQUALITY** — `git add --pathspec-from-file` only; staged == manifest  
11. **GATE-COMMIT-BINDING** — base `60255b26…`, branch `backup/codex-ion-carrier-v4-governance-snapshot-20260725`, remote `origin`  
12. **GATE-TREE-HASH** — post-commit tree hash + staged-manifest equality before push  
13. **GATE-PUSH-AUTHORIZATION** — separated; operator receipt; backup branch only  
14. **GATE-DRAFT-PR** — separated; draft PR template + nemesis link; no accepted merge claim  

## Repository binding (first snapshot)

| field | value |
|---|---|
| shell_root | `/home/sev/ION - Production/ION_Developement` |
| base_sha | `60255b26a290276c465b937708f2552e400363f6` |
| source_branch | `codex/ion-custom-gpt-front-door-carrier-v4` |
| target_branch | `backup/codex-ion-carrier-v4-governance-snapshot-20260725` |
| remote | `origin` → `https://github.com/ION-operations/ION-Production.git` |
| worktree | separate clean backup worktree (never stage parent dirty tree) |

## Risk classification

- **Execution risk:** high if manifest bypassed (217k+ unclassified paths)  
- **Secret risk:** mitigated by dual-layer scan with redacted output contract  
- **Provenance risk:** mitigated by per-path hash ledger + tree-hash recomputation  
- **Authority risk:** low for this turn — specification only, no git mutation performed  

## Verdict

`FIRST_GIT_SNAPSHOT_PRECOMMIT_GATE_SPEC_READY` — gate law is specified and reusable; **execution remains blocked** until `FIRST_GIT_SNAPSHOT_MANIFEST.candidate.yaml` is materialized by branch-fabric owner.

## Blockers (execution, not spec)

- BLK-WORKING-TREE-UNCLASSIFIED — manifest empty  
- BLK-OPERATOR-PUSH-AUTH — standing operator gate for push  
- BLK-REBASE12-FORENSIC — builder paths must stay absent from manifest  

## Recommended next packets

1. **domain.context_graph_branch_fabric** — tier classification + manifest materialization at `ION/05_context/current/repository_governance/FIRST_GIT_SNAPSHOT_MANIFEST.candidate.yaml`  
2. **domain.context_systems** — git snapshot receipt templates (already queued)  
3. **operator** — push authorization receipt after local commit gates pass  

## Steward integration notes

- Register `gate.git_snapshot.*` entries in GATE_REGISTRY when operator ratifies hard mode.  
- Until manifest exists, do not spawn Mason landing or any staging executor.  
- Draft PR gate is witness-only until GitHub platform templates land.

## Non-claims

candidate_only · specification_only · no_git_mutation · no_secret_content_output · no_accepted_state
