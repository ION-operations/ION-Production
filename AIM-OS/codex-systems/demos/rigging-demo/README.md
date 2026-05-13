# Rigging Demo (Codex Systems)

**Status:** Skeleton in progress  
**Goal:** Visualize FABRIK and CCD IK solvers converging on targets.

## Planned Setup
- Simple React Three Fiber scene (or Three.js) inside `codex-systems/`
- Visualize a chain of bones (lines/spheres)
- Controls:
  - Switch solver (FABRIK / CCD)
  - Drag target in 3D
  - Adjust tolerance / iterations / stepFactor
- Display:
  - Iterations taken
  - Reached boolean
  - Distance to target

## Files to create
- `codex-systems/demos/rigging-demo/ik-demo.tsx` (R3F)
- `codex-systems/demos/rigging-demo/useIkDemo.ts` (state + hooks)

## Notes
- Keep demo isolated from main app (no `src/` imports)
- Use the solvers from `codex-systems/rigging/ik/*`
- Favor lightweight dependencies; use Three.js + R3F only if needed

