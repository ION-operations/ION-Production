# Shadertoy al-ro Harness - Runbook

This document is a practical guide for running, debugging, and safely iterating on the harness.

## 1) Run

- Launcher: `gpt-volumetric-clouds/shadertoy-alro-harness/launch-shadertoy-alro-harness.bat`
- Manual:
  - `cd gpt-volumetric-clouds/shadertoy-alro-harness`
  - `python -m http.server 5173`
  - Open `http://localhost:5173/`

## 2) Controls

### Orbit mode

- Click-drag on the canvas to rotate the view.
- Mouse wheel adjusts camera FOV (zoom via FOV).

### Free flight mode

- Switch mode in the Flight tab.
- Click the canvas to enter pointer lock (Esc exits pointer lock).
- Movement:
  - `W/S`: forward/back
  - `A/D`: left/right
  - `Q/E`: down/up
  - `Shift`: speed boost
- Mouse wheel adjusts camera FOV.

## 3) Expected noise vs bugs

### Expected: jitter/noise when TAA is off

The shader uses per-pixel ray jitter to avoid banding. Without temporal accumulation, this appears as visible grain.

### Expected: ghosting when TAA alpha is low

`accum.glsl` blends `history -> current` with an exponential moving average:

- Higher alpha: more responsive, less smoothing
- Lower alpha: smoother, but more temporal lag / ghosting

### Free flight + TAA: why grain returns while moving

Reprojection in `accum.glsl` is rotation-only (directional). Free flight includes translation, so reprojection is disabled.
To avoid smear/darkening from sampling mismatched history, the harness resets history while moving when reprojection is off.

What you should expect:
- While moving in free flight: more visible grain (history is not accumulated across motion)
- When you stop moving: history accumulates again and the image smooths out

## 4) Common diagnostics

### Shader compilation fails

- Check the Status tab -> Errors drawer.
- The harness wraps Shadertoy shaders at runtime. If wrapping fails, WebGL compile errors can look like:
  - missing `precision`
  - undeclared `iResolution/iTime/iChannel0`

### God rays look misaligned

- God rays use a projected light UV computed from:
  - current camera direction
  - camera up vector
  - FOV
  - light direction (azimuth + elevation)
- If the light "slides" while moving, check whether the camera motion and the projection math are using the same camera basis.

## 5) Recovery / Forensics

- Safe copies are kept under `forensics_backups/`.
- The project has backups for the harness and for related apps, e.g.:
  - `forensics_backups/shadertoy-alro-harness_.../`
  - `forensics_backups/volumetric-clouds-iquilez_.../`

If something gets overwritten, we can restore from the most recent timestamped backup.
