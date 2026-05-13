# Deep Think Handoff — Pack 4: MLS-MPM Full Roadmap (Container + Phase 3 + Phase 4)

**Use with:** Gemini 3 Deep Think (paste this handoff + attach the files listed below).  
**Limit:** 10 files per session.

---

## Your task

We have one **MLS-MPM splash** app with:

- **Done:** SSR (Phase 1), second sim for outer pool (Phase 2), unified rendering of both particle sets (Phase 5).
- **Not done:** (1) **Two-tier container** — physics currently gets only inner pool AABB; particles on deck fall through. (2) **Phase 3** — soft boundary between inner (le) and outer (leOuter) sims. (3) **Phase 4** — bidirectional heightfield–particle coupling beyond the current wave floor.

We want you to:

1. **Dependency graph:** In what order should we implement the container fix, Phase 3, and Phase 4? (e.g. container first so deck is correct before we tune boundary; or Phase 3 first so both pools are coupled before we add heightfield.) Justify in 2–3 sentences per dependency.
2. **Conflict check:** Could the two-tier container (deck + pool bounds) and Phase 3 (inner vs outer *sim* zones) interact badly? Same g2p, different bounds for inner vs outer sim — do we need two container buffer layouts or one shared?
3. **Simplification:** Is there any way to reduce scope (e.g. defer heightfield-to-particle, or do a minimal overlap band first) and still get a "good enough" concentric pool with waves crossing the boundary?
4. **Risks:** Top 3 implementation or stability risks across these three pieces and how to mitigate.

---

## Files to attach (≤10)

| # | Path | Purpose |
|---|------|--------|
| 1 | `apps/mlsmpmsplashdrafts/MULTI_POOL_SSR_ARCHITECTURE_PLAN.md` | Full architecture: Phases 1–5, Data Flow, Related container section |
| 2 | `apps/mlsmpmsplashdrafts/docs/GEMINI_TWO_TIER_CONTAINER_ANALYSIS.md` | Two-tier container analysis and recommendation |
| 3 | `knowledge_architecture/AGENT_ONBOARDING/DEEP_THINK_PACKS/INDEX.md` | List of all packs (this roadmap is Pack 4) |

**Total items:** 3 files. Stay under 10 if you add code excerpts (e.g. g2p/execute container usage).

---

## What we need from you

1. **Recommended order:** Container → Phase 3 → Phase 4, or another order, with brief justification.
2. **Dependency diagram:** Text or bullet list (e.g. "Container fix blocks: correct deck behavior. Phase 3 blocks: soft boundary design. Phase 4 depends on: Phase 3 and wave solver extension.").
3. **Container vs Phase 3:** One paragraph on whether inner and outer sim share one container bounds buffer or need different bounds; and any g2p changes to support both.
4. **Scope reduction:** One or two concrete "minimal first steps" (e.g. "Container + zone-attraction only, no overlap band in v1").
5. **Top 3 risks** and mitigations.
