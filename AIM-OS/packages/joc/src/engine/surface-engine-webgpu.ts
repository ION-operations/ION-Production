// surface-engine-webgpu.ts
// ═══════════════════════════════════════════════════════════════════
// WebGPU Hero Backend — Per-pixel lighting, SDF shapes, caustics.
//
// This is the "tier 3" renderer. It draws a fullscreen quad and
// shades the toggle analytically in the fragment shader:
//   - SDF rounded-rect for the track
//   - SDF circle for the knob
//   - Height-derived normals for specular response
//   - Dynamic cast shadows from light direction
//   - Caustic bloom from glass refraction approximation
//   - Cavity ambient occlusion
// ═══════════════════════════════════════════════════════════════════

import type { ThemeMode } from './surface-engine-core';
import type { SurfaceSimState } from './surface-engine-motion';

export type WebGPUToggleParams = {
    width: number;
    height: number;
    checked: boolean;
    theme: ThemeMode;
    time: number;
    sim: SurfaceSimState;
};

export class SurfaceWebGPURenderer {
    private device!: GPUDevice;
    private context!: GPUCanvasContext;
    private format!: GPUTextureFormat;
    private pipeline!: GPURenderPipeline;
    private uniformBuffer!: GPUBuffer;
    private bindGroup!: GPUBindGroup;
    private ready = false;

    async init(canvas: HTMLCanvasElement): Promise<void> {
        const gpu = navigator.gpu;
        if (!gpu) {
            throw new Error('WebGPU not supported');
        }

        const adapter = await gpu.requestAdapter();
        if (!adapter) throw new Error('No GPU adapter found');

        this.device = await adapter.requestDevice();
        const context = canvas.getContext('webgpu');
        if (!context) throw new Error('WebGPU canvas context unavailable');

        this.context = context;
        this.format = gpu.getPreferredCanvasFormat();

        this.context.configure({
            device: this.device,
            format: this.format,
            alphaMode: 'premultiplied',
        });

        // Uniform buffer: 4 × vec4<f32> = 64 bytes
        this.uniformBuffer = this.device.createBuffer({
            size: 16 * 4,
            usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
        });

        const shader = this.device.createShaderModule({
            code: TOGGLE_WGSL,
        });

        this.pipeline = this.device.createRenderPipeline({
            layout: 'auto',
            vertex: {
                module: shader,
                entryPoint: 'vs',
            },
            fragment: {
                module: shader,
                entryPoint: 'fs',
                targets: [{ format: this.format }],
            },
            primitive: {
                topology: 'triangle-list',
            },
        });

        this.bindGroup = this.device.createBindGroup({
            layout: this.pipeline.getBindGroupLayout(0),
            entries: [
                {
                    binding: 0,
                    resource: { buffer: this.uniformBuffer },
                },
            ],
        });

        this.ready = true;
    }

    render(canvas: HTMLCanvasElement, params: WebGPUToggleParams): void {
        if (!this.ready) return;

        const dpr = window.devicePixelRatio || 1;
        const targetW = Math.max(1, Math.round(params.width * dpr));
        const targetH = Math.max(1, Math.round(params.height * dpr));

        if (canvas.width !== targetW || canvas.height !== targetH) {
            canvas.width = targetW;
            canvas.height = targetH;
            this.context.configure({
                device: this.device,
                format: this.format,
                alphaMode: 'premultiplied',
            });
        }

        // Pack uniforms: 4 × vec4<f32>
        const u = new Float32Array(16);
        u[0] = targetW;                       // a.x: width
        u[1] = targetH;                       // a.y: height
        u[2] = params.time;                   // a.z: time
        u[3] = params.checked ? 1 : 0;        // a.w: checked

        u[4] = params.sim.hoverAmount;        // b.x: hover
        u[5] = params.sim.pressAmount;        // b.y: press
        u[6] = params.theme === 'dark' ? 1 : 0; // b.z: dark
        u[7] = params.sim.toggleTravel;       // b.w: travel

        u[8] = params.sim.hotspotX;           // c.x: hotspotX
        u[9] = params.sim.hotspotY;           // c.y: hotspotY
        u[10] = params.sim.causticEnergy;     // c.z: caustic
        u[11] = dpr;                          // c.w: dpr

        u[12] = params.sim.velocity;          // d.x: velocity (for stretch)
        // u[13..15] reserved

        this.device.queue.writeBuffer(this.uniformBuffer, 0, u);

        const encoder = this.device.createCommandEncoder();
        const pass = encoder.beginRenderPass({
            colorAttachments: [
                {
                    view: this.context.getCurrentTexture().createView(),
                    clearValue: { r: 0, g: 0, b: 0, a: 0 },
                    loadOp: 'clear',
                    storeOp: 'store',
                },
            ],
        });

        pass.setPipeline(this.pipeline);
        pass.setBindGroup(0, this.bindGroup);
        pass.draw(6, 1, 0, 0);
        pass.end();

        this.device.queue.submit([encoder.finish()]);
    }

    destroy(): void {
        this.uniformBuffer?.destroy();
        this.ready = false;
    }
}

// ─── WGSL Shader ─────────────────────────────────────────────────
// Analytic SDF toggle with per-pixel lighting, cavity AO,
// specular response, and caustic bloom approximation.

const TOGGLE_WGSL = /* wgsl */ `
struct Uniforms {
  a: vec4f, // width, height, time, checked
  b: vec4f, // hover, press, themeDark, travel
  c: vec4f, // hotspotX, hotspotY, caustic, dpr
  d: vec4f, // velocity, reserved, reserved, reserved
};

@group(0) @binding(0) var<uniform> u: Uniforms;

struct VSOut {
  @builtin(position) position: vec4f,
  @location(0) uv: vec2f,
};

// Fullscreen triangle-strip quad
@vertex
fn vs(@builtin(vertex_index) vi: u32) -> VSOut {
  var pos = array<vec2f, 6>(
    vec2f(-1.0, -1.0), vec2f( 1.0, -1.0), vec2f(-1.0,  1.0),
    vec2f(-1.0,  1.0), vec2f( 1.0, -1.0), vec2f( 1.0,  1.0)
  );
  var out: VSOut;
  out.position = vec4f(pos[vi], 0.0, 1.0);
  out.uv = pos[vi] * 0.5 + 0.5;
  return out;
}

// ─── SDF Primitives ──────────────────────────────────────────

fn sdRoundRect(p: vec2f, b: vec2f, r: f32) -> f32 {
  let q = abs(p) - b + vec2f(r);
  return length(max(q, vec2f(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

fn sdCircle(p: vec2f, r: f32) -> f32 {
  return length(p) - r;
}

// ─── Fragment Shader ─────────────────────────────────────────

@fragment
fn fs(in: VSOut) -> @location(0) vec4f {
  let uv = in.uv;
  let time = u.a.z;
  let checked = u.a.w;
  let hover = u.b.x;
  let press = u.b.y;
  let dark = u.b.z > 0.5;
  let travel = u.b.w;
  let hotspot = u.c.xy;
  let causticE = u.c.z;
  let velocity = u.d.x;

  // ── GEOMETRY ───────────────────────────────────────────

  // Track: centered capsule
  let trackCenter = vec2f(0.5, 0.5);
  let trackHalf = vec2f(0.47, 0.44);
  let trackR = 0.44;
  let trackSdf = sdRoundRect(uv - trackCenter, trackHalf, trackR);

  // Knob: sliding circle
  let knobCx = mix(0.26, 0.74, travel);
  let knobCy = 0.5 + press * 0.012;
  let knobR = 0.38;
  let knobSdf = sdCircle(uv - vec2f(knobCx, knobCy), knobR);

  // Discard outside track
  if (trackSdf > 0.005) {
    return vec4f(0.0, 0.0, 0.0, 0.0);
  }

  // Anti-alias edge
  let trackAlpha = 1.0 - smoothstep(-0.005, 0.005, trackSdf);

  // ── LIGHTING RIG ───────────────────────────────────────

  // Key light: top-left, slightly forward
  let keyDir = normalize(vec3f(-0.5, -0.7, 0.8));
  // Fill: front
  let fillDir = normalize(vec3f(0.0, 0.0, 1.0));

  // ── TRACK MATERIAL ─────────────────────────────────────

  // Cavity normal: slight slope inward
  let trackNormal = normalize(vec3f(
    (uv.x - 0.5) * -0.08,
    (uv.y - 0.5) * -0.15,
    1.0
  ));

  // Base albedo with volume gradient (LAW 2)
  var trackBase: vec3f;
  if (dark) {
    trackBase = mix(
      vec3f(0.11, 0.14, 0.19),
      vec3f(0.05, 0.07, 0.10),
      uv.y
    );
  } else {
    trackBase = mix(
      vec3f(0.90, 0.93, 0.97),
      vec3f(0.76, 0.82, 0.88),
      uv.y
    );
  }

  // Cavity AO (darker in the well)
  let cavityDepth = smoothstep(-0.01, -0.15, trackSdf);
  let cavityDark = cavityDepth * (0.30 + 0.18 * uv.y);

  // Diffuse
  let trackDiff = max(dot(trackNormal, keyDir), 0.0) * 0.12;

  // Active state glow
  let glowDist = length(uv - vec2f(knobCx, 0.5));
  let activeGlow = exp(-glowDist * glowDist * 18.0) * (0.06 + 0.16 * checked);

  // Caustic bloom under the knob (light concentrating through glass)
  let causticPhase = sin(time * 1.2 + uv.x * 18.0) * 0.003;
  let causticP = uv - vec2f(knobCx + causticPhase, 0.68);
  let causticBloom = exp(-(causticP.x * causticP.x * 64.0 + causticP.y * causticP.y * 256.0)) * causticE;

  var trackColor = trackBase
    + vec3f(trackDiff)
    + vec3f(0.14, 0.44, 0.88) * activeGlow
    + vec3f(0.16, 0.62, 0.95) * causticBloom * 0.22
    - vec3f(cavityDark * 0.22);

  // Under-knob contact shadow
  let shadowP = uv - vec2f(knobCx, 0.58);
  let contactShadow = exp(-(shadowP.x * shadowP.x * 80.0 + shadowP.y * shadowP.y * 320.0))
    * (0.18 + press * 0.10);

  trackColor -= vec3f(contactShadow);

  // ── KNOB MATERIAL ──────────────────────────────────────

  // Derive normals from spherical height field
  let local = (uv - vec2f(knobCx, knobCy)) / knobR;
  let r2 = dot(local, local);
  let sphereZ = sqrt(max(0.0, 1.0 - r2));
  let knobNormal = normalize(vec3f(local.x, local.y, sphereZ));

  // Knob albedo with dome gradient
  var knobBase: vec3f;
  if (dark) {
    knobBase = mix(
      vec3f(0.18, 0.22, 0.30),
      vec3f(0.08, 0.10, 0.16),
      local.y * 0.5 + 0.5
    );
  } else {
    knobBase = mix(
      vec3f(0.98, 0.99, 1.0),
      vec3f(0.78, 0.84, 0.92),
      local.y * 0.5 + 0.5
    );
  }

  // Diffuse: key light
  let knobDiff = max(dot(knobNormal, keyDir), 0.0);

  // Specular: Blinn-Phong
  let halfVec = normalize(keyDir + fillDir);
  let specPow = mix(40.0, 85.0, 1.0 - press);
  let knobSpec = pow(max(dot(knobNormal, halfVec), 0.0), specPow);
  let specIntensity = 0.16 + hover * 0.14;

  // Hotspot glow (chases pointer)
  let hpVec = uv - hotspot;
  let hotspotGlow = exp(-dot(hpVec, hpVec) * 20.0);

  // Fresnel rim light
  let fresnel = pow(1.0 - sphereZ, 3.0) * 0.12;

  var knobColor = knobBase
    + vec3f(knobDiff * 0.16)
    + vec3f(knobSpec * specIntensity)
    + vec3f(fresnel)
    + vec3f(0.10, 0.28, 0.68) * hotspotGlow * 0.12;

  // ── COMPOSITE ──────────────────────────────────────────

  var finalColor: vec3f;
  if (knobSdf < -0.002) {
    finalColor = knobColor;
  } else if (knobSdf < 0.002) {
    // Anti-alias knob edge
    let knobBlend = 1.0 - smoothstep(-0.002, 0.002, knobSdf);
    finalColor = mix(trackColor, knobColor, knobBlend);
  } else {
    finalColor = trackColor;
  }

  // Micro rim on knob edge (LAW 4)
  let rimGlow = smoothstep(0.004, -0.008, knobSdf) * smoothstep(-0.025, -0.008, knobSdf);
  let rimColor = select(vec3f(0.08), vec3f(0.6), dark);
  finalColor += rimColor * rimGlow * 0.3;

  return vec4f(finalColor, trackAlpha);
}
`;
