# R/U Wiring Sprint — Final Consensus (GPT-5.2 & Gemini Deep Think)

**Status:** Locked consensus, ready for Antigravity IDE implementation  
**Date:** 2025-02-27  
**Source:** Independent dual-audit by GPT-5.2 and Gemini Deep Think; physics debate resolved; final builder brief agreed.  
**App:** ProFlow HyperH2O_v2 — `C:\Users\bombe\Documents\Application_Dev\ProFlow\builds\HyperH2O_v2\src`

---

## 1. Executive summary

Two independent AI audits of the HyperH2O_v2 WebGPU codebase identified the **same five structural bugs**. After one critical physics correction (frame-rate–safe velocity injection), both models endorsed the same patch set. This document is the single source of truth for the **R/U Wiring Sprint** (Milestones 0 & 1): fix causality, fix intent-field math, and wire the rupture field **R** and momentum field **U** into MLS-MPM breakout so that escaping particles move **directionally forward** (slash/crest peel) instead of spraying straight up.

---

## 2. Independent audit consensus — the five bugs

When two independent systems audit thousands of lines of WebGPU code and point to the **exact same issues**, the result is treated as validated. The following were agreed by both GPT-5.2 and Gemini.

| # | Name | Location | What’s wrong |
|---|------|----------|--------------|
| 1 | **Causality inversion** | `src/splash/V2Engine.tsx` | Physics (`simulator.execute()`) runs **before** wave impulses and intent-field dispatch. The “brain” (R, C, M, U) runs after the “body,” so breakout always reads **yesterday’s** intent. |
| 2 | **Reservoir drain trap** | `src/splash/multiregime/intentFields.wgsl` | Drain (mass subtraction from reservoir M) is multiplied by `dt`. So M never properly empties — it becomes a “haunted sponge” that never really drains. |
| 3 | **NMS overlap bug** | `src/splash/hierarchy/patchExtraction.wgsl` | Only **4 neighbors** (L, R, D, U) are checked for local maximum. Diagonal crests double-extract; plateaus spam. |
| 4 | **Missing intent plumbing** | `src/splash/v2-mls-mpm/mls-mpm.ts` | Simulator has no bindings for intent textures. `intentRCView` and `intentUView` are never passed; bind group doesn’t include R/U. |
| 5 | **Wave-floor blind to R/U** | `src/splash/v2-mls-mpm/waveFloorCoupling.wgsl` | Shader reads only heightfield. No bindings for R or U; breakout uses only legacy scalar crestness, so no directional throw. |

**Doctrine alignment:** The intent-field writeup states that the fields exist to **steer what the surface wants to become next**. Upward particle hoses from scalar hotspots, infinite emission without memory, and broken causality between surface forcing and detached response are called out as main water sins. These five bugs directly violate that.

---

## 3. Physics debate and resolution

### 3.1 The “railgun confetti” trap (Gemini’s correction)

**Issue:** In Patch 4 (waveFloorCoupling breakout), injecting horizontal throw with:

```wgsl
particles[id.x].v.x += throwDir.x * throwMag;  // throwMag = effectiveCrestness * boost * 0.6
```

is **frame-rate dependent** if `throwMag` is constant per frame. A particle can stay in the breakout band for **several frames**; this block runs **every frame**. So:

- `v += constant` every frame = **acceleration**
- Acceleration must be scaled by **dt** when integrated into velocity
- Without `dt`, at 144 Hz particles get ~2.4× more momentum than at 60 Hz → “railgun confetti”

**Conclusion:** The horizontal throw term **must** be scaled by `dt`. Gemini’s version is correct; GPT-5.2 agreed and withdrew the earlier raw-impulse sketch.

### 3.2 U: direction vs magnitude (GPT’s hybrid, then consensus)

- **U** is a **magnitude-bearing vector field** (direction and strength), not just an azimuth.
- **Raw U:** preserves magnitude but can overreact to local spikes.
- **Fully normalized U:** preserves direction only, loses “how strong is this crest transport?”
- **Hybrid (agreed):** Use **direction** from normalized U, scale by a **capped magnitude** term (e.g. `min(length(U), 1.5)` or `min(uLen, 2.0)`), and integrate with **dt** so repeated in-band application is frame-rate safe.

### 3.3 Clean semantics (GPT’s micro-refinement)

Gemini’s line:

```wgsl
let throwMag = effectiveCrestness * waveFloor.crestBreakoutBoost * uMag * 60.0 * dt * 0.4;
```

is correct but “tuned by folk ritual.” The `60.0 * dt * 0.4` is a 60 Hz–normalized fudge. GPT suggested:

- Name an explicit **acceleration** constant (e.g. `THROW_ACCEL_SCALE`).
- Compute `throwAccel = ... * THROW_ACCEL_SCALE`, then `throwDeltaV = throwAccel * dt`.

**Final consensus:** Use the **dt-scaled, capped-magnitude** formulation with **named constants** (`THROW_ACCEL_SCALE`, `LIFT_ACCEL_SCALE`) for tunable, self-documenting shader code. Same behavior, clearer meaning.

### 3.4 One-frame-latent coupling (clarification)

Moving `injectImpulses()` **before** `simulator.execute()` means the physics step reads **previous-frame** particle positions for wave injection. That is **intentional and stable** for two-way coupling — not a bug. The bug was the **opposite**: physics first, then fresh intent, so breakout was reading yesterday’s brain.

---

## 4. Recommended patch order (pain-to-value)

For sequencing by impact:

1. **Patch 1 — Causality reorder (V2Engine.tsx)** — Restore “brain before body”; immediate visible win (no scalar hose, stable R overlay).
2. **Patch 2 — Intent plumbing (mls-mpm.ts)** — Pass R/U texture views into the simulator.
3. **Patch 3 — Directional breakout (waveFloorCoupling.wgsl)** — Wire R/U into breakout with dt-scaled throw and named constants.
4. **Patch 4 — Reservoir drain (intentFields.wgsl)** — M drains properly per frame.
5. **Patch 5 — 8-way NMS (patchExtraction.wgsl)** — Structural fix for hierarchy path; reduces diagonal double-seeding and plateau spam.

Patch 5 is correct but not the first visual jackpot; 1–3 give the main behavioral fix.

---

## 5. Final builder brief — exact patches

All paths relative to HyperH2O_v2 **src** (e.g. `src/splash/...` means `splash/...` under the app’s `src` folder).

---

### Patch 1: V2Engine causality reorder

**File:** `src/splash/V2Engine.tsx`

**Action:** In the `if (solverMode === 'mlsmpm')` block inside `frame()`, reorder so that:

1. Wave impulses (`injectImpulses`) run first.
2. Intent field dispatch runs second (`intentFieldManager.updateFieldParams`, `updateMomentumParams`, `dispatch`, optional `dispatchDebug`; then `getRCView()` / `getUView()`).
3. Bind views: `simulator.setIntentFieldsViews(intentRCView, intentUView)` (and same for `outerSimulator`, `outerSimulator2` if present).
4. Then `simulator.execute(...)`.
5. Then secondary systems (spray, outer sims, aeration, etc.).

**Do not** move `wavePool.step()` — it is already earlier. The minimal repair is: **impulses + intent before MLS execute**.

**Snippet (structure only; keep existing variable names and logic):**

```ts
// ── 1. WAVE IMPULSES ──
if (wavePool && waveActive && ...) {
  // [existing wavePool.injectImpulses(...) block]
}

// ── 2. INTENT FIELDS ──
let intentRCView: GPUTextureView | null = null;
let intentUView: GPUTextureView | null = null;
if (intentFieldManager && currentSettings.intentFieldsEnabled && currentSettings.running) {
  const dtSeconds = maxDt * currentSettings.speed;
  intentFieldManager.updateFieldParams({ ... });
  intentFieldManager.updateMomentumParams({ ... });
  intentFieldManager.dispatch(commandEncoder, dtSeconds);
  // optional dispatchDebug(...)
  intentRCView = intentFieldManager.getRCView();
  intentUView = intentFieldManager.getUView();
}

// ── 3. BIND VIEWS ──
simulator.setIntentFieldsViews(intentRCView, intentUView);
if (outerSimulator) outerSimulator.setIntentFieldsViews(intentRCView, intentUView);
if (outerSimulator2) outerSimulator2.setIntentFieldsViews(intentRCView, intentUView);

// ── 4. PARTICLE EXECUTE ──
simulator.execute(commandEncoder, ...);

// ── 5. SECONDARY SYSTEMS ──
// spraySystem.dispatch, outerSimulator.execute, aerationVolume.step, etc.
```

---

### Patch 2: Intent texture plumbing (mls-mpm.ts)

**File:** `src/splash/v2-mls-mpm/mls-mpm.ts`

**Actions:**

1. **Add class members** (near other view/buffer members, ~line 70):
   - `intentRCView: GPUTextureView | null = null;`
   - `intentUView: GPUTextureView | null = null;`
   - `dummyIntentTex!: GPUTexture;`
   - `dummyIntentView!: GPUTextureView;`

2. **At bottom of constructor**, before `setHeightfieldView`:
   - Create dummy 1×1 texture: `rg32float`, `TEXTURE_BINDING`.
   - `this.dummyIntentView = this.dummyIntentTex.createView();`
   - Call `this.setHeightfieldView(heightfieldTextureView);` (end constructor).

3. **Replace `setHeightfieldView`** so it only updates `heightfieldView` and calls `rebuildWaveFloorCouplingBindGroup()`.

4. **Add `setIntentFieldsViews(rcView, uView)`** that updates `intentRCView` / `intentUView` and calls `rebuildWaveFloorCouplingBindGroup()` (with early exit if views unchanged).

5. **Add `private rebuildWaveFloorCouplingBindGroup()`** that:
   - If no `heightfieldView`, set `waveFloorCouplingBindGroup = null` and return.
   - Otherwise use `safeRcTex = intentRCView ?? dummyIntentView`, `safeUTex = intentUView ?? dummyIntentView`.
   - Create bind group with existing buffers (0–9) and **binding 10 = safeRcTex**, **binding 11 = safeUTex**.

Exact bind group layout must match the WGSL (bindings 0–11). See Patch 3 for shader bindings.

---

### Patch 3: Directional breakout (waveFloorCoupling.wgsl)

**File:** `src/splash/v2-mls-mpm/waveFloorCoupling.wgsl`

**Actions:**

1. **Add bindings** at top (after existing @group(0) bindings):
   - `@group(0) @binding(10) var intentRC: texture_2d<f32>;`
   - `@group(0) @binding(11) var intentU: texture_2d<f32>;`

2. **From `let dim = textureDimensions(heightfield);`** through the rest of the main logic, **replace** with logic that:
   - Samples heightfield and computes `px, py`, `eta`.
   - **Reads intent fields:** if `textureDimensions(intentRC).x > 1`, sample R and U at same uv, set `hasIntent = true`; else R=0, U=vec2(0), `hasIntent = false`.
   - **Fallback crestness:** compute legacy slope/crest/curvature metric and `legacyCrestness` as today.
   - **Effective crest:** if `hasIntent`, `effectiveCrestness = clamp(R,0,1)`, `effectiveCrestMetric = R*4.0`; else use legacy.
   - **Band and breakout:** same bandMinY/bandMaxY, x_n, wall responses, breakout velocity/band logic.
   - **In the “breakout allowed” branch**, add the **R/U horizontal throw**:
     - Only if `hasIntent && crestBreakoutEnabled && effectiveCrestness > 0.05`.
     - `uLen = length(U)`; if `uLen > 1e-5` (or 1e-6): `throwDir = U/uLen`, `uMag = min(uLen, 1.5)` (or 2.0).
     - **Named constants:** `THROW_ACCEL_SCALE = 24.0` (tunable), `LIFT_ACCEL_SCALE = 5.0`.
     - `throwAccel = waveFloor.crestBreakoutBoost * uMag * effectiveCrestness * THROW_ACCEL_SCALE`.
     - `throwDeltaV = throwAccel * dt`.
     - `particles[id.x].v.x += throwDir.x * throwDeltaV`, `particles[id.x].v.z += throwDir.y * throwDeltaV`.
     - `particles[id.x].v.y += effectiveCrestness * LIFT_ACCEL_SCALE * dt`.

**Important:** Throw and lift must both be **dt-scaled** so that repeated application in the band is frame-rate independent.

---

### Patch 4: Reservoir drain fix (intentFields.wgsl)

**File:** `src/splash/multiregime/intentFields.wgsl`

**Target:** Section “Compute M (Reservoir Mass)” (~line 140).

**Change:** Drain is an **absolute subtraction per frame**; it must **not** be multiplied by `dt`. Refill and other additive terms remain inside `dt * (...)`.

**Replace the M update with:**

```wgsl
  let refill = params.mRefillRate * (params.mBaseline - prevM);
  let recaptureInput: f32 = 0.0;

  // FIX: Drain bypasses dt — absolute subtraction per frame
  let newM = saturateF(
    (prevM - drain) + dt * (
      refill
      + params.mConvGain * compression
      + params.mRecaptureScale * recaptureInput
    )
  );
```

---

### Patch 5: 8-way NMS (patchExtraction.wgsl)

**File:** `src/splash/hierarchy/patchExtraction.wgsl`

**Target:** The 4-way “Sparse Local Maximum Extraction” block (~line 40).

**Change:** Replace with **8-way** neighborhood (L, R, D, U, DL, DR, UL, UR). Use deterministic tie-breaking (e.g. strict `>` on one set, `>=` on the other) so a single local max wins. Keep existing patch-saving logic (`atomicAdd(&patchOutput.count, 1u)`, etc.) unchanged.

**Snippet (neighborhood and condition only):**

```wgsl
    let R_L  = textureLoad(rcTex, clamp(coord + vec2i(-1,  0), vec2i(0), vec2i(res - 1))).r;
    let R_R  = textureLoad(rcTex, clamp(coord + vec2i( 1,  0), vec2i(0), vec2i(res - 1))).r;
    let R_D  = textureLoad(rcTex, clamp(coord + vec2i( 0, -1), vec2i(0), vec2i(res - 1))).r;
    let R_U  = textureLoad(rcTex, clamp(coord + vec2i( 0,  1), vec2i(0), vec2i(res - 1))).r;
    let R_DL = textureLoad(rcTex, clamp(coord + vec2i(-1, -1), vec2i(0), vec2i(res - 1))).r;
    let R_DR = textureLoad(rcTex, clamp(coord + vec2i( 1, -1), vec2i(0), vec2i(res - 1))).r;
    let R_UL = textureLoad(rcTex, clamp(coord + vec2i(-1,  1), vec2i(0), vec2i(res - 1))).r;
    let R_UR = textureLoad(rcTex, clamp(coord + vec2i( 1,  1), vec2i(0), vec2i(res - 1))).r;

    if (R > R_L && R >= R_R && R > R_D && R >= R_U &&
        R > R_DL && R >= R_DR && R > R_UL && R >= R_UR) {
      let idx = atomicAdd(&patchOutput.count, 1u);
      // ... [keep existing patch saving logic]
    }
```

---

## 6. Verification and sign-off

After applying all five patches and compiling:

| Test | Pass criteria |
|------|----------------|
| **Slash test** | Drag mouse forcefully across surface. Escaping particles **peel horizontally in the direction of the drag**, not straight up. |
| **Crest peel** | Fast-moving waves spawn particles that lean **forward** over the trough. |
| **R overlay (Mode 1)** | Red rupture zones track crests **smoothly**, no 1-frame jitter/static (validates causality). |
| **M drain (Mode 3)** | With patch extraction, **sharp black drain holes** that slowly refill to cyan; no endless flashing. |
| **No confetti** | No railgun/explosion. Coherent water breakout. If too strong, reduce `THROW_ACCEL_SCALE` in `waveFloorCoupling.wgsl`. |

**Regression traps to watch:**

- Reverting causality order → hose behavior and jittery R.
- Removing dt from throw/lift → frame-rate–dependent confetti at high FPS.
- Using only 4-way NMS → diagonal double-seeding and plateau spam in hierarchy path.

---

## 7. References and history

- **Dual-audit:** GPT-5.2 and Gemini Deep Think each audited the same codebase independently; both listed the same five structural bugs.
- **Physics agreement:** Gemini proposed dt-scaled throw; GPT-5.2 initially suggested a non–dt-scaled hybrid, then **endorsed Gemini’s dt-scaled version** as the correct final consensus and noted the railgun-confetti risk.
- **Semantics:** GPT-5.2 suggested named constants (`THROW_ACCEL_SCALE`, `LIFT_ACCEL_SCALE`) for clarity and tuning; both agreed on the final formulation.
- **V2Engine nuance:** `wavePool.step()` stays where it is; only **impulses + intent dispatch** move above `simulator.execute()`.

This document is the **final council verdict** and the single reference for implementing the R/U Wiring Sprint in the Antigravity IDE.

---

## Appendix A: Chat narrative (verbatim summary)

- **Gemini:** Identified same five bugs; proposed full patch set; corrected physics: “particle stays in breakout band for several frames” → throw must be dt-scaled or you get frame-rate–dependent “railgun confetti”; also normalize(U) alone discards wave momentum, so use capped U magnitude + direction.
- **GPT-5.2 (first pass):** Agreed on Patches 1, 2, 3, 5; for Patch 4 suggested a **more conservative** hybrid throw (capped uMag, no dt in first sketch) to avoid “sideways confetti cannon.”
- **GPT-5.2 (after Gemini’s dt correction):** “Gemini is right on the dt point. … My earlier breakout throw sketch treated the U injection too much like a one-shot impulse. … v += constant every frame = frame-rate dependent acceleration. … So yes: the horizontal throw term should be scaled by dt.” Endorsed Gemini’s latest as the **final consensus patch**; suggested THROW_ACCEL_SCALE / LIFT_ACCEL_SCALE for cleaner semantics.
- **V2Engine:** GPT clarified that `wavePool.step()` is already earlier; only **injectImpulses + intent dispatch** need to move above `simulator.execute()`.
- **Patch order (value):** Causality → Plumbing → Breakout → Drain → NMS (so immediate win is killing the hose and restoring causality; NMS is right but not the first visual jackpot).

---

## Appendix B: Exact code blocks (copy-paste reference)

The following are the **exact** snippets from the final builder brief for use in the IDE. Variable names (e.g. `sphereRenderFl` vs `densityGridFlag`) must match the existing file.

### B.1 waveFloorCoupling.wgsl — breakout section (dt-scaled, named constants)

From `let dim = textureDimensions(heightfield);` through end of breakout logic, use this pattern (ensure bindings 10 and 11 are intentRC and intentU):

```wgsl
  let dim = textureDimensions(heightfield);
  let px = clamp(i32(u * f32(dim.x)), 0, i32(dim.x) - 1);
  let py = clamp(i32(v * f32(dim.y)), 0, i32(dim.y) - 1);
  let eta = textureLoad(heightfield, vec2i(px, py), 0).r;

  // ── READ INTENT FIELDS ──
  var R = 0.0;
  var U = vec2f(0.0);
  var hasIntent = false;
  let rcDim = textureDimensions(intentRC);
  if (rcDim.x > 1u) {
    hasIntent = true;
    let px_rc = clamp(i32(u * f32(rcDim.x)), 0, i32(rcDim.x) - 1);
    let py_rc = clamp(i32(v * f32(rcDim.y)), 0, i32(rcDim.y) - 1);
    R = textureLoad(intentRC, vec2i(px_rc, py_rc), 0).r;
    U = textureLoad(intentU, vec2i(px_rc, py_rc), 0).rg;
  }

  // ── FALLBACK CRESTNESS ──
  let etaL = textureLoad(heightfield, vec2i(max(px - 1, 0), py), 0).r;
  let etaR = textureLoad(heightfield, vec2i(min(px + 1, i32(dim.x) - 1), py), 0).r;
  let etaD = textureLoad(heightfield, vec2i(px, max(py - 1, 0)), 0).r;
  let etaU = textureLoad(heightfield, vec2i(px, min(py + 1, i32(dim.y) - 1)), 0).r;
  let slope = 0.5 * length(vec2f(etaR - etaL, etaU - etaD));
  let crest = max(0.0, 4.0 * eta - etaL - etaR - etaD - etaU);
  let curvatureBias = clamp(waveFloor.crestCurvatureBias, 0.0, 1.0);
  let legacyMetric = mix(slope, crest, curvatureBias);
  let legacyMetricThresholded = max(0.0, legacyMetric - max(0.0, waveFloor.crestThreshold));
  let legacyCrestness = clamp(legacyMetricThresholded * max(0.0, waveFloor.crestSensitivity), 0.0, 1.0);

  var effectiveCrestMetric = legacyMetric;
  var effectiveCrestness = legacyCrestness;
  if (hasIntent) {
    effectiveCrestness = clamp(R, 0.0, 1.0);
    effectiveCrestMetric = R * 4.0;
  }

  let crestMetricQ = u32(round(clamp(effectiveCrestMetric, 0.0, 8.0) * CREST_STATS_FP_SCALE));
  let crestnessQ = u32(round(effectiveCrestness * CREST_STATS_FP_SCALE));

  let surfaceY = waveFloor.yOffset + eta * waveFloor.amplitude;
  let bandMinY = surfaceY - waveFloor.sheetThickness;
  let bandMaxY = surfaceY;
  let k = 2.0;
  let x_n = pos + particles[id.x].v * dt * k;

  atomicAdd(&waveFloorStats[0], 1u);
  atomicAdd(&waveFloorStats[4], crestMetricQ);
  atomicAdd(&waveFloorStats[5], crestnessQ);
  atomicMax(&waveFloorStats[6], crestnessQ);
  if (crestnessQ > 0u) { atomicAdd(&waveFloorStats[7], 1u); }

  if (x_n.y < bandMinY) {
    particles[id.x].v.y += waveFloor.wallStiffness * (bandMinY - x_n.y);
  }

  if (x_n.y > bandMaxY) {
    let above = x_n.y - bandMaxY;
    var band = max(1e-4, waveFloor.sheetThickness * 2.5);
    var breakoutV = waveFloor.vBreakout;
    if (waveFloor.crestBreakoutEnabled != 0u) {
      breakoutV = max(0.0, breakoutV - effectiveCrestness * waveFloor.crestBreakoutBoost);
      band *= 1.0 + 0.75 * effectiveCrestness;
    }
    if (above <= band) { atomicAdd(&waveFloorStats[1], 1u); }

    if (particles[id.x].v.y <= breakoutV && above <= band) {
      particles[id.x].v.y += waveFloor.wallStiffness * (bandMaxY - x_n.y);
      atomicAdd(&waveFloorStats[3], 1u);
    } else if (above <= band) {
      atomicAdd(&waveFloorStats[2], 1u);

      if (hasIntent && waveFloor.crestBreakoutEnabled != 0u && effectiveCrestness > 0.05) {
        let uLen = length(U);
        if (uLen > 1e-5) {
          let throwDir = U / uLen;
          let uMag = min(uLen, 1.5);
          let THROW_ACCEL_SCALE = 24.0;
          let throwAccel = waveFloor.crestBreakoutBoost * uMag * effectiveCrestness * THROW_ACCEL_SCALE;
          let throwDeltaV = throwAccel * dt;
          particles[id.x].v.x += throwDir.x * throwDeltaV;
          particles[id.x].v.z += throwDir.y * throwDeltaV;
        }
        let LIFT_ACCEL_SCALE = 5.0;
        particles[id.x].v.y += effectiveCrestness * LIFT_ACCEL_SCALE * dt;
      }
    }
  }
```

### B.2 intentFields.wgsl — Compute M section

```wgsl
  // ────────────────────────────────────────────────────
  //  6. Compute M (Reservoir Mass)  —  §120.4
  // ────────────────────────────────────────────────────

  let refill = params.mRefillRate * (params.mBaseline - prevM);
  let recaptureInput: f32 = 0.0;

  // FIX: Drain is an absolute subtraction per frame, bypass dt multiplier
  let newM = saturateF(
    (prevM - drain) + dt * (
      refill
      + params.mConvGain * compression
      + params.mRecaptureScale * recaptureInput
    )
  );
```

### B.3 patchExtraction.wgsl — 8-way NMS condition

Keep existing `R = textureLoad(...).r` and patch-saving logic; replace only the neighbor loads and the `if` condition with the 8-way version in §5 Patch 5 above.
