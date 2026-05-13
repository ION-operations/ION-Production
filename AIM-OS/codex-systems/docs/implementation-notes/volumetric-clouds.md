# Volumetric Clouds (Codex Systems)

**Status:** Scaffolding started  
**Encyclopedia References:**  
- `docs/encyclopedia/VOLUMETRIC_CLOUDS_RAYMARCHING_COMPLETE.md`  
- `docs/encyclopedia/03_Rendering/Volumetric/VOLUMETRIC_RENDERING_COMPLETE.md`  

## Plan
- Raymarcher with step count tuned for perf (quality vs speed tiers).
- 3D noise: FBM + Worley, blendable; temporal evolution.
- Lighting: single-scatter with Henyey-Greenstein; ambient + light absorption.
- God rays: integrate directional light; optional screen-space shafts.
- Dynamic presets: cumulus, stratus, cirrus.
- Demo: R3F/Three scene with adjustable params.

## Current Scaffolding
- `CloudGenerator.ts`: settings structures + defaults.
- `CloudRenderer.ts`: placeholder renderer with settings/resolution accessors.
- `shaders/cloud.vert|frag`: fullscreen pass stub; raymarch TODO.

## Next Steps
- Generate 3D noise (texture3D or tiled 2D slices) on CPU/GPU.
- Implement raymarch loop with early-exit and shadow marching.
- Add Henyey-Greenstein phase function and light absorption.
- Add quality tiers (low/med/high) controlling steps and noise resolution.
- Build demo under `demos/volumetric-demo/clouds-demo.tsx`.

## Success Criteria
- Photorealistic cloud look at medium/high tiers.
- 30+ FPS at 1080p (medium tier); lower res for low tier.
- Adjustable presets for different cloud types.

