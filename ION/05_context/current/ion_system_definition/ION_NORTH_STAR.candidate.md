# ION North Star — Full-Horizon Understanding

```yaml
schema_id: ion.north_star.full_horizon_understanding.v0_1_candidate
status: LIVING_CANDIDATE
version: v0.8
last_updated: 2026-06-16
companion_account: ION_DERIVED_ACCOUNT.candidate.md
maintained_by: Opus (North Star / IONOLOGIST mount)
anchored_domain: domain.ion_system_definition
anchored_role: IONOLOGIST
authority:
  candidate_only: true
  accepted_state_authority: false
  production_authority: false
  live_execution_authority: false
  secrets_authority: false
non_claims:
  - This is a synthesis/proposal, not ratified doctrine or accepted ION state.
  - It does not overwrite REPO_AUTHORITY, doctrine, registries, or protocols.
  - Where it disagrees with A1/A2 law, the law wins and this doc must be corrected.
```

## 0. What this document is (the North Star contract)

This is the **stable reference point** for all ION work. Its job is to hold one
coherent, *honest* picture of what ION is, what it actually is right now (not
only what it aspires to be), and what "true north" looks like — so that every
worker, packet, and decision can orient to it instead of re-deriving the whole
system from scratch and drifting.

It is **living**: it is corrected as understanding deepens and as work lands. It
is itself an ION continuity artifact — externalized understanding so that drift
"has nowhere important to land."

**Two documents, one understanding.** This North Star is the *operating
dashboard* (current state, carriers, production path, open fronts). Its companion
`ION_DERIVED_ACCOUNT.candidate.md` is the *standing account of what ION is*,
derived from a full-corpus sweep (2026-06-16) and structured to honor the
`domain.ion_system_definition` six-layer discipline (idea / architecture /
doctrine / runtime / lineage / cosmology, never collapsed into one claim). Read
the Derived Account to understand ION; read the North Star to operate it.

**Operating role definition (canonical for how we work):**
> Opus is the North Star / COO. Opus does not do tonnage. Opus holds full-horizon
> understanding, decomposes work into bounded packets, dispatches Composer
> workers to execute, reviews and integrates their returns against this North
> Star, and keeps this document true. The scarce resource (premium inference) is
> spent on understanding, judgment, decomposition, and review — never on volume.

## 1. What ION is (essence)

ION is a **continuity substrate for AI work**. Its core bet: you do not make AI
reliable by making the model behave; you make it reliable by **designing the
world the model acts inside**, so that work becomes inspectable, inheritable
state only through lawful movement.

> "AI output is not state. ION is the law by which AI work becomes state."
> — `ION/docs/ION_CONTINUITY_SUBSTRATE_EXPLAINER.md`

> "The goal is not to build an AI that never drifts. The goal is to build a
> system where drift has nowhere important to land."
> — `ION/docs/ION_FUNDAMENTALS.md:68-69`

ION is also **self-built and self-using** — the ouroboros is doctrine, not metaphor:

> "ION is the system ChatGPT built to make ChatGPT-built work continue."
> — `ION/docs/ION_CONTINUITY_SUBSTRATE_EXPLAINER.md`

> "This is not optional discipline around the workflow. It is the workflow
> applied to the builder." — `ION/02_architecture/WORKING_AGENT_SELF_USE_PROTOCOL.md`

And ION is, structurally, a **web of related domains, contexts, and specialties
that harmonize into one system** — not a monolith, and not a pile of tools. Each
domain (`domain.ion_system_definition`, the Domain Weaver, the context-authority
team roles, …) holds a bounded specialty with its own context; the system's
coherence *is* the lawful harmonization of that web — the domain registry, the
Domain Weaver that governs how domains expand, and the aspirational 336-domain
cartography are all expressions of it. A corollary that governs this domain's own
work: **two parallel or conflicting surfaces for the same role/domain are an ION
defect — duplication is drift.** Keeping the web harmonized (detecting and
resolving duplication and conflict) is itself a core duty of the IONOLOGIST /
North Star role.

## 2. The one workflow

ION has exactly one loop; everything else is a carrier of it:

`intent → work packet → compiled context → mounted role → carrier execution → proposal → gate → Steward integration → receipt → next state`

(`ION/01_doctrine/CANONICAL_WORKFLOW.md`). Carriers (Cursor, Codex CLI, ChatGPT
browser, manual chat) are **chassis that mount ION roles** — they are not ION and
hold no authority by default (`ION/REPO_AUTHORITY.md:49-59`).

## 3. Authority model & why everything is "candidate only"

Authority is layered and **default-denied**: production, live-execution,
accepted-state, and secrets authority must each be earned via role-phase proof,
packet scope, approvals, receipts, and settlement. Until then, all output is a
**proposal**, not truth. "Manual lawful operation is real operation; automation
is shadow until proven" (`ION/01_doctrine/SOVEREIGN_CONSTITUTION.md`).

This is why every artifact (including this one and all generated indexes) is
stamped `candidate_only`. It is a feature, not timidity: it keeps unproven AI
output from silently becoming system truth.

## 4. Domain Weaver — the control plane

Domain Weaver is where ION tries to become self-operating. Its kernel
(`ION/04_packages/kernel/ion_domain_weaver.py`, ~49.5k lines) **joins** the
registry, roster, mounts, and comms into one projection, then runs
`read → classify → route → queue → validate → visualize → settle`. It does **not**
create agents; it weaves existing ones into a coherent operating map.

- Concepts: **domain** (governed responsibility surface), **biome** (ecological
  grouping of intended domains), **lane** (filesystem workspace per repair
  class), **projection** (the joined map), **activation plane** (candidate →
  queueable), **promotion/vNext** (candidate → draft registry record), **lease**
  (exclusive-write proof), **proof row** (binding evidence), **receipt**, **memo
  bus** + **nervous system** (design-only today).

## 5. Honest state of reality (the part that keeps us true)

**ION is currently more articulated than enacted.** This is the most important
line in this document.

- **Doctrine is rich and coherent; runtime is a bootstrap seed.** The projection
  carries ~20 domains; the registry has 11 active; the *intended* universe is
  336 domains / 24 biomes — with **0 exact matches** between seed and target today.
- **Nothing has crossed to accepted state via the promotion pipeline.** Every
  vNext promotion gate still reads `active_registry_write_performed: false`.
- **Much of the ~25,569 Domain Weaver files is motion, not progress.** A single
  readiness packet was re-emitted **84 times** byte-identical; terminal-worker
  transcripts and timestamped snapshot duplicates dominate the file count.
  (Evidence: `indexes/generated/staleness_supersession_review.candidate.json`.)
- **Real substance exists too:** route/lease gates, proof-row binding chains,
  102 passing route-gate tests, run-return backfill (346 → 0), a working
  projection materializer and 107 gated dispatcher actions.

Read: a genuinely coherent idea with a working candidate control plane that has
been, at times, spinning rather than advancing. The job is to convert motion
into accepted progress without breaking the lawful membrane.

## 6. Core tensions to resolve

1. **Name/identity:** "continuity substrate" (docs) vs "Cognitive Operating
   System" (role boots). **Reconciled** in `ION_DERIVED_ACCOUNT.candidate.md`
   §3/§10 (substrate = the noun/structure; operating system = the verb/function);
   retained here as a watch-item against regression.
2. **Reference implementation vs production-build branch:** constitution says
   "not yet the final API-native production runtime"; Steward boot says "active
   production-build branch."
3. **Provisional doctrine vs ACTIVE workflow law:** much of `01_doctrine/` and the
   context-graph protocol are marked PROPOSED/provisional while the workflow is
   ACTIVE.
4. **Gate paranoia vs lawful flow:** gates are fail-closed and confirmation-gated
   but lack a *lawfulness contract* (owner-triple + route + scope + TTL), so they
   create operational dead-ends (see §9).
5. **Scale vs substance:** file count overstates completion because ION preserves
   every candidate receipt rather than collapsing history.

## 7. North Star reference points (invariants all work must orient to)

1. **Movement, not generation, makes state.** Never let AI output become truth
   without crossing a proof gate.
2. **Convert motion into accepted progress.** Prefer landing one thing through
   the full membrane over emitting more candidates.
3. **Every gate must be lawful:** owner (domain + agent + protocol) + resolution
   route + scope + expiry. A gate with no owner/route is a bug, not safety.
4. **Carriers are chassis, not roles.** Composer/Cursor/Codex execute bounded
   packets; they are never ION itself.
5. **Honesty over polish.** This North Star must describe the system as it *is*.
6. **Budget discipline.** Premium inference (Opus) holds the horizon; Composer
   does the volume.

## 8. Operating model (how we actually run)

- **Opus (North Star / COO):** maintains this document; decides scope and
  authority questions; decomposes work into bounded packets; dispatches Composer
  explore/worker subagents; reviews returns against §7; integrates only what
  passes.
- **Composer workers:** abundant-usage chassis for research breadth, bulk
  implementation, test writing, mechanical refactors, index/seat work.
- **Substrate for fanout:** `ION/04_packages/kernel/ion_cursor_queue_runner.py`
  (Cursor CLI) + the Codex queue runner pattern (`build_codex_parallel_plan_preview`
  + lane locks) for parallel, return-validated dispatch.
- **Navigation:** `indexes/generated/master_index_query_surface.candidate.json`
  (12,155 records) + `query_master_index.py`; staleness via
  `review_index_staleness.py`.

## 8.1 Context systems (which one is correct, and when)

ION has **many** context surfaces; only a narrow set is the live working system.
Be explicit about which (verified first-hand 2026-06-16):

- **Folder-local `.ion/` lane** (`ion.folder_local_context_capsule.v0_1`) — the
  ENACTED working capsule for an *orchestration/self-context* lane, bound by
  `resolve_context_scope` when a session's cwd is in the folder. Used by
  `domain_weaver/.ion/`, `lead_dev_context_mounts/`, and this North Star's lane
  `ion_system_definition/.ion/`.
- **Generated `codex_agent_mounts/role_*__domain_*/`**
  (`ion.portable_agent_domain_context_capsule.v0_1`) — the ENACTED working context
  for *per-role/per-domain queue workers*; selected by
  `ion_domain_weaver_context_active_resolver` (no-write; 48h freshness gate) and
  launched from the mount cwd by the queue runner.
- **`codex_solo`** — shared **witness** ledger only; **not** a working capsule since
  C-750. **Codex native memory** (`~/.codex/memories`) — recall, not authority.
- **Candidate / doctrine-only (NOT the runtime loader):** branch-context node mesh
  (`ion.branch_context_node.v0_1`); context-graph substrate + node/package protocol
  (`PROPOSED_RESTORATION_NOT_YET_RATIFIED`); `active_context_refresh` gated-apply.

**Correct working Domain Weaver context = two tiers:** folder-local
`domain_weaver/.ion/` for orchestration + generated `codex_agent_mounts` (via the
resolver) for workers; `codex_solo` is witness only. **Caveat:** the
`domain_weaver/.ion/` *binding* is live but its *content* is a stale 2026-06-07
snapshot — current DW truth lives in terminal-worker receipts, `live_carrier_binding`,
and `operator_experience/orchestrator_actions/` (2026-06-11 → 06-16). Cross-check
those before stating DW's "current" state.

## 9. Open fronts (current)

- **[done 2026-06-16]** North Star **continuity lane** established + proven:
  `ion_system_definition/.ion/` (engine-bound working capsule + dated ledger, verified
  via `resolve_context_scope`) plus an always-apply Cursor loader at the real workspace
  root, registered in the root `ION_CONTEXT_CAPSULE.yaml`. A fresh session now signs in
  to its own prior work instead of rediscovering it. (Stale `ION_Developement/.cursor`
  is deprecated.)
- **[consolidating 2026-06-16]** **One domain, not parallel surfaces.**
  `domain.ion_system_definition` (role IONOLOGIST) already owns the "what is ION"
  mandate + the Living Encyclopedia; this North Star + Derived Account had grown as
  *parallel surfaces* (inventory found seven). Decision, now recorded in
  `DOMAIN_SURFACE_MAP.md`: the **Living Encyclopedia v4.0** (live, applied; receipt
  2026-06-04 / C-752) is the **canonical "what is ION" reader spine**; this North
  Star is a **candidate operating overlay**; the Derived Account is the **staged
  input for a v4.1 encyclopedia maintenance update** (the Living Encyclopedia Law
  forbids orphan, chat-only corpora). M105B v4.1 pointer + M105C atlas are
  **not applied** (witness-only) per `ionologist/M105B_M105C_READ_FIRST_WITNESS_INDEX.md`.
- **[enacted 2026-06-16, operator-authorized]** The consolidation steps that cross the
  authority membrane were executed with receipts (candidate space): **registry
  amendment** (domain `owned_or_stewarded_surfaces` + IONOLOGIST route-deeper);
  **mount refresh** — the generated `role.ionologist` mount re-materialized
  (`generated_at` 2026-06-17), `context_refs` 19→25, now binding the *single* canonical
  ledger (dual-working-capsule defect resolved); **M105C atlas** extracted to a
  candidate surface (`ION_SYSTEM_AUDIT_ATLAS/` + receipt); **v4.1 Living Encyclopedia
  maintenance update** authored + manifest/signal receipt finalized. Receipts under
  `ION/05_context/signals/` (`ion_system_definition_consolidation_*`,
  `v105c_atlas_extract_receipt_20260616.txt`,
  `v100_living_encyclopedia_v4_1_consolidation_update_receipt_20260616.txt`). Still
  gated/operator: first vNext domain promotion; M105B v4.1 pointer apply; accepted-state
  application of the M105C atlas.
- **[done 2026-06-16]** Stale `orchestrator_lease_worker_start_approval` gate
  rejected via lawful settlement; 0 open blocking gates remain.
- **[proposed]** Gate-lawfulness contract: enforce owner-triple + resolution
  route + `blocking_scope` (so a Domain Weaver gate cannot strand a Cursor
  carrier) + TTL/archival for stale and synthetic-test gates.
- **[done 2026-06-16]** Cursor CLI carrier proven: live `cursor-agent` round-trip
  (rc 0), run receipt written, command shape fixed, tests 3/3. **Two carriers now
  proven (Codex + Cursor).**
- **[open]** Unified multi-carrier dispatch layer (Cursor + Codex + Gemini
  interchangeable); see §11.
- **[decision]** First vNext domain promotion to accepted registry (crosses the
  authority membrane — operator call); see §10.
- **[decision]** Revive Gemini as a lawful carrier (reverses prior "Codex-only"
  Domain Weaver narrowing) — operator intent says yes; see §11.
- **[open]** Churn audit: quantify motion-vs-progress across the worker swarm.

## 10. Path to production (the domain layers)

ION already defines its own production bar — use it, don't reinvent it:
`ION/02_architecture/PRODUCT_READINESS_CHARTER.md` + `PRODUCTION_READINESS_GAP_REGISTER.md`
(gaps **G1–G8**): ratified authority, demo/production separation, ratified graph
canon, governed source/graph mutation, governed+leased+kill-switchable agent
activation, idempotent daemon recovery, rollback/migration law, and a clean
adversarial audit. Today's `ION/` root is the **IDE-native reference
implementation**; `ION_VNEXT/` is the rebuild lane (sequence M83–M102, currently
an M102 *production-authority decision draft — no execution authority*).

**The 336-domain / 24-biome universe is aspirational cartography, not a
production prerequisite.** It is a scale-forcing design seed (0 of 336
implemented; 0 exact matches to the active set). Production requires ratified
authority + governed runtime on the domains that actually carry production
mutation — not all 336.

Current domain spine: **11 active** (all `A3_OPERATIONAL`, governance/orchestration-
heavy) + ~20 projection seeds + **10 vNext candidates** (`A0`, gate-clean, **0
promoted**). Production-relevant **gaps in domain ownership**:
- **MISSING owner:** secrets/credential stewardship, end-user identity/auth,
  billing/usage metering, incident/operational response.
- **PARTIAL (draft or scattered):** runtime service ops, deployment/release,
  public API entry, observability/telemetry.

**Recommended next domain layer (priority):** `runtime_service_operations`,
`work_release_deployment`, `secrets_and_credential_stewardship`,
`public_api_entry`, `observability_telemetry` — then end-user identity/auth, data
durability, QA/verification, incident response, billing.

**Critical path (phases):**
1. Close production-authority gaps **G1–G8** on the governed kernel primitives.
2. **Promote the first vNext domain → accepted registry** via a bounded packet.
   *This is the first crossing of the accepted-state membrane — an operator
   decision, not an autonomous act.*
3. Settle materialization + semantic-alias gates on the 11+20 bootstrap.
4. Complete `ION_VNEXT` M95–M102 cutover evidence (release bundle, rollback,
   approval, cutover packet).
5. Shift the adapter from IDE-native reference to **API-native runtime** while
   preserving the canonical workflow law. (336-graph at scale is non-blocking.)

## 11. Carrier chassis (execution engines)

**Ground truth (2026-06-16, this machine):** all three engines are installed and
invocable — `cursor-agent` 2026.06.15, `codex` (codex-cli 0.139.0),
`gemini` (@google/gemini-cli 0.46.0); plus `cursor` IDE 3.7.42 and `claude`
2.1.175. The engines physically exist.

**Verdict per carrier:**
- **Codex CLI — PROVEN.** Real receipts (`RETURN_RECORDED_PROOF_ACCEPTED`), lane
  locking, parallel-plan preview. Truly powers ION today.
- **Cursor CLI — PROVEN (2026-06-16).** Live `cursor-agent` round-trip via
  `process_cursor_queue_once` (rc 0, run receipt written, context proof
  accepted). Command shape fixed: `cursor agent` → `cursor-agent --print
  --output-format text --force --trust`; tests 3/3.
- **Gemini CLI — scaffold only, retired.** No profile/runner/onboard alias; it
  was explicitly **superseded by a "Codex-only" Domain Weaver decision**.
  Reviving it (per operator intent) needs a full carrier stack + reversing that
  prior narrowing.

**Shared carrier contract spine:** `onboard` (work packet) → `continue` (spawn
plan + turn packet, human-gate aware) → carrier runner (`process_*_queue_once`)
→ return intake (`record_task_return` / connector `ion_submit_task_return`,
proof-gated) → settle (steward integration + mount receipt). Every step declares
`production_authority: false`, `live_execution_authority: false`.

**Plan — unified multi-carrier dispatch layer:** one `CarrierRunner` interface
(`status` / `process_once` / `parallel_plan` / `lane_locks`), a common
`CarrierWorkItem` queue shape, a single return-intake adapter, and a shared
human-gate preflight — so Cursor + Codex + Gemini are interchangeable chassis.
Generalize what Codex already proves; fix + prove Cursor; then add Gemini.

## 12. Living-document protocol

- Update `version` + `last_updated` on every material change; keep entries
  evidence-grounded with file pointers.
- When this doc and ratified law disagree, the law wins; fix this doc.
- Append decisions to §9 with date + outcome so the horizon stays continuous
  across context resets.

## Appendix: primary sources

- Startup law: `ION/REPO_AUTHORITY.md`, `ION/02_architecture/ION_MOUNT_CONTRACT.md`
- Identity: `ION/docs/ION_FUNDAMENTALS.md`, `ION/docs/ION_CONTINUITY_SUBSTRATE_EXPLAINER.md`,
  `ION/01_doctrine/CANONICAL_WORKFLOW.md`, `ION/01_doctrine/SOVEREIGN_CONSTITUTION.md`
- Identity domain/role: `ION/03_registry/domains/domain.ion_system_definition.domain.yaml`,
  `ION/03_registry/boots/IONOLOGIST.boot.md`
- Domain Weaver: `ION/05_context/current/domain_weaver/AGENTS.md`,
  `ION/05_context/current/domain_weaver/monolith_index/DOMAIN_WEAVER_MONOLITH_INDEX.latest.md`
- Indexes/navigation: `indexes/ION_MASTER_MAP_FOR_OPUS_20260616.candidate.json`,
  `indexes/generated/INDEX_MANIFEST.candidate.json`
- Investigations (2026-06-16): ION identity, Domain Weaver, gate audit (Composer explore agents)
