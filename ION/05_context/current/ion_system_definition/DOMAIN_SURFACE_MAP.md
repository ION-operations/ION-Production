# ION System Definition — Domain Surface Map (consolidation index)

```yaml
schema_id: ion.system_definition.domain_surface_map.v0_1_candidate
status: LIVING_CANDIDATE
created: 2026-06-16
maintained_by: Opus (North Star / IONOLOGIST mount)
domain: domain.ion_system_definition
role: role.ionologist
authority: candidate_only  # no accepted-state / production / live / registry-mutation authority
companions:
  - ION_NORTH_STAR.candidate.md
  - ION_DERIVED_ACCOUNT.candidate.md
```

## Why this file exists

ION is a web of related domains/contexts/specialties that harmonize into one
system. The same law holds *inside* a single domain: **two working capsules, or
two "what is ION" corpora, for one role+domain is a defect — duplication is
drift.** The IONOLOGIST / `domain.ion_system_definition` domain had grown **seven
parallel surfaces** that disagreed on which capsule and which corpus is canonical.

This map is the single index that makes them harmonize: **one role per artifact,
one continuity ledger, one canonical reference corpus**, with everything else
pointing inward instead of competing. It is a *structural map of the domain's own
surfaces* — **not** a third "what is ION" narrative. Narrative canon is the Living
Encyclopedia (below).

## The one domain, distinct artifacts

| Artifact | Single responsibility | Status |
|---|---|---|
| **Registry identity** — `03_registry/boots/IONOLOGIST.boot.md`, `semantic_identities/IONOLOGIST.semantic.yaml`, `domains/domain.ion_system_definition.domain.yaml`, `agent_context_systems/IONOLOGIST.context_system.md`, context-authority team registry | Identity & authority **law** for the role/domain | **Canonical** (ACTIVE registry) |
| **Living Encyclopedia** — `ION/docs/encyclopedia/ION_Production_Encyclopedia_v4_0_LIVE_*.md` + `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json` + `02_architecture/ION_LIVING_ENCYCLOPEDIA_MAINTENANCE_PROTOCOL.md` | **Canonical "what is ION" reference corpus**, governed by the maintenance protocol | **Canonical, applied** (receipt 2026-06-04 / codex_solo C-752) |
| **North Star** — `ion_system_definition/ION_NORTH_STAR.candidate.md` | Living **operating dashboard** (current state, carriers, production path, open fronts) — a candidate *overlay* on the encyclopedia, not a rival corpus | **Candidate** |
| **Derived Account** — `ion_system_definition/ION_DERIVED_ACCOUNT.candidate.md` | Six-layer cited **deep account**; staged **input for the next encyclopedia maintenance update (v4.1)** | **Candidate** |
| **System Audit Atlas** — M105C taxonomy / relationship-map / stale-index | **Structural map** of ION's 18 systems (the web diagram) — indexes systems; does not write "what is ION" prose | **Candidate witness (not applied)** |
| **Continuity ledger** — `ion_system_definition/.ion/ACTIVE_CONTEXT_PACKAGE.md` | **The single** continuity / working-memory ledger for IONOLOGIST work, across all carriers | **Canonical working memory** |
| **Folder-local capsule** — `ion_system_definition/.ion/ION_CONTEXT_CAPSULE.yaml` | Engine binding for in-folder (Cursor/Codex) sessions | **Enacted** (`resolve_context_scope`) |
| **Generated mount** — `codex_agent_mounts/role_ionologist__domain_ion_system_definition/` | **Queue-worker launch surface** — must *point to* the canonical ledger + corpus, not own a second truth | **Live mount, stale context (2026-06-04) — refresh required** |
| **Witness index** — `ionologist/M105B_M105C_READ_FIRST_WITNESS_INDEX.md` | Read-first routing to the M105 witness packages | **Candidate witness** |
| **Cursor loader** — `/.cursor/rules/ion-north-star-continuity.mdc` | Cursor sign-in → this lane | **Live** (supersedes stale `ION_Developement/.cursor/`) |
| **Portable package** — `portable_agent_domain_packages/role_ionologist__…/20260526…` | Historical offline drop-in snapshot | **Superseded archive** |

## The defect being resolved: two working capsules

- **Before:** an in-folder session binds `ion_system_definition/.ion/` (fresh,
  2026-06-16) while a queue worker binds the generated mount's `.ion/` (stale,
  2026-06-04, no North Star refs) — two ledgers, two "read-first" orders, divergent
  truth for ONE role+domain.
- **Target:** **one** continuity ledger
  (`ion_system_definition/.ion/ACTIVE_CONTEXT_PACKAGE.md`). The generated mount
  carries only a thin compiled *view* that points to it, with read-first order:
  registry identity → encyclopedia manifest → shared ledger → North Star + Derived
  Account → witness index → atlas.

## "What is ION" corpus layering (no rival narratives)

- **Canonical reader spine:** Living Encyclopedia **v4.0** (live, applied). All
  "what is ION" truth defers here.
- **Candidate operating overlay:** North Star (dashboard) — classifies itself as
  candidate; advances the encyclopedia, does not replace it.
- **Candidate maintenance input:** Derived Account → routed into a **v4.1**
  encyclopedia maintenance update (`CURRENT_STATE_OVERRIDE` / `CLAIM_LEDGER` / … +
  receipt), per the Living Encyclopedia Law (which forbids orphan, chat-only
  corpora).
- **Candidate structural map:** M105C atlas (once extracted) — taxonomy /
  relationship map, not prose canon.

## M105 applied / not-applied (per the IONOLOGIST Usage Rule)

| Package | Claim | Evidence | Class |
|---|---|---|---|
| Encyclopedia v4.0 + V100 manifest | **applied** | receipt 2026-06-04, codex_solo C-752 | active-truth (candidate maintenance) |
| M105B v4.1 pointer binding | **not applied** | `patch_applied: false`; no v4.1 file / V105 pointer on disk | historical witness |
| M105C Full System Audit Atlas | **not applied** | `settled_candidate`; no on-disk extract; zips only inside the 2026-05-26 portable embed (active-root `Needs_Routed/` absent) | historical witness |

## Consolidation status

**Enacted now (candidate space, in-authority):**
- This surface map — the single domain index.
- North Star reclassified as candidate operating overlay; encyclopedia v4.0 named
  the canonical reader spine; this map cross-linked.
- Continuity ledger affirmed as the single IONOLOGIST ledger; logged.

**Enacted — operator-authorized 2026-06-16, with receipts (candidate space):**
- **Registry amendment** ✓ — added the `ion_system_definition/` lane to
  `domain.ion_system_definition.domain.yaml` `owned_or_stewarded_surfaces` + IONOLOGIST
  route-deeper; `Needs_Routed/*.zip` relocation noted in `open_edges`. Receipt:
  `ion_system_definition_consolidation_registry_receipt_20260616.txt`.
- **Mount refresh** ✓ — generated mount re-materialized (`generated_at` 2026-06-17),
  `context_refs` 19→25, mount package now a compiled view pointing at the single
  canonical ledger (dual-working-capsule defect resolved). Receipt:
  `ion_system_definition_consolidation_mount_refresh_receipt_20260616.txt`.
- **Encyclopedia v4.1 maintenance update** ✓ —
  `ION/docs/encyclopedia/ION_Production_Encyclopedia_v4_1_LIVE_V100_CONTEXT_SYSTEMS_CONSOLIDATION_AND_CARRIER_PROOF.md`
  (8 protocol sections) + `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json` update + receipt
  `v100_living_encyclopedia_v4_1_consolidation_update_receipt_20260616.txt`.
- **M105C atlas extract** ✓ — landed candidate at `ION_SYSTEM_AUDIT_ATLAS/` (+ README +
  receipt `v105c_atlas_extract_receipt_20260616.txt`). Candidate, not applied to
  accepted state.

**Still gated/operator (not done):** first vNext domain promotion; M105B v4.1 pointer
apply; any accepted-state application of the M105C atlas.

## Cross-references
- North Star: `ION_NORTH_STAR.candidate.md` (§8.1 context systems, §9 open fronts).
- Continuity ledger: `.ion/ACTIVE_CONTEXT_PACKAGE.md`.
- Witness index: `ION/05_context/current/ionologist/M105B_M105C_READ_FIRST_WITNESS_INDEX.md`.
- Maintenance law: `ION/02_architecture/ION_LIVING_ENCYCLOPEDIA_MAINTENANCE_PROTOCOL.md`.
