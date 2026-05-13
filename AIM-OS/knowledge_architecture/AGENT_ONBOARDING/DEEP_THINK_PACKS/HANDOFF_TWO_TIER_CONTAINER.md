# Deep Think Handoff — Pack 1: Two-Tier Container Physics

**Use with:** Gemini 3 Deep Think (paste this handoff + attach the files listed below).  
**Limit:** 10 files per session.

---

## Your task

We have a **WebGPU MLS-MPM fluid simulator** in a single HTML file. The **renderer** draws a **pool-with-deck** (two-tier geometry: inner pool hole + surrounding deck). The **physics** (g2p compute shader) currently receives only a **single AABB** — when the UI shape is "pool", we send only the **inner pool** bounds. Particles that splash onto the deck are then outside the physics world and glitch or fall through.

We want you to:

1. **Validate** the proposed two-tier fix (deck bounds + pool bounds, 64-byte buffer, shapeType) in the attached analysis.
2. **Confirm or correct** the WGSL logic for: (a) position clamp (deck XZ, pool vs deck floor in Y), (b) soft walls at deck and at pool edges when on deck, (c) wave floor and reset-sheet using deck bounds.
3. **Flag** any edge cases (e.g. particle exactly on pool rim, deckMin.y convention for pool shape), and suggest a minimal test checklist before we implement.

---

## Files to attach (paste or upload these; ≤10 total)

Attach the following files from the repo. Paths are relative to repo root.

| # | Path | Purpose |
|---|------|--------|
| 1 | `apps/mlsmpmsplashdrafts/docs/GEMINI_TWO_TIER_CONTAINER_ANALYSIS.md` | Full analysis (root cause, proposed WGSL/CPU, risks) |
| 2 | `apps/mlsmpmsplashdrafts/MULTI_POOL_SSR_ARCHITECTURE_PLAN.md` | Architecture plan; read "Related: Container Two-Tier Physics" and Phase 3 intro |
| 3 | `apps/mlsmpmsplashdrafts/splash-mls-mpm-WaveFloor-MINIMAL.html` | Main app (large). If over upload limit, attach only: search for `struct ContainerBounds` and `containerBoundsBuffer` and paste the g2p shader block (variable Tt) and the It constructor line with containerBoundsBuffer, and the It.execute() block that builds `cb` and writes containerBoundsBuffer. |

If you cannot attach the full HTML (size limit), use these **excerpts** as separate paste-ins (count as 1–2 "files" in the 10):

- **Excerpt A — g2p ContainerBounds and wall logic:** In `splash-mls-mpm-WaveFloor-MINIMAL.html`, find `struct ContainerBounds { wallMin` and the following ~80 lines (position clamp, wallMinY/wallMaxY, soft walls, reset sheet). Paste that block with a one-line note: "From splash-mls-mpm-WaveFloor-MINIMAL.html, g2p shader (Tt)."
- **Excerpt B — CPU container write:** Find `const cp=typeof window` and the block that sets `pMinX,pMinY,...` and `cb.set([pMinX,...])` and `writeBuffer(this.containerBoundsBuffer`. Paste with note: "From splash-mls-mpm-WaveFloor-MINIMAL.html, It.execute()."

**Total items:** 2–3 (analysis + plan + full HTML or 2 excerpts).

---

## What we need from you

1. **Go/No-go** on the two-tier design (64-byte buffer, 4×vec4, shapeType in deckMin.w).
2. **Corrected or confirmed** WGSL logic (bullet list or short code snippets) for position clamp and soft walls.
3. **Edge cases** and a **short test checklist** (5–10 items) we can run after implementation.

---

## Constraints (for context)

- Single HTML file, WebGPU, WGSL. No build step.
- Same `It` class and g2p are used for both "inner" and "outer" sims; they share the same container bounds for now.
- We must preserve existing wave floor and reset-sheet behavior; only container bounds and related clamp/wall logic change.
