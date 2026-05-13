# Shadertoy al-ro Harness - Master Index

Date: 2026-01-13  
Purpose: Single navigation hub + unambiguous reference for this harness  
Status: Active development

## Start Here

- System Architecture Map (S.A.M.): `gpt-volumetric-clouds/shadertoy-alro-harness/docs/SYSTEM_ARCHITECTURE_MAP.json5`
- Project README: `gpt-volumetric-clouds/shadertoy-alro-harness/README.md`
- Runbook / debugging guide: `gpt-volumetric-clouds/shadertoy-alro-harness/docs/RUNBOOK.md`

## Run / Launch

- Windows launcher: `gpt-volumetric-clouds/shadertoy-alro-harness/launch-shadertoy-alro-harness.bat`
- Manual:
  - `cd gpt-volumetric-clouds/shadertoy-alro-harness`
  - `python -m http.server 5173`
  - Open `http://localhost:5173/`

## Key Files

- UI shell (overlay + tab layout): `gpt-volumetric-clouds/shadertoy-alro-harness/index.html`
- Orchestrator + render loop + UI wiring: `gpt-volumetric-clouds/shadertoy-alro-harness/main.js`
- Shaders (Shadertoy-style, wrapped at runtime):
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/bufferA.glsl`
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/bufferB.glsl`
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/image.glsl`
- Post passes:
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/accum.glsl` (TAA-lite)
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/godrays.glsl`

## Render Pipeline (High-Level)

1. BufferA (1x4): mouse tracking + legacy view-direction storage + resolution-change flags
2. BufferB (full res, rebuild-on-demand): Perlin-Worley atlas + cloud map + moon texture
3. Image (full res): volumetric clouds render (alpha carries transmittance)
4. Optional TAA accumulation: blend current frame into history (optionally reprojected)
5. Optional God rays: radial blur post using projected light UV + scene texture
6. Blit: present to canvas

## Camera Modes (Current)

- Orbit:
  - Click-drag to rotate (matches al-ro BufferA motion scaling).
  - Camera position is fixed; only view direction changes.
  - Reprojection is supported (rotation-only).
- Free flight:
  - Click canvas to enter pointer lock (Esc to exit).
  - WASD move, Q/E down/up, Shift boost.
  - Basic inertia/bank controls exist (more planned).
  - Reprojection is disabled (translation is not yet reprojected).

## Settings UI (Current)

- Right-side overlay provides:
  - tab bar (left column)
  - scrollable panel area (right column)
  - collapsible drawers inside each tab
  - collapse button (hides the panel body, keeps header)
- Tabs/drawers are created in `initControls()` inside `gpt-volumetric-clouds/shadertoy-alro-harness/main.js`.

## Known Problem Areas

- Shaky / grainy clouds:
  - Without temporal accumulation, the shader's ray jitter is visible (expected: noise instead of banding).
  - With temporal accumulation, low alpha can produce ghosting while moving (expected tradeoff).
  - In free-flight mode, reprojection is off; the harness resets history while moving to avoid smear (expect more grain while moving).

## Forensics / Recovery

- Timestamped backups are kept under `forensics_backups/` (safe copies for recovery from accidental overwrites).
