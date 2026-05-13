// SkeuShaderToggle.tsx
// ═══════════════════════════════════════════════════════════════════
// The flagship Surface Engine component.
//
// A physically-rendered toggle switch that looks like a machined
// glass puck sliding inside a CNC-milled aluminum cavity. Inspired
// by high-end DSLR camera bodies — the kind where every control
// has weight, texture, and mechanical precision.
//
// Features:
//   - Auto-resolves CSS vs WebGPU backend
//   - Frosted glass knob with convex dome gradient
//   - Caustic bloom under the knob (light concentrating through glass)
//   - Spring-physics toggle travel with overshoot and damping
//   - Pointer-reactive tilt and perspective rotation
//   - Specular hotspot that chases the cursor
//   - Kinetic stretch during high-velocity travel
//   - Reduced-motion aware
//   - ARIA accessible
// ═══════════════════════════════════════════════════════════════════

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
    registerSurfaceProperties,
    resolveSurfaceBackend,
    type SurfaceBackend,
    type SurfaceNode,
    type ThemeMode,
} from '../../engine/surface-engine-core';
import { useSurfaceInteraction } from '../../engine/surface-engine-motion';
import { compileGlassToggleCss } from '../../engine/surface-engine-css';
import { SurfaceWebGPURenderer } from '../../engine/surface-engine-webgpu';

// ─── SVG Material Shaders ────────────────────────────────────────
// These inject micro-surface noise that breaks the mathematical
// perfection of CSS gradients. Real materials have grain.

function DOMShaders() {
    return (
        <svg
            style={{
                width: 0,
                height: 0,
                position: 'absolute',
                pointerEvents: 'none',
            }}
            aria-hidden
        >
            <defs>
                {/* Anisotropic machined metal grain */}
                <filter id="sx-brushed-metal">
                    <feTurbulence
                        type="fractalNoise"
                        baseFrequency="0.01 2"
                        numOctaves={3}
                        result="noise"
                    />
                    <feColorMatrix
                        type="matrix"
                        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.06 0"
                        in="noise"
                        result="coloredNoise"
                    />
                    <feBlend in="SourceGraphic" in2="coloredNoise" mode="multiply" />
                </filter>

                {/* Frosted glass micro-roughness */}
                <filter id="sx-frosted-glass">
                    <feTurbulence
                        type="fractalNoise"
                        baseFrequency="1.5"
                        numOctaves={3}
                        result="noise"
                    />
                    <feColorMatrix
                        type="matrix"
                        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.04 0"
                        in="noise"
                        result="coloredNoise"
                    />
                    <feBlend in="SourceGraphic" in2="coloredNoise" mode="screen" />
                </filter>
            </defs>
        </svg>
    );
}

// ─── Component Props ─────────────────────────────────────────────

interface SkeuShaderToggleProps {
    /** Current toggle state */
    checked: boolean;
    /** Called when the toggle is clicked */
    onChange: (value: boolean) => void;
    /** Color theme */
    theme?: ThemeMode;
    /** Rendering backend override (default: auto-detect) */
    backend?: SurfaceBackend;
    /** Width in pixels */
    width?: number;
    /** Height in pixels */
    height?: number;
    /** Accessible label */
    label?: string;
    /** Enable WebGPU hero rendering when available */
    hero?: boolean;
    /** Optional className for outer wrapper */
    className?: string;
}

// ─── The Component ───────────────────────────────────────────────

export function SkeuShaderToggle({
    checked,
    onChange,
    theme = 'dark',
    backend = 'auto',
    width = 256,
    height = 112,
    label = 'Toggle switch',
    hero = true,
    className,
}: SkeuShaderToggleProps) {
    const { sim, bind } = useSurfaceInteraction(checked);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const rendererRef = useRef<SurfaceWebGPURenderer | null>(null);
    const [gpuReady, setGpuReady] = useState(false);

    // Build the SurfaceNode for backend resolution
    const node: SurfaceNode = useMemo(
        () => ({
            id: 'toggle',
            preset: 'glass.acrylic.soft',
            shape: 'capsule',
            width,
            height,
            hero,
        }),
        [width, height, hero],
    );

    const resolved = resolveSurfaceBackend(node, backend);

    // Register typed CSS custom properties once
    useEffect(() => {
        registerSurfaceProperties();
    }, []);

    // ─── WebGPU Initialization ─────────────────────────────────

    useEffect(() => {
        if (resolved !== 'webgpu') return;
        const canvas = canvasRef.current;
        if (!canvas) return;

        let cancelled = false;

        (async () => {
            try {
                const renderer = new SurfaceWebGPURenderer();
                await renderer.init(canvas);
                if (cancelled) return;
                rendererRef.current = renderer;
                setGpuReady(true);
            } catch {
                // Fallback to CSS silently
                setGpuReady(false);
            }
        })();

        return () => {
            cancelled = true;
            rendererRef.current?.destroy();
            rendererRef.current = null;
        };
    }, [resolved]);

    // ─── WebGPU Render Loop ────────────────────────────────────

    useEffect(() => {
        if (resolved !== 'webgpu' || !gpuReady) return;
        const canvas = canvasRef.current;
        const renderer = rendererRef.current;
        if (!canvas || !renderer) return;

        let raf = 0;
        const startTime = performance.now();

        const frame = (now: number) => {
            renderer.render(canvas, {
                width,
                height,
                checked,
                theme,
                time: (now - startTime) / 1000,
                sim,
            });
            raf = requestAnimationFrame(frame);
        };

        raf = requestAnimationFrame(frame);
        return () => cancelAnimationFrame(raf);
    }, [resolved, gpuReady, width, height, checked, theme, sim]);

    // ─── Click Handler ─────────────────────────────────────────

    const handleClick = () => onChange(!checked);

    // ─── WebGPU Path ───────────────────────────────────────────

    if (resolved === 'webgpu' && gpuReady) {
        return (
            <div className={className} style={{ display: 'inline-block' }}>
                <DOMShaders />
                <button
                    type="button"
                    aria-pressed={checked}
                    aria-label={label}
                    onClick={handleClick}
                    style={{
                        width,
                        height,
                        padding: 0,
                        border: 'none',
                        background: 'transparent',
                        cursor: 'pointer',
                        borderRadius: 999,
                        overflow: 'hidden',
                        display: 'inline-block',
                        WebkitTapHighlightColor: 'transparent',
                    }}
                    {...bind}
                >
                    <canvas
                        ref={canvasRef}
                        style={{
                            width: '100%',
                            height: '100%',
                            display: 'block',
                            borderRadius: 999,
                        }}
                    />
                </button>
            </div>
        );
    }

    // ─── CSS Path ──────────────────────────────────────────────

    const css = compileGlassToggleCss({
        theme,
        checked,
        sim,
        width,
        height,
    });

    return (
        <div className={className} style={{ display: 'inline-block' }}>
            <DOMShaders />
            <button
                type="button"
                aria-pressed={checked}
                aria-label={label}
                onClick={handleClick}
                style={css.root}
                {...bind}
            >
                {/* Track: the machined cavity (LAW 3: 3-tier shadows) */}
                <span aria-hidden style={css.track} />

                {/* Inner well polish (micro-bevel) */}
                <span aria-hidden style={css.well} />

                {/* Caustic pass: light concentrated under glass */}
                <span aria-hidden style={css.caustic} />

                {/* Knob: the convex glass puck (LAW 2: dome gradient) */}
                <span aria-hidden style={css.knob}>
                    {/* Specular polish layer */}
                    <span aria-hidden style={css.knobInner} />
                </span>
            </button>
        </div>
    );
}

export default SkeuShaderToggle;
