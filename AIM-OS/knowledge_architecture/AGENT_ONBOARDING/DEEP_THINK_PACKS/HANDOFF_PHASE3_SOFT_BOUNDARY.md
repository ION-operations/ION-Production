# Deep Think Handoff — Pack 2: Phase 3 Soft Boundary (Inner/Outer Pools)

**Use with:** Gemini 3 Deep Think (paste this handoff + attach the files listed below).  
**Limit:** 10 files per session.

---

## Your task

We have **two MPM sims** in one app: **inner** (le, fine particles) and **outer** (leOuter, coarse particles). They run in the same frame and render into the same depth/thickness (unified rendering done). Right now they are **independent**: no coupling at the boundary. We want a **soft boundary** so that:

- Particles "prefer" to stay in their home zone (inner box vs outer ring) but are not hard-walled.
- Wave energy and momentum can **cross** the boundary (ripples can travel from inner to outer and back).
- We avoid CPU readback if possible (prefer pure GPU: g2p and/or grid coupling).

We need you to:

1. **Compare** Approach A (zone-attraction force in g2p) vs Approach B (particle handoff with overlap) from the attached plan — pros/cons, implementation cost, and which fits our codebase.
2. **Design** the preferred approach in enough detail to implement: where to add logic (which shader(s), which buffers), how to define "home zone" for inner vs outer, and how to implement an **overlap band** (2–4 cells) where both sims contribute to grid so pressure/velocity transfer happens.
3. **List** tuning parameters (stiffness, overlap width, damping) and suggest default values and bounds.

---

## Files to attach (≤10)

| # | Path | Purpose |
|---|------|--------|
| 1 | `apps/mlsmpmsplashdrafts/MULTI_POOL_SSR_ARCHITECTURE_PLAN.md` | Full plan; focus on Phase 2 (done), Phase 3 (soft boundary), Phase 5 (done), Data Flow |
| 2 | `apps/mlsmpmsplashdrafts/docs/GEMINI_TWO_TIER_CONTAINER_ANALYSIS.md` | Optional: container vs sim boundary distinction (Section 4) |
| 3 | `knowledge_architecture/AGENT_ONBOARDING/GEMINI_DEEP_THINK_CONTEXT_GUIDE.md` | Optional: 10-file and pack conventions |

If you can attach code: in `splash-mls-mpm-WaveFloor-MINIMAL.html`, the run loop `s()` calls `le.execute(...)` then `leOuter.execute(...)` in the same encoder; both use class `It` with their own buffers. g2p uses `containerBounds` and `poolMin`; `updateGrid` uses `poolMinBuffer`. Paste the relevant execute signatures and the fact that inner grid size is e.g. `ce`/`pe`, outer is `ce_outer`/`pe_outer`, so you know the spatial layout.

**Total items:** 2–4 files.

---

## What we need from you

1. **Recommendation:** Approach A, B, or a hybrid — with one paragraph justification.
2. **Design:** Step-by-step where to add code (g2p for each sim? new compute pass? overlap band in p2g?) and what data to pass (e.g. "inner box min/max in world space" to outer g2p).
3. **Parameter table:** Overlap width, restoring stiffness, damping (min, max, default).
4. **Risks:** e.g. energy gain at boundary, ordering dependence — and how to mitigate.
