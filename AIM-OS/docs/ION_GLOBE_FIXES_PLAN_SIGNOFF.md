# ION Globe: Startup Freeze, Moon, and City Glow — Plan for Sign-Off

**Part of Globe docs:** [docs/Globe/INDEX.md](Globe/INDEX.md)

**Status:** DRAFT — no code will be changed until you sign off.  
**Date:** 2026-02-23  
**Constraint:** All implementation only after this plan is approved in full or by section.  
**Decision (2026-02-24):** [ION_GLOBE_SIGNOFF_DECISION.md](ION_GLOBE_SIGNOFF_DECISION.md) — Deep Think: Approve §3 (Option A + loader fix) and §4 (moon); HOLD §5 (city glow); Section 5 to be redesigned per soft-noise alternative.

---

## 1. Scope and process

- **Startup freeze:** ~30 second browser freeze when opening the app before the scene appears.
- **Moon:** You do not see a moon or any moon setting.
- **City light pollution:** Current effect is wrong; you want a **spreading gradient glow around the city in the clouds**, not duplicated beams in a couple of directions.
- **Process:** No code changes until this plan is documented in full and you have signed off. Implementation will follow the plan (or your approved edits) only after approval.

---

## 2. Which file you use

- **IONv4c.html** — Globe only; has moon (constants, uniform, phase/eclipse, disc, **Moon Elevation** and **Moon Azimuth** on the **Sun** tab).
- **IONv4c-weather.html** — Globe + optional weather (Wx tab, toggle); **does not have the moon** (no `uMoonDirection`, no moon in `getSpace`, no Moon sliders).

If you open **IONv4c-weather.html**, that is why you see no moon and no moon setting. The plan below assumes we fix the **weather** version so it matches the non-weather version for moon and UI.

---

## 3. Startup freeze (~30 s)

### 3.1 What likely causes it

- **No weather at startup:** Weather in `IONv4c-weather.html` is lazy (FBOs/sim only after you turn “Weather-driven clouds” on). So the freeze is **not** from the weather sim.
- **Likely cause:** Work done on or before the **first frame**:
  1. **Shader compile:** One very large fragment shader (atmosphere, clouds, city, stars, etc.). WebGL compiles shaders when they are first used. The first `renderer.render()` can block the main thread for a long time on some drivers while the GPU compiles this shader.
  2. **First frame draw:** That first frame does a full-screen raymarch (atmosphere + clouds + scattering). Heavy, but usually not 30 s by itself; the main suspect is **compilation blocking the main thread**.
- **Loader:** The “Generating Universe” loader is hidden after a fixed 800 ms. So the freeze can happen **after** the loader appears or **after** it disappears; the UI does not wait for the first frame to finish.

### 3.2 What we will do (after sign-off)

1. **Measure (no behavior change):**
   - Add `performance.mark()` / `performance.measure()` around: script start, WebGL context creation, `ShaderMaterial` creation, first `renderer.render()` call, and loader hide.
   - Document where the 30 s is spent (e.g. “first render” = compile + first draw). This can be a one-time audit or a small debug build you run locally.

2. **Mitigate based on measurement:**
   - If the time is in **first shader compile:**
     - **Option A:** Keep showing the loader until the first successful frame (e.g. call `renderer.render()` once in a `requestAnimationFrame`, then hide loader after that). So the user sees “Generating Universe” for the real 30 s instead of a frozen tab.
     - **Option B:** First frame at lower cost (e.g. fewer raymarch steps or simplified shader path for frame 0), then switch to full quality on frame 1. Reduces first-frame GPU work; compile may still block.
     - **Option C:** If we ever split the shader, compile a minimal “loading” shader first, draw one frame with it, then compile the full shader on a timeout and switch. (Larger change.)
   - If the time is **not** in the first render (e.g. CDN or script parse): we will target that specifically.

3. **Deliverable:** No more “browser frozen for 30 s with no feedback.” Either the loader stays visible for the real load time, or the load time is reduced, or both, per the option you approve.

---

## 4. Moon

### 4.1 Current state

- **IONv4c.html:** Moon is implemented: `MOON_*` constants, `uMoonDirection`, `getSpace(rd, sunDir, moonDir, time)` with phase and eclipse and moon disc. **Sun** tab has a “Moon” section with **Moon Elevation** and **Moon Azimuth** sliders; default elevation 25° so the moon is above the horizon.
- **IONv4c-weather.html:** None of that. `getSpace(rd, sunDir, time)` has only two arguments; no moon uniform, no moon in sky, no sliders.

### 4.2 What we will do (after sign-off)

1. **Port the moon from IONv4c.html into IONv4c-weather.html:**
   - Add the same `MOON_*` constants and `uMoonDirection` uniform.
   - Change `getSpace` to take `moonDir` and use the same phase, eclipse, and moon disc logic as IONv4c.html.
   - Add **Moon Elevation** and **Moon Azimuth** sliders on the **Sun** tab (same as IONv4c.html), with a clear “Moon” label, and `updateMoon()` (or equivalent) so the uniform is updated from the sliders.
   - Ensure all call sites of `getSpace` in the weather file pass `moonDir` (e.g. from `uMoonDirection`).

2. **If you use IONv4c.html only:** We will only add a short note in the UI (e.g. on the Sun tab) that the moon controls are in the “Moon” section (no code change to behavior, only clarity).

3. **Deliverable:** In the file you use, you see the moon in the sky and a clear Moon section with Elevation and Azimuth controls on the Sun tab.

---

## 5. City light pollution (spreading gradient glow)

### 5.1 What you want

- **Spreading gradient glow around the city in the clouds:** The glow should look like light **spreading out in all directions** from the city and fading smoothly with distance — a single, soft gradient centered on the city, not discrete beams or “duplicated lighting in 2 directions.”

### 5.2 What the code does today (and why it’s wrong)

- **IONv4c.html:** `getCityGlow` samples **5 ground points**: nadir under `p` plus 4 points offset along T and B (tangent directions). It blends their emission with weights. That produces a **cross/plus** pattern (bright at nadir, then along two perpendicular directions). So the glow is not a radial spread; it’s “duplicated and moved in 2 directions” (really four, but same idea).
- **IONv4c-weather.html:** Same idea with **3 samples**: nadir + one T offset + one B offset. Again discrete directions, not a smooth radial gradient.

So in both files the implementation is **directional sampling**, not **distance-based gradient**. That’s why you get “total garbage” and not the spreading glow you asked for.

### 5.3 Intended behavior (for sign-off)

- **Visual:** One soft glow centered on the city, fading smoothly in **all directions** (in the clouds and in the atmosphere). No extra beams, no obvious “second light” in another direction. Like a single dome of light above the city that softens with distance.
- **Model:** For each sample point `p` in the atmosphere/clouds:
  - Define the “city center” as the ground nadir of the main city (e.g. one fixed direction or the current nadir used for the single-city case).
  - Compute how far `p` is from that city center **in angle** (e.g. angle between `normalize(p)` and the city nadir direction) or in a way that is consistent along the sphere.
  - Apply a **smooth falloff** (e.g. Gaussian or `smoothstep`) so that:
    - Directly above the city: full glow.
    - Farther away in any direction: gradual fade.
  - Multiply the city’s emission (computed once at the city center) by this falloff. So the glow is **one emission value × one gradient** — no multiple directional samples that create separate beams.

### 5.4 Technical approach (high level)

1. **Single city emission:** Compute emission (and optionally transmittance) **once** at the city nadir point (one `getSurface` + one `getAtmoTransmittance` from that point toward `p`, or a simplified transmittance).
2. **Gradient from city:** For the current raymarch point `p`:
   - `cityNadir` = unit vector from planet center through the city (fixed or from uniform).
   - `angleFromCity` = angle between `normalize(p)` and `cityNadir` (e.g. `acos(dot(...))`).
   - `falloff` = e.g. `exp(-(angleFromCity/radius)^2)` or `1.0 - smoothstep(0.0, radius, angleFromCity)` with a configurable radius (e.g. 0.05–0.15 radians or a uniform).
3. **Result:** `cityGlow = cityEmission * transmittance * falloff * uCityGlowStrength * ...` (same altitude/night checks as now). So the glow **spreads in all directions** and fades with angle; no extra directional samples, no duplicated beams.

4. **Performance:** One city sample per call to `getCityGlow` instead of 3 or 5; we only add one angle and one falloff calculation per sample. So we **reduce** cost and fix the visual.

5. **Tunables:** Falloff radius (angle or distance) and curve (Gaussian vs linear smoothstep) as uniforms or constants so you can adjust “how wide” the glow spreads without code churn.

### 5.5 What we will not do

- We will **not** add more directional samples (e.g. more tangent directions) to “smooth” the current approach. That has already produced the wrong effect (duplicated directions). The fix is **radial falloff from one city center**, not more directions.

### 5.6 Deliverable

- City glow in the clouds and atmosphere is a **single, spreading gradient** centered on the city, with no discrete beams or duplicated lighting in 2 (or 4) directions. Implementation will follow the approach above unless you change it in sign-off.

---

## 6. Sign-off

Please review and respond with one of:

- **Approve full plan** — I will implement all three sections (startup, moon, city glow) according to this document.
- **Approve by section** — e.g. “Approve 3 and 4, hold 5” or “Approve 4 and 5 only.”
- **Request changes** — Specify what to add, remove, or change (e.g. different falloff shape, different loader behavior, or which file is primary). I will update the plan and resubmit; no code until you approve.

No code will be touched until you have signed off.

---

*End of plan.*
