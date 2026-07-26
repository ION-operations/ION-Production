# Lead Orchestration Return — GitHub Repository Governance Domain Assembly

packet_id: PCKT-ION-LEAD-ORCHESTRATION-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725  
from_role: role.domain_fission_architect  
from_domain: domain.domain_mitosis_and_agent_society_formation  
from_mount: role_domain_fission_architect__domain_domain_mitosis_and_agent_society_formation  
to_role: lead_orchestration_carrier  
return_channel: lead_orchestration  
state: candidate_task_return  
observed_at: 2026-07-25T23:58:00Z  
task_class: domain_ownership_and_activation_assembly  
carrier: cursor_agent  
model: composer-2.5  
terminal_verdict: **GITHUB_REPOSITORY_GOVERNANCE_DOMAIN_ASSEMBLY_PROPOSED**

### CONTEXT PROOF

- `.ion/ION_CONTEXT_CAPSULE.yaml` — 95 lines — `agent_role_id: "role.domain_fission_architect"`
- `.ion/CONTEXT_IDENTITY.json` — 77 lines — `"verdict": "WORKING_CAPSULE_IDENTITY_READY"`
- `.ion/HOT_CONTEXT.md` — 32 lines — `candidate_mount_only: true`
- `.ion/ACTIVE_CONTEXT_PACKAGE.md` — 447 lines — `write_posture: none`
- `.ion/inbox/PCKT-ION-LEAD-ORCHESTRATION-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725_TASK.candidate.yaml` — 70 lines — `terminal_verdict: GITHUB_REPOSITORY_GOVERNANCE_DOMAIN_ASSEMBLY_PROPOSED`
- `candidate_founding_domains/domain.artifact_provenance_and_gate_legitimacy/domain.artifact_provenance_and_gate_legitimacy.domain.candidate.yaml` — 43 lines — `priority: P0`
- `codex_agent_mounts/role_monolith_decomposition_cartographer__domain_context_graph_branch_fabric/.ion/DOMAIN.yaml` — 15 lines — `domain_id: "domain.context_graph_branch_fabric"`
- `codex_agent_mounts/role_nemesis__domain_artifact_provenance_and_gate_legitimacy/.ion/inbox/PCKT-ION-LEAD-ORCHESTRATION-REBASE-12-BUILDER-BYTE-PROVENANCE-FORENSIC-20260725_TASK.candidate.yaml` — 52 lines — `git_tracked: false`

## Domain ownership decision

**Verdict:** evolve existing specialty domains with explicit sub-charters plus **one narrow new platform domain**. **Do not** create a monolithic Git steward under Steward.

| Concern | Lawful owner | Rationale |
| --- | --- | --- |
| Repository identity & remote registry | `domain.context_graph_branch_fabric` | Branch/repository graph and monolith cartography |
| Branch naming, upstream, merge-base, divergence | `domain.context_graph_branch_fabric` | Branch-fabric law, not orchestration |
| Working-tree tier inventory & path cartography | `domain.context_graph_branch_fabric` + `domain.artifact_provenance_and_gate_legitimacy` | Topology vs provenance classification |
| Change-set ownership & commit-boundary manifests | `domain.artifact_provenance_and_gate_legitimacy` | Birth receipt and gate legitimacy |
| Pre-commit gates (secrets, LFS, generated, deletions) | `domain.artifact_provenance_and_gate_legitimacy` (+ Nemesis review) | Existing GATE_REGISTRY posture |
| Continuity templates (orientation, commit plan, push auth, PR, rollback) | `domain.context_systems` | Template-governed carrier resume |
| Accepted merge / rank boundary | `domain.state_rank_and_receipt_truth` | Fan-in ledger before accepted truth |
| GitHub settings, branch protection, Actions, CODEOWNERS | **`domain.github_repository_platform_governance`** (new candidate) | Platform surface only |
| Tag / production release | `domain.release.release_readiness` (deferred) | Expansion-graph release family |
| Bounded repo landing after manifest | `domain.product_and_implementation_domain_formation` / Mason | Executes only post-gate |

**Explicit non-owner:** `domain.current_phase_orchestration_management` / Steward retains turn-packet and integration-queue orchestration only — **read-only consumer** of repository state summary, not Git owner.

**Rejected:** monolithic Git steward; Steward evolution in place; blanket `git add .`; subrepo split before classified snapshot; MINI/CAPSULE as git truth.

## Relationship map

```
[Repo graph + branch law] context_graph_branch_fabric
       │ identity / merge-base / backup branch naming
       ▼
[Inventory tiers + commit manifests] artifact_provenance_and_gate_legitimacy
       │ pre-commit gates                    ▲
       ▼                                     │ path ownership
[Continuity templates] context_systems       │
       │                                     │
       ├── read-model ──► STEWARD_REPO_AWARENESS (steward read-only)
       │
[GitHub platform] github_repository_platform_governance
       │ branch protection / Actions / CODEOWNERS read-model
       ▼
[Accepted merge] state_rank_and_receipt_truth
       ▼
[Release tag] release.release_readiness (deferred)
```

## Continuity and template system

Persistent resume surfaces (candidate paths):

- `ION/05_context/current/repository_governance/REPOSITORY_IDENTITY_REGISTRY.candidate.json`
- `ION/05_context/current/repository_governance/REPOSITORY_STATE_SUMMARY.candidate.md`
- `ION/05_context/current/repository_governance/WORKING_TREE_INVENTORY.candidate.json`
- `ION/05_context/current/repository_governance/COMMIT_BOUNDARY_MANIFEST.candidate.yaml`

Template activation packet: `PCKT-CONTEXT-SYSTEMS-GIT-SNAPSHOT-RECEIPT-TEMPLATES-20260725` → six receipt templates under `ION/07_templates/repository_governance/`.

Folder-local specialist mounts should bind `.ion/` continuity for:

- `role.monolith_decomposition_cartographer` / branch fabric
- `role.nemesis` / artifact provenance
- `role.context_cartographer` / context systems
- `role.mason` / GitHub platform read-model (phase 2)

## Current repository risk classification

| Fact | Class | Risk |
| --- | --- | --- |
| Shell root `ION_Developement` | lawful carrier git toplevel | low if respected |
| Remote `ION-operations/ION-Production` | primary origin (HTTPS) | medium — push auth is operator gate |
| Branch `codex/ion-custom-gpt-front-door-carrier-v4` | feature carrier lane | medium — not protected-main |
| Working tree | very large preexisting dirty | **high** — blanket commit unsafe |
| `immediate_blanket_commit_safe: false` | packet attestation | **critical block** |
| Rebase-12 builder | `git_tracked: false`, overwrite incident | **critical** — BLK-REBASE12-FORENSIC open |
| Generated `ACTIVE_*` runtime JSON | T2 tier | high mis-stage risk |
| Vault / credentials paths | T4 tier | **critical** — hard forbid staging |
| Missing symlinks / branch export paths | T6 tier | high — deletion gate required |

## First safe snapshot plan

| Phase | Action | Owner | Git mutation | Gate |
| --- | --- | --- | --- | --- |
| **0** | Read-only orientation + inventory JSON | branch_fabric | none | `PCKT-BRANCH-FABRIC-REPOSITORY-ORIENTATION-READONLY-20260725` |
| **0b** | Close rebase-12 byte + runtime forensics | artifact_provenance / nemesis + runtime_cartographer | none | Nemesis verdict ≠ HOLD |
| **1** | Pre-commit gate spec + gitignore/LFS proposal | artifact_provenance | none | `PCKT-ARTIFACT-PROVENANCE-PRE-COMMIT-GATE-SPEC-20260725` |
| **1b** | Continuity receipt templates | context_systems | none | template curator review optional |
| **2** | GitHub platform read-model | github_platform / mason | none | no API mutation |
| **3** | First domain-scoped commit boundary manifest | domain_fission_architect | **proposal only** | inventory + forensic closure |
| **4** | Operator-authorized local commit on backup branch | branch_fabric + operator | add+commit | manifest + gates + receipt |
| **5** | Remote backup branch push | operator | push to `backup/*` | push authorization receipt |
| **6** | Draft PR | github_platform | none on settings | Nemesis non-block |
| **7** | Accepted merge | state_rank + steward | merge via GitHub | integration queue |
| **8** | Tag / release | release_readiness | tag | separate operator gate |

**Repository shape:** remain **monolithic**; use **tier logical partitions** (T0–T6) — no subrepo split until after first classified snapshot.

**Authority distinction:**

- Local Git save ≠ remote backup ≠ draft PR ≠ accepted merge ≠ production release.

## Activation packet set

| Packet | Assigned domain / role | Phase |
| --- | --- | --- |
| `PCKT-BRANCH-FABRIC-REPOSITORY-ORIENTATION-READONLY-20260725` | context_graph_branch_fabric / monolith_decomposition_cartographer | 0 |
| `PCKT-ARTIFACT-PROVENANCE-PRE-COMMIT-GATE-SPEC-20260725` | artifact_provenance / nemesis | 1 |
| `PCKT-CONTEXT-SYSTEMS-GIT-SNAPSHOT-RECEIPT-TEMPLATES-20260725` | context_systems / context_cartographer | 1 |
| `PCKT-GITHUB-PLATFORM-BRANCH-PROTECTION-READMODEL-20260725` | github_repository_platform_governance / mason | 2 |
| `PCKT-FIRST-SNAPSHOT-BOUNDARY-AFTER-REBASE12-CLOSURE-20260725` | domain_mitosis / domain_fission_architect | 3 |

## Commit / push / PR / release gate model

See `COMMIT_BOUNDARY_AND_STAGING_LAW.candidate.yaml` — authority ladder L0–L6 with `GATE-FORENSIC-HOLD` blocking any commit while rebase-12 forensics remain open.

## Metrics

See `GITHUB_REPOSITORY_GOVERNANCE_METRICS.candidate.yaml` — baseline targets include zero blanket-add incidents and 100% commits with domain manifest attachment once staging begins.

## Forbidden actions — confirmed not performed

- git add, commit, push
- branch switch or checkout
- remote or repository setting change
- destructive reset
- secrets access

## Deliverables

| artifact | path |
| --- | --- |
| Decision | `.../evolution_packets/PCKT-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725_DECISION.candidate.yaml` |
| Registry contract | `.../evolution_packets/REPOSITORY_IDENTITY_AND_REMOTE_REGISTRY.candidate.yaml` |
| Inventory tiers | `.../evolution_packets/WORKING_TREE_INVENTORY_TIERS.candidate.yaml` |
| Staging law | `.../evolution_packets/COMMIT_BOUNDARY_AND_STAGING_LAW.candidate.yaml` |
| Metrics | `.../evolution_packets/GITHUB_REPOSITORY_GOVERNANCE_METRICS.candidate.yaml` |
| Own-mount receipt | `.ion/receipts/20260725T235800Z_PCKT-ION-LEAD-ORCHESTRATION-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725_OWN_MOUNT_RECEIPT.candidate.json` |
| Lead return (this file) | `.ion/outbox/20260725T235800Z_PCKT-ION-LEAD-ORCHESTRATION-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725_LEAD_ORCHESTRATION_RETURN.candidate.md` |

## Non-claims

Candidate-only. No accepted state, registry promotion, git mutations, first snapshot execution, or push authorization.
