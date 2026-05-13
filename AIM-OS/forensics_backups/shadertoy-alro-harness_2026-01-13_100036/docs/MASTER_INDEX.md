# Shadertoy al-ro Harness — Master Index

**Date:** 2026-01-13  
**Purpose:** Single navigation hub + “no ambiguity” reference for this harness  
**Status:** Active development

## Start Here

- **System Architecture Map (S.A.M.)**: `gpt-volumetric-clouds/shadertoy-alro-harness/docs/SYSTEM_ARCHITECTURE_MAP.json5`
- **Project README**: `gpt-volumetric-clouds/shadertoy-alro-harness/README.md`
- **Al-ro reference notes (repo-level)**: `gpt-volumetric-clouds/docs/SHADERTOY_ALRO_REFERENCE.md`

## Run / Launch

- **Windows launcher**: `gpt-volumetric-clouds/shadertoy-alro-harness/launch-shadertoy-alro-harness.bat`
- **Manual**:
  - `cd gpt-volumetric-clouds/shadertoy-alro-harness`
  - `python -m http.server 5173`
  - Open `http://localhost:5173/`

## Key Files

- UI shell: `gpt-volumetric-clouds/shadertoy-alro-harness/index.html`
- Runtime + render loop: `gpt-volumetric-clouds/shadertoy-alro-harness/main.js`
- Shaders (Shadertoy-style, wrapped at runtime):
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/bufferA.glsl`
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/bufferB.glsl`
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/image.glsl`
- Post passes:
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/accum.glsl` (TAA-lite)
  - `gpt-volumetric-clouds/shadertoy-alro-harness/shaders/godrays.glsl`

## Render Pipeline (High-Level)

1. **BufferA** (1x4): mouse tracking + view direction + resolution-change flags  
2. **BufferB** (full res, rebuild-on-demand): Perlin-Worley atlas + cloud map + moon texture  
3. **Image** (full res): volumetric clouds render (alpha carries transmittance)  
4. Optional **TAA accumulation**: blend current frame into history with optional reprojection  
5. Optional **God rays**: radial blur post using projected light UV + scene transmittance  
6. **Blit**: present to canvas

## Settings UI (What Exists Today)

- Right-side overlay uses:
  - icon tab bar (left column)
  - scrollable tab panel (right column)
  - collapse button (hides panels, keeps header)
- Tabs are created in `initControls()` inside `gpt-volumetric-clouds/shadertoy-alro-harness/main.js`.

## Known Problem Areas (Current)

- **Camera / input correctness**
  - Mouse coordinates are currently stored from DOM events and must match the shader’s `iResolution` pixel space and Y-origin expectation.
  - Keyboard events are currently bound to the canvas; if the canvas isn’t focused, flight controls won’t work.
- **“Super shakey” reports**
  - Usually indicates mismatch between camera motion used for rendering vs motion used for reprojection (TAA), or mis-scaled mouse inputs.
  - Treat this as a pipeline consistency bug: camera motion + reprojection must share a single source of truth.

## Forensics / Recovery

- There are timestamped backups under `forensics_backups/` (safe copies + manifests) that can be used to recover from accidental overwrites.

## Next Work (Roadmap for This Harness)

1. Fix mouse coordinate mapping (pixel scaling + correct Y origin).
2. Make camera controls professional: orbit (rotate/pan/zoom) + true free-flight mode + on-screen control legend.
3. Stabilize TAA during motion (reprojection correctness + drag-specific settings).
4. Expand settings coverage without bloating: structured groups, search/filter, presets.

