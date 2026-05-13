# Deep Think Handoff — Pack 3: Phase 4 Heightfield–Particle Bidirectional Coupling

**Use with:** Gemini 3 Deep Think (paste this handoff + attach the files listed below).  
**Limit:** 10 files per session.

---

## Your task

Beyond the **coarse outer particle pool** we have an existing **heightfield wave solver** (256×256, wave equation) used today as a "wave floor" under the inner pool. We want to extend so that:

- **Outer particles** near the boundary **displace** the heightfield (particles → waves), and
- **Heightfield** slope **pushes** outer particles (waves → particles) so incoming waves affect the fluid.

The plan references **ProPool.html** for one-way particle displacement (volume-based). We need **bidirectional** coupling and a clear way to integrate with the current wave floor (same solver? extended domain? mask for inner region?).

We need you to:

1. **Summarize** the particle-to-heightfield coupling method (volume displacement, grid sampling) and the heightfield-to-particle coupling (gradient sampling, force application) in a form we can implement in WGSL/JS.
2. **Propose** how the current 256×256 wave floor relates to the "outer" heightfield: same texture extended in domain, or separate layer, and how the inner (particle) region is masked so the solver doesn’t double-count.
3. **List** the exact shader/CPU changes: which pass(es) read/write the heightfield, where gradient is sampled (e.g. outer sim g2p), and any new buffers or uniforms.
4. **Flag** stability risks (e.g. feedback gain, CFL) and suggest safeguards.

---

## Files to attach (≤10)

| # | Path | Purpose |
|---|------|--------|
| 1 | `apps/mlsmpmsplashdrafts/MULTI_POOL_SSR_ARCHITECTURE_PLAN.md` | Full plan; focus on Phase 4 (heightfield layer), Phase 5 (rendering), Data Flow |
| 2 | `docs/ION_WEATHER_GCM_IMPLEMENTATION_PLAN.md` | Optional: reference for GPU sim + sampling patterns (different domain but same idea of sim texture + main shader sampling) |
| 3 | Code context: in `splash-mls-mpm-WaveFloor-MINIMAL.html` we have `waveTexA`/`waveTexB`, `waveSolverPipe`, `heightfieldView` passed to `It` (g2p binding 6). Wave floor params in `waveFloorBuf`. Paste or describe where the wave solver runs and where g2p samples the heightfield. |

**Total items:** 2–3 files (+ optional code excerpt).

---

## What we need from you

1. **Bidirectional coupling spec:** (a) Particles → heightfield: formula or pseudocode for displacement per cell; (b) Heightfield → particles: gradient computation and force in g2p.
2. **Integration with current wave floor:** One paragraph + diagram or bullet list: same solver vs extended, mask strategy, and where outer particles write displacement.
3. **Implementation checklist:** Numbered list of code changes (file, pass, new buffer/uniform if any).
4. **Stability and CFL:** Short note on time step or damping to avoid blow-up.
