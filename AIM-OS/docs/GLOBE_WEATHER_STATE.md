# Globe / Weather — Current State

**Part of Globe docs:** [docs/Globe/INDEX.md](Globe/INDEX.md)

**Purpose:** Single place for "what is true right now" and "what done means" for the Globe weather app. Update this when something major is fixed or broken. Agents must read this before editing Globe/weather code (see `.cursor/rules/GLOBE_WEATHER.mdc`).

---

## App and file

- **App:** `apps/Globe/IONv4c-weather.html` (ION Engine – Weather GCM).
- **Other:** `apps/Globe/IONv4a.html` (water world, no weather); `apps/Globe/IONv4c.html` (different variant). Do not assume they share the same logic.

---

## What "Weather ON" is supposed to do

- **Weather OFF:** Clouds come from legacy FBM only (`getCloudDensityLegacy`). Only control is Cloud Coverage (threshold on noise).
- **Weather ON:** Clouds come from the GCM texture (T, q, u, v) via `getCloudDensity(p, time, weatherUV, uWeatherTex)`. That should produce **different patterns** (stratus, cloud streets, squalls) driven by the sim, not the same FBM as Weather OFF. Coverage should **scale** that pattern, not replace it.

---

## What "done" means for the next task

- (Fill in when you have a specific task, e.g. "Weather ON shows visibly different clouds from Weather OFF" or "Coverage only scales the GCM pattern.")

---

## Known issues / recent fixes

- **Legacy fallback removed (2025-02-23):** When Weather was ON, the code still blended in legacy clouds when `totalWeight < 0.05`, so it looked like "Weather OFF + a bit more coverage." The legacy fallback inside `getCloudDensity` was removed so Weather ON only uses GCM-driven density. Coverage was changed from subtract to multiply: `finalDensity *= (0.25 + 0.75 * uCloudCoverage)`.
- (Add new issues or fixes below as they happen.)

---

## Do not assume

- That the implementation matches `docs/ION_WEATHER_GCM_IMPLEMENTATION_PLAN.md` (that plan may be outdated).
- That "weather" is on by default (it is a toggle; FBOs and sim are created when the user turns Weather on).
