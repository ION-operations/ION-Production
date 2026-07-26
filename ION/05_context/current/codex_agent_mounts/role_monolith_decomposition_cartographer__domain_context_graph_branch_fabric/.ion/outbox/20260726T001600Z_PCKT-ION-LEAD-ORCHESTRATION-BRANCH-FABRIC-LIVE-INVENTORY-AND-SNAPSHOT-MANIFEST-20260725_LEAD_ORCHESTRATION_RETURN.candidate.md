# Lead Orchestration Return — Live Repository Inventory and First Snapshot Manifest

packet_id: PCKT-ION-LEAD-ORCHESTRATION-BRANCH-FABRIC-LIVE-INVENTORY-AND-SNAPSHOT-MANIFEST-20260725  
from_role: role.monolith_decomposition_cartographer  
from_domain: domain.context_graph_branch_fabric  
from_mount: role_monolith_decomposition_cartographer__domain_context_graph_branch_fabric  
to_role: lead_orchestration_carrier  
return_channel: lead_orchestration  
state: candidate_task_return  
observed_at: 2026-07-26T00:16:00Z  
carrier: cursor_agent  
model: composer-2.5  
terminal_verdict: **LIVE_REPOSITORY_INVENTORY_AND_FIRST_SNAPSHOT_MANIFEST_READY**

### CONTEXT PROOF

| path | lines / note | excerpt |
| --- | --- | --- |
| `.ion/ION_CONTEXT_CAPSULE.yaml` | 96 | `agent_role_id: "role.monolith_decomposition_cartographer"` |
| `.ion/CONTEXT_IDENTITY.json` | 77 | `"verdict": "WORKING_CAPSULE_IDENTITY_READY"` |
| `.ion/HOT_CONTEXT.md` | 32 | `candidate_mount_only: true` |
| `.ion/ACTIVE_CONTEXT_PACKAGE.md` | 192 | `write_posture: none` |
| `.ion/inbox/PCKT-ION-LEAD-ORCHESTRATION-BRANCH-FABRIC-LIVE-INVENTORY-AND-SNAPSHOT-MANIFEST-20260725_TASK.candidate.yaml` | 51 | `terminal_verdict: LIVE_REPOSITORY_INVENTORY_AND_FIRST_SNAPSHOT_MANIFEST_READY` |
| `evolution_packets/COMMIT_BOUNDARY_AND_STAGING_LAW.candidate.yaml` | 62 | `manifest_path: ION/05_context/current/repository_governance/COMMIT_BOUNDARY_MANIFEST.candidate.yaml` |
| `evolution_packets/WORKING_TREE_INVENTORY_TIERS.candidate.yaml` | 72 | `T2_generated_runtime_active` |
| `domain.github_repository_platform_governance.domain.candidate.yaml` | 85 | `domain_id: domain.github_repository_platform_governance` |
| Nemesis provenance-hold marker | 45 | `"must_not_execute": true` |

## Summary

Compiled parent-provided live Git evidence into four mount-local governance artifacts. Defined wave-0 commit boundary as **repository governance domain assembly + provenance-hold witness surfaces only**, with explicit excludes for dirty-tree bulk, runtime ACTIVE state, reconstructed rebase-12 builder source, secrets, archives, and unrelated deletions.

**Clean backup worktree posture:** propose `backup/ion-governance-snapshot-wave0-20260725` from HEAD `60255b26…` in a separate worktree; never stage from the 217151-entry dirty active tree.

**Carrier limitation:** read-only git verification was blocked in this shell session; inventory counts are bound to parent `live_parent_carrier_evidence`, not stale witness files.

## Repository identity

| Field | Value |
| --- | --- |
| Git toplevel | `/home/sev/ION - Production/ION_Developement` |
| HEAD | `60255b26a290276c465b937708f2552e400363f6` |
| Branch | `codex/ion-custom-gpt-front-door-carrier-v4` |
| Upstream | aligned (0 ahead / 0 behind) |
| vs `origin/main` | 115 ahead / 0 behind; merge-base `14b617e1…` |

## Working tree inventory (live parent evidence)

| Class | Count |
| --- | --- |
| Total porcelain | 217,151 |
| Untracked | 197,991 |
| Deleted | 18,915 |
| Modified | 245 |

Dominant prefixes: `projects/` (110,643), `ION/` (67,808), `ION_GPT_STATE/` (17,950). Filename-risk signals: 9,247 binary/archive patterns, 1,714 secret-name-risk paths (presence-only audit).

## Deliverables (mount-local)

| Artifact | Path |
| --- | --- |
| Repository identity registry | `REPOSITORY_IDENTITY_REGISTRY.candidate.json` |
| State summary | `REPOSITORY_STATE_SUMMARY.candidate.md` |
| Working tree inventory | `WORKING_TREE_INVENTORY.candidate.json` |
| Commit boundary manifest | `COMMIT_BOUNDARY_MANIFEST.candidate.yaml` |
| Own-mount receipt | `.ion/receipts/20260726T001600Z_…_OWN_MOUNT_RECEIPT.candidate.json` |

## First snapshot manifest highlights

- **Include:** GitHub platform governance charter, repository-governance evolution packets, platform read-model/CODEOWNERS proposal, domain-fission assembly return/receipt, Nemesis/runtime governing forensic receipts, rebase-12 provenance-hold forensic folder (not builder source), this mount's four new artifacts.
- **Exclude:** `_build_rebase12_package.candidate.py`, `ACTIVE_*`, `projects/`, vault/credentials, broad receipt dumps, deletions, binaries.
- **Proposed backup branch:** `backup/ion-governance-snapshot-wave0-20260725`
- **Draft PR base:** `main` (after L3 push + gates)

## Blockers before execution

| ID | Effect |
| --- | --- |
| BLK-REBASE12-FORENSIC | `GATE-FORENSIC-HOLD` — L2 commit forbidden until closure |
| BLK-OPERATOR-PUSH-AUTH | L3 remote backup requires operator receipt |

## Forbidden actions — confirmed not performed

- git add, commit, push
- branch or worktree creation
- checkout, reset, remote mutation
- secret content reads

## Non-claims

Candidate-only promotion bundle for parent carrier. No accepted state, no git mutation, no push authorization.
