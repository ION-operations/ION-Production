// surface-engine-core.ts
// ═══════════════════════════════════════════════════════════════════
// The bedrock of the Surface Engine. Every control is a material
// specimen, not a styled div. This file defines the node schema,
// backend resolution, typed CSS property registration, and math.
// ═══════════════════════════════════════════════════════════════════

export type ThemeMode = 'light' | 'dark';
export type SurfaceBackend = 'auto' | 'css' | 'paint' | 'webgpu';

export type SurfacePreset =
    | 'polymer.soft'
    | 'ceramic.gloss'
    | 'metal.anodized'
    | 'metal.brushed'
    | 'glass.acrylic.soft'
    | 'glass.acrylic.hard'
    | 'rubber.tactile'
    | 'gel.capsule';

export type SurfaceShape =
    | 'rounded-rect'
    | 'capsule'
    | 'circle'
    | 'ring';

export interface SurfaceNode {
    id: string;
    preset: SurfacePreset;
    shape: SurfaceShape;
    width: number;
    height: number;
    hero?: boolean;
    borderRadius?: number;
}

// ─── Backend Detection ───────────────────────────────────────────

let _supportsWebGPU: boolean | null = null;
let _supportsPaintWorklet: boolean | null = null;

export function supportsWebGPU(): boolean {
    if (_supportsWebGPU === null) {
        _supportsWebGPU =
            typeof navigator !== 'undefined' && 'gpu' in navigator;
    }
    return _supportsWebGPU;
}

export function supportsPaintWorklet(): boolean {
    if (_supportsPaintWorklet === null) {
        _supportsPaintWorklet =
            typeof CSS !== 'undefined' && 'paintWorklet' in CSS;
    }
    return _supportsPaintWorklet;
}

export function resolveSurfaceBackend(
    node: SurfaceNode,
    requested: SurfaceBackend = 'auto',
): Exclude<SurfaceBackend, 'auto'> {
    if (requested !== 'auto') return requested;
    if (node.hero && supportsWebGPU()) return 'webgpu';
    if (supportsPaintWorklet()) return 'paint';
    return 'css';
}

// ─── Typed CSS Custom Properties ─────────────────────────────────
// These become our "shader uniforms" in CSS land. Registering them
// with syntax makes them interpolatable and GPU-compositable.

let didRegister = false;

export function registerSurfaceProperties(): void {
    if (didRegister) return;
    didRegister = true;

    if (
        typeof CSS === 'undefined' ||
        typeof CSS.registerProperty !== 'function'
    ) {
        return;
    }

    const props: Array<{
        name: string;
        syntax: string;
        inherits: boolean;
        initialValue: string;
    }> = [
            { name: '--sx-hover', syntax: '<number>', inherits: false, initialValue: '0' },
            { name: '--sx-press', syntax: '<number>', inherits: false, initialValue: '0' },
            { name: '--sx-hotspot-x', syntax: '<percentage>', inherits: false, initialValue: '50%' },
            { name: '--sx-hotspot-y', syntax: '<percentage>', inherits: false, initialValue: '50%' },
            { name: '--sx-travel', syntax: '<number>', inherits: false, initialValue: '0' },
            { name: '--sx-caustic', syntax: '<number>', inherits: false, initialValue: '0' },
            { name: '--sx-tilt-x', syntax: '<number>', inherits: false, initialValue: '0' },
            { name: '--sx-tilt-y', syntax: '<number>', inherits: false, initialValue: '0' },
            { name: '--sx-lift', syntax: '<length>', inherits: false, initialValue: '0px' },
            { name: '--sx-depth', syntax: '<length>', inherits: false, initialValue: '0px' },
        ];

    for (const prop of props) {
        try {
            CSS.registerProperty({
                name: prop.name,
                syntax: prop.syntax,
                inherits: prop.inherits,
                initialValue: prop.initialValue,
            });
        } catch {
            // Ignore duplicate registration or unsupported syntax
        }
    }
}

// ─── Math Utilities ──────────────────────────────────────────────

export function clamp01(v: number): number {
    return v < 0 ? 0 : v > 1 ? 1 : v;
}

export function clamp(v: number, min: number, max: number): number {
    return v < min ? min : v > max ? max : v;
}

export function lerp(a: number, b: number, t: number): number {
    return a + (b - a) * t;
}

export function mapRange(
    value: number,
    inMin: number,
    inMax: number,
    outMin: number,
    outMax: number,
): number {
    const t = clamp01((value - inMin) / (inMax - inMin || 1));
    return lerp(outMin, outMax, t);
}

export function smoothstep(edge0: number, edge1: number, x: number): number {
    const t = clamp01((x - edge0) / (edge1 - edge0));
    return t * t * (3 - 2 * t);
}
