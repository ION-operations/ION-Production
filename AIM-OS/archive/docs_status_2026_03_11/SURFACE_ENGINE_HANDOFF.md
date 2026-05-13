# Surface Engine Integration — Handoff

## What Was Built

6 files in `packages/joc/src/engine/`:

| File | Purpose |
|------|---------|
| `surface-engine-core.ts` | Schema, backend detection, CSS property registration, math |
| `surface-engine-motion.ts` | Hooke's Law spring physics, pointer tracking |
| `surface-engine-css.ts` | CSS compiler: toggle, button, panel material recipes |
| `surface-engine-webgpu.ts` | WGSL shader: SDF shapes, per-pixel lighting, caustics |
| `webgpu.d.ts` | WebGPU type declarations |

First component: `packages/joc/src/components/surface/SkeuShaderToggle.tsx`
Demo page: `packages/joc/src/pages/SurfaceEngineDemo.tsx` (routed as `'surface-demo'`)

## NOT YET DONE

- **Toggle NOT visually verified in browser** — demo page has no menu item, need to call `addTab('Surface Demo', 'surface-demo')` on Zustand store
- Material presets file (`surface-engine-materials.ts`)
- `SkeuButton`, `SkeuPanel`, `SkeuSlider` components
- Rebuilding actual JOC pages with Surface Engine materials

## The Canon

**5 Laws of CSS Skeuomorphism:**
1. Global Light Source — all shadows agree on one direction
2. Material Volume — gradients for curvature, never flat
3. 3-Tier Cast Shadow — contact + umbra + penumbra
4. Inverse Cut (Micro-Bevels) — machined edges catch light
5. Negative Spread — tapered shadows for cylindrical geometry

**Material Presets:** polymer.soft, ceramic.gloss, metal.anodized, glass.acrylic.soft, rubber.tactile, gel.capsule

**The vision:** CIA + JARVIS + DSLR camera body. Every page modeled after a real-world device.

**Reference:** `C:\Users\bombe\Documents\Application_Dev\LucidEngine\src\components\ui-editor\PremiumPanelSystem.tsx`

## Page Rebuild Roadmap

| Page | Analogue |
|------|----------|
| Dashboard | NASA Mission Control |
| Diagnostics | DSLR camera LCD |
| Agent Comms | CIA secure terminal |
| Fleet Status | Navy CIC |
| Session Health | ICU monitor |
| Oracle | JARVIS AI |
| System Atlas | Telescope control |
| Compute | Server rack panel |

## Services

- MCP: `python lucid_mcp_server.py` (stdio) + `python scripts/mcp_http_fallback_server.py --port 5001`
- JOC: `npm run dev` in `packages/joc` → port 5011
- Branch: `opus/M-42/joc-build`
