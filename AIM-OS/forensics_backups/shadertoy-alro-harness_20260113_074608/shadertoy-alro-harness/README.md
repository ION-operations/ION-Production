# Shadertoy al-ro Clouds Harness (Isolated)

Purpose
- Run the **multi-buffer Shadertoy pipeline** (BufferA + BufferB + Image) locally in WebGL2 so we can:
  - validate the shader as a correctness / lighting reference
  - extract ideas (Perlin-Worley atlas, multiple scattering approximation, energy-conserving integration)
  - compare against our production volumetrics plan

What this is
- A tiny **no-deps** WebGL2 harness.
- Implements Shadertoy-style uniforms:
  - `iResolution`, `iTime`, `iFrame`, `iMouse`
  - `iChannel0..3`, `iChannelResolution[4]`
- Implements feedback buffers:
  - BufferA reads previous BufferA (mouse tracking + resolution change)
  - BufferB reads previous BufferB (atlas persistence) and reads BufferA

How to run
1) Serve this folder (module + shader fetches require `http://`, not `file://`):
   - From repo root: `cd gpt-volumetric-clouds/shadertoy-alro-harness`
   - Then: `python -m http.server 5173`
2) Open `http://localhost:5173/` in a modern browser (WebGL2 required).
3) Drag mouse to rotate the view.

Settings UI
- Use the top-left overlay to tweak options live (no reload needed for most knobs).
- Settings are grouped into collapsible drawers (`Render`, `Temporal (TAA)`, `Lighting`, `God Rays`, `Share`).
- `Status / Debug` is its own drawer (closed by default) and contains the live settings readout + errors.

Presets
- Fast + crisp: `http://localhost:5173/?preset=fast-crisp`
- Smooth: `http://localhost:5173/?preset=smooth`
- Override example (preset + manual tweaks): `http://localhost:5173/?preset=smooth&scale=0.6&taaAlpha=0.1`

Lighting (Moon ↔ Sun)
- Toggle night/day: `?lighting=night` or `?lighting=day`
- Light direction: `?lightAz=220&lightH=0.25` (azimuth in degrees, elevation is the y component before normalization)
- If you set `lighting=day` without extra params, the harness seeds reasonable day defaults automatically.

God Rays
- Toggle: `?godrays=1`
- Useful knobs:
  - `?godraysSamples=48` (cost)
  - `?godraysIntensity=1.0`
  - `?godraysDecay=0.965`
  - `?godraysWeight=0.02`
  - `?godraysDensity=0.95`
  - `?godraysRadius=1.0` (scales source disk radius)
  - `?godraysDuringDrag=0` (default; disables rays while dragging for FPS)

Performance
- Use `?scale=0.5` (or `0.33`, etc) to reduce render cost: `http://localhost:5173/?scale=0.5`
- Use `?fast=1` to enable the shader's built-in lower-step mode.

Notes
- Requires `EXT_color_buffer_float` (float render targets). If missing, the overlay shows an error.
- The blue-noise channel is currently a randomly-generated 1024x1024 tile (good enough for dithering, but not true blue-noise yet).
- The Perlin-Worley atlas expects linear filtering (it includes halo padding for seamless bilinear sampling). If float-linear filtering isn't supported, the harness falls back to RGBA8 for BufferB to keep linear sampling and avoid blocky "column" artifacts.
- Temporal accumulation is enabled by default to reduce dithering grain:
  - Disable: `?taa=0`
  - Tweak blend: `?taaAlpha=0.08` (lower = smoother but more lag/ghosting)
  - Reduce lag while moving: `?taaUseDragAlpha=1&taaAlphaDrag=0.25` (higher = more responsive, noisier)
  - Disable reprojection: `?reproject=0` (more stable under mismatch, worse while rotating)
  - Allow accumulation while dragging: `?taaDuringDrag=1`
  - Improve FPS while dragging: `?fastWhileDrag=1` (uses the shader's `#define FAST` only while mouse is down)
- `shaders/image.glsl` outputs **cloud transmittance in alpha** (used by the god-rays post pass).

License
- The GLSL code in `shaders/*.glsl` includes the original al-ro MIT license header (as provided in the shader).
