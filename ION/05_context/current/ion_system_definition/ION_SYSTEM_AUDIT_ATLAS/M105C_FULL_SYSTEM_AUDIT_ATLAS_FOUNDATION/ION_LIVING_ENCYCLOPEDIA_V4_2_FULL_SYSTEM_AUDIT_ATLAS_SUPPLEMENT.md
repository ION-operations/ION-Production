# ION Living Encyclopedia v4.2 — Full System Audit Atlas Foundation

Status: sandbox candidate atlas foundation  
Created: 2026-05-25  
Posture: `LOCAL_SANDBOX_PARTIAL_MOUNT`  
Authority: documentation/currentness planning only. No live repo mutation, no worker start, no queue processing, no invocation submission, no accepted-state claim.

## Purpose

This is the first atlas layer for evolving the living encyclopedia into a full explanation of every ION system and subsystem, their relationships, currentness status, stale risks, proof surfaces, and design-quality gates.

This does not replace the living encyclopedia. It is a candidate supplement to the corrected v4.1 living encyclopedia path:

```text
ION/docs/encyclopedia/ION_Production_Encyclopedia_v4_1_LIVE_M103_M105_DOMAIN_WEAVE_ACTION_BRANCHING_PROOF_NATIVE_CURRENTNESS.md
```

## Source Corpus Boundary

This audit was performed from sandbox files only. It did not mutate the live repo.

|source|sha256|files|dirs|role|
|---|---|---|---|---|
|full_workspace_ION_Developement_zip|7322bda9525d1290883adac99aa6e7d07425104e5bbea7d9b00cea844dc58020|36079|4444|support/witness|
|ion_root_current_zip|c41cf01ba72820849c5bcc8c65b490755498c22109534f0e47a61d44c49f4614|17669|1705|primary|
|ion_root_prior_zip|4ba3ef46ae91faa5c9531c78ea8e93451682528c877355e89341542768bbf23e|16183|1592|support/witness|
|vnext_current_candidate_zip|37bb4e519d5033d4a1d4d182db025880fd303a589ce981f49b3b3999cff5744c|482|72|primary|
|vnext_m102_m104_zip|c4a835f1acd7f2942802c390b8e309ad4356b6ea054dad6cdf90b296fb3a6368|322|67|support/witness|
|needs_routed_source_pool_zip|56c8b0bc5960b89e178bccc70dbf30d407c9c7207c57ad7f416e0279a800401e|278|26|support/witness|
|daimon_source_pool_zip|7d48d5e4e496aa8ee64485c57da378b3f9cad5dea68cba6c6a631085aae4f2a6|19265|2915|support/witness|
|living_encyclopedia_v4_1_update_zip|7fa27d1ff30f1fc0a8159be0b34743ea230723e12dbe94222c441b9ca638262f|7|0|primary|
|living_encyclopedia_pointer_binding_zip|9883f3409656efdf7a30bd413d85df0cb569f4369f524b141d26ff9b140509e9|5|0|support/witness|
|gpt_pro_m105a_m106_witness_zip|78f12619504beb1e3e85e6d3aa73d8a57b5faaf4cc37feb84ea46f5a8bd67943|25|6|support/witness|

## Currentness Caveats

- `ION Developement.zip` is broad and contains the full workspace topology, but its embedded `ION_VNEXT/` is stale relative to `ION_VNEXT_.zip` for Domain Weave surfaces.
- `ION_VNEXT_.zip` is the current sandbox source for vNext Domain Weave files.
- `M105A_CORRECTED_LIVING_ENCYCLOPEDIA_V4_1_UPDATE.zip` is the corrected living-encyclopedia evolution package.
- `ION_VNEXT_M105A_ENCYCLOPEDIA_AND_AGENT_COCKPIT_CONTROL_PLANE_CANDIDATE.zip` is witness material: its M105A side encyclopedia is superseded, while its M106/JOC advisory content is salvageable only after rebasing to the real v4.1 living encyclopedia.
- Any live-repo claim still requires live connector proof or a later local Codex validation packet.

## System Taxonomy v0.1

|system_id|name|authority|next_audit|
|---|---|---|---|
|workspace_topology|Workspace Topology and Source Pools|candidate/currentness-bound; source-pool presence is not authority|build root-by-root lineage table with currentness rank and promotion status|
|living_encyclopedia|Living Encyclopedia and Documentation Spine|A2 documentation context authority; not production ratification; must preserve prior body and add current-state supplements|merge v4.1 into live repo and generate v4.2 atlas supplement from this audit|
|core_law_and_doctrine|Core Law, Doctrine, and Authority Boundaries|mixed: active protocols plus historical/superseded doctrine; requires currentness classification|classify every protocol as active, candidate, historical, superseded, or quarantine|
|registries_schemas_policies|Registries, Schemas, and Policies|active/candidate mix; branch leader registry is draft_non_production|map each registry to consuming kernel modules and tests|
|kernel_runtime|ION Kernel Runtime Modules|active local implementation candidate; tests must be audited for correct law, not just pass/fail|module-by-module map: owner, status, tests, proof contract, prose-proof risk|
|agents_and_agent_domains|Agents, Agent Roles, and Domain-Scoped Operating Environments|partially implemented; target model requires domain-local context/config plus proof-native receipts|build agent/domain registry with executable role vs candidate steward metadata distinction|
|context_systems|Context Systems and Context Packages|active/candidate mix; context is input/custody, not proof or accepted state by itself|separate active current context, archival context, generated context, and private context|
|domain_weave|Domain Weave|core candidate ION substrate; not paused; not accepted ION state; real mutation requires M103F real-use gate and proof-native receipts|separate pure Domain Weave kernel from worker-return lane and audit each M103/M104 result status|
|action_branching|Action/MCP Branching|draft_non_production; read routes plus confirmation-gated mutation routes|branch-by-branch route map with exact handler, authority, and receipt requirement|
|joc_cockpit|JOC / Cockpit / Operator UI|local-only cockpit candidate; must use broker/runner for Start, not raw shell|map panels/endpoints to backend sources and authority boundaries|
|codex_queue_and_workers|Codex Queue, Worker Runner, and CLI Carrier|active candidate local worker lane; proof-boundary defect exists in return acceptance|repair proof-native return intake and map runner lifecycle statuses|
|proof_receipts_custody|Receipts, Custody, Settlement, and Proof-Native Evidence|mixed: receipt infrastructure exists, but prose-proof gates are confirmed defect|define REQUIRED_READ_EVIDENCE, TOUCHED_PATHS, RUN_POSTURE, RETURN_CONTRACT_STATUS schemas and patch gates|
|mcp_actions_chatgpt_bridge|MCP / Actions / ChatGPT Browser Bridge|candidate bridge; current tool surfaces show no production/live authority|map each exposed tool to read/write authority and owner module|
|supabase_mirror|Supabase Mirror / Cockpit Read Model|mirror/read-model only; not chat authority or accepted state|map tables/RLS/contracts and edge/gateway boundaries|
|relay_steward_persona|Relay, Steward, Persona, Front-Stage Council|doctrine and partial kernel support; live full chain requires currentness proof|map actual implemented kernels/tests vs doctrine|
|release_rollback_production_authority|Release, Rollback, and Production Authority|candidate proof surfaces only; no production authority and no live execution authority|derive exact remaining production gates from M102 and v4.1 encyclopedia|
|legacy_donor_archive|Legacy, Donor, Archive, and Reference Roots|reference/source-pool unless promoted by proof-gated packet|source-pool admissibility and promotion-status table|
|known_defects_quarantines|Known Defects and Quarantine Index|active audit finding; not proof that all ION is invalid; enough to require repair before relying on affected lane|expand confirmed/suspect/safe classification across all proof gates|

## Key Design Laws for the Atlas

1. Domain Weave is a core ION substrate, not paused and not downgraded.
2. Model prose is not proof.
3. Runtime receipts and machine evidence are proof.
4. Wrappers are evidence salvage, not root-cause repair.
5. Documentation can explain and govern currentness, but it cannot create accepted state by itself.
6. Domain folder scoping is an operating target for agents, but folder presence is not agent readiness.
7. Action Branching is bounded route/control metadata, not arbitrary execution.
8. Supabase is coordination/persistence/read-model only, not ION authority.
9. JOC/Cockpit is the operator-facing command surface, but UI display must not imply authority not proven by receipts.
10. Tests are not trustworthy unless they encode the correct law.

## Atlas Work Plan

### Phase 1 — Foundation Taxonomy

Completed in this package:
- source corpus manifest,
- system taxonomy,
- first relationship map,
- known stale/quarantine index,
- currentness caveats.

### Phase 2 — System-by-System File Map

For each system, build:
- file inventory,
- owner module,
- status,
- tests,
- proof surfaces,
- authority boundary,
- stale risks,
- relationship edges.

### Phase 3 — Relationship Graph

Create a graph from:
- Doctrine -> Architecture -> Registries -> Kernel -> Context -> Agents -> JOC -> Receipts -> Steward -> Encyclopedia.
- Domain Weave -> domain ownership -> steward review -> impact check -> settlement.
- Action Branching -> route capsules -> gateway/core/codex/agent/supabase branches.

### Phase 4 — Stale and Defect Classification

Classify every system as:
- ACTIVE,
- CANDIDATE,
- WITNESS,
- SUPERSEDED,
- LEGACY_QUARANTINE,
- CONFIRMED_DEFECT,
- SUSPECT,
- SAFE_AFTER_PROOF.

### Phase 5 — Living Encyclopedia v4.2 Integration

After validation, fold this atlas into the living encyclopedia as a v4.2 supplement, preserving the v4.1 body and adding a current-state audit map.

## Non-Claims

- no accepted ION state,
- no production authority,
- no live execution authority,
- no live repo mutation,
- no worker start,
- no queue processing,
- no invocation submission,
- no Supabase mutation,
- no deployment,
- no service restart,
- no Git push,
- no secret access,
- no broad reorganization.

