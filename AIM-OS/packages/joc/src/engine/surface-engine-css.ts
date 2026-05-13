// surface-engine-css.ts
// ═══════════════════════════════════════════════════════════════════
// CSS Backend Compiler — The 5 Laws of Skeuomorphism encoded.
//
// Every SurfaceNode compiles into layered backgrounds, stacked
// box-shadows, and blend modes. No solid colors. No flat shadows.
// Every layer has ONE job. Every highlight implies a matching shadow.
//
// Laws:
//   1. Global Light Source — all shadows agree on one direction
//   2. Material Volume — gradients for curvature, never flat
//   3. 3-Tier Cast Shadow — contact + umbra + penumbra
//   4. Inverse Cut (Micro-Bevels) — machined edges catch light
//   5. Negative Spread — tapered shadows for cylindrical geometry
// ═══════════════════════════════════════════════════════════════════

import type { ThemeMode } from './surface-engine-core';
import { lerp, mapRange } from './surface-engine-core';
import type { SurfaceSimState } from './surface-engine-motion';

// ─── Skeuomorphic Tokens ─────────────────────────────────────────

export interface SkeuTokens {
    // Base surfaces
    panel: string;
    trackTop: string;
    trackBottom: string;
    knobTop: string;
    knobMid: string;
    knobBottom: string;

    // Light response
    rimHi: string;
    rimHiSoft: string;
    rimLo: string;
    cavity: string;
    cavityDeep: string;
    contact: string;
    cast: string;
    spec: string;

    // State
    activeGlow: string;
    caustic: string;
    causticSoft: string;

    // Structure
    border: string;
}

export function getSkeuTokens(theme: ThemeMode): SkeuTokens {
    return theme === 'dark'
        ? {
            panel: '#0e1117',
            trackTop: '#1e2230',
            trackBottom: '#0a0d14',
            knobTop: '#2a3040',
            knobMid: '#1a2030',
            knobBottom: '#0f1520',

            rimHi: 'rgba(255,255,255,0.10)',
            rimHiSoft: 'rgba(255,255,255,0.05)',
            rimLo: 'rgba(0,0,0,0.75)',
            cavity: 'rgba(0,0,0,0.56)',
            cavityDeep: 'rgba(0,0,0,0.78)',
            contact: 'rgba(0,0,0,0.62)',
            cast: 'rgba(0,0,0,0.48)',
            spec: 'rgba(255,255,255,0.16)',

            activeGlow: 'rgba(98, 178, 255, 0.18)',
            caustic: 'rgba(122, 204, 255, 0.18)',
            causticSoft: 'rgba(122, 204, 255, 0.06)',

            border: 'rgba(255,255,255,0.04)',
        }
        : {
            panel: '#e7ebf0',
            trackTop: '#dfe4ea',
            trackBottom: '#bfc7d1',
            knobTop: '#f7f9fc',
            knobMid: '#e5eaf0',
            knobBottom: '#c8d0db',

            rimHi: 'rgba(255,255,255,0.92)',
            rimHiSoft: 'rgba(255,255,255,0.48)',
            rimLo: 'rgba(0,0,0,0.26)',
            cavity: 'rgba(0,0,0,0.16)',
            cavityDeep: 'rgba(0,0,0,0.26)',
            contact: 'rgba(0,0,0,0.24)',
            cast: 'rgba(0,0,0,0.22)',
            spec: 'rgba(255,255,255,0.72)',

            activeGlow: 'rgba(90, 155, 255, 0.18)',
            caustic: 'rgba(120, 196, 255, 0.28)',
            causticSoft: 'rgba(120, 196, 255, 0.10)',

            border: 'rgba(255,255,255,0.55)',
        };
}

// ─── Glass Toggle CSS Compiler ───────────────────────────────────

export type ToggleCssParts = {
    root: React.CSSProperties;
    track: React.CSSProperties;
    well: React.CSSProperties;
    caustic: React.CSSProperties;
    knob: React.CSSProperties;
    knobInner: React.CSSProperties;
};

export function compileGlassToggleCss(params: {
    theme: ThemeMode;
    checked: boolean;
    sim: SurfaceSimState;
    width?: number;
    height?: number;
}): ToggleCssParts {
    const { theme, sim } = params;
    const width = params.width ?? 256;
    const height = params.height ?? 112;
    const t = getSkeuTokens(theme);
    const dark = theme === 'dark';

    const knobSize = height - 8;
    const travel = width - knobSize - 8;
    const knobX = 4 + travel * sim.toggleTravel;

    const hotspotX = `${(sim.hotspotX * 100).toFixed(2)}%`;
    const hotspotY = `${(sim.hotspotY * 100).toFixed(2)}%`;

    // Tilt: perspective rotation from pointer position
    const rotX = (-sim.tiltX * 4).toFixed(2);
    const rotY = (sim.tiltY * 6).toFixed(2);
    const hoverLift = lerp(0, 4, sim.hoverAmount);
    const pressInset = lerp(0, 2.5, sim.pressAmount);

    // Caustic positioning
    const causticX = `${mapRange(sim.toggleTravel, 0, 1, 28, 72).toFixed(2)}%`;
    const causticScale = lerp(0.8, 1.15, sim.causticEnergy);

    // Kinetic stretch based on velocity
    const stretch = 1 + Math.min(Math.abs(sim.velocity) * 1.2, 0.08);

    return {
        // ─── Root (The Chassis) ──────────────────────────────────
        root: {
            position: 'relative',
            width,
            height,
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            borderRadius: 999,
            background: t.panel,
            transformStyle: 'preserve-3d',
            transform: `perspective(1200px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(${-hoverLift + pressInset}px)`,
            transition: 'transform 40ms linear',
            boxShadow: dark
                ? `0 ${(12 + hoverLift).toFixed(1)}px ${(32 + hoverLift * 2).toFixed(1)}px -14px rgba(0,0,0,0.55)`
                : `0 ${(10 + hoverLift).toFixed(1)}px ${(28 + hoverLift * 2).toFixed(1)}px -14px rgba(0,0,0,0.20)`,
            overflow: 'hidden',
            isolation: 'isolate' as const,
            userSelect: 'none' as const,
            WebkitTapHighlightColor: 'transparent',
        },

        // ─── Track (The Machined Cavity) ─────────────────────────
        // LAW 1: Light from top-left. LAW 2: Gradient curvature.
        // LAW 3: Layered cavity shadows. LAW 4: Micro-bevel rim.
        track: {
            position: 'absolute',
            inset: 0,
            borderRadius: 999,
            background: [
                // Sheen: radial catch from key light (top-left)
                `radial-gradient(120% 100% at 18% 10%, ${t.rimHiSoft} 0%, transparent 42%)`,
                // Active glow: subtle state indicator embedded in housing
                `radial-gradient(80% 60% at ${hotspotX} ${hotspotY}, ${t.activeGlow} 0%, transparent 42%)`,
                // Volume: top-to-bottom curvature gradient (LAW 2)
                `linear-gradient(180deg, ${t.trackTop} 0%, ${t.trackBottom} 100%)`,
            ].join(', '),
            boxShadow: [
                // LAW 4: Top micro-bevel catching light
                `inset 0 1px 1px ${t.rimHi}`,
                // LAW 1: Bottom compression shadow (light blocked)
                `inset 0 -6px 12px ${t.rimLo}`,
                // LAW 3, tier 1: Upper cavity shadow
                `inset 0 14px 18px ${t.cavity}`,
                // LAW 3, tier 2: Deep cavity darkness
                `inset 0 28px 38px ${t.cavityDeep}`,
                // LAW 4: Outer bottom micro-bevel
                `0 1px 0 ${t.border}`,
                // LAW 3, tier 3: Ambient penumbra
                `0 10px 22px -12px ${t.cast}`,
            ].join(', '),
        },

        // ─── Inner Well Polish ───────────────────────────────────
        well: {
            position: 'absolute',
            inset: 8,
            borderRadius: 999,
            background: `linear-gradient(180deg, transparent 0%, transparent 34%, ${dark ? 'rgba(0,0,0,0.14)' : 'rgba(0,0,0,0.05)'} 100%)`,
            boxShadow: [
                `inset 0 1px 0 ${t.rimHiSoft}`,
                `inset 0 -1px 0 ${dark ? 'rgba(0,0,0,0.55)' : 'rgba(0,0,0,0.14)'}`,
            ].join(', '),
            pointerEvents: 'none' as const,
        },

        // ─── Caustic Pass ────────────────────────────────────────
        // Light concentrates under the glass knob, projecting onto
        // the track floor. Moves inversely to the knob position.
        caustic: {
            position: 'absolute',
            inset: 10,
            borderRadius: 999,
            background: `radial-gradient(20% 50% at ${causticX} 70%, ${t.caustic} 0%, ${t.causticSoft} 36%, transparent 70%)`,
            transform: `scale(${causticScale.toFixed(3)}) translateY(${lerp(0, 2, sim.pressAmount).toFixed(2)}px)`,
            filter: `blur(${lerp(4, 8, sim.causticEnergy).toFixed(2)}px) saturate(${lerp(1.0, 1.35, sim.hoverAmount).toFixed(2)})`,
            opacity: lerp(0.35, 1, sim.causticEnergy),
            pointerEvents: 'none' as const,
            mixBlendMode: 'screen' as const,
        },

        // ─── Knob (The Convex Glass Puck) ────────────────────────
        // LAW 2: Convex dome gradient. LAW 3: Contact + cast.
        // LAW 5: Negative spread for cylindrical taper.
        knob: {
            position: 'absolute',
            top: 4,
            left: 4,
            width: knobSize,
            height: knobSize,
            borderRadius: '50%',
            transform: `translate3d(${knobX.toFixed(2)}px, ${pressInset.toFixed(2)}px, 0) scaleX(${stretch.toFixed(4)})`,
            transition: 'transform 40ms linear',
            willChange: 'transform' as const,
            // LAW 2: Convex dome — light top, dark bottom
            background: [
                // Specular hotspot chasing the pointer
                `radial-gradient(115% 115% at ${hotspotX} ${hotspotY}, ${t.spec} 0%, transparent 24%)`,
                // Volume gradient
                `linear-gradient(180deg, ${t.knobTop} 0%, ${t.knobMid} 55%, ${t.knobBottom} 100%)`,
            ].join(', '),
            boxShadow: [
                // LAW 4: Top rim catching light
                `inset 0 1px 1px ${t.rimHi}`,
                // LAW 1: Bottom form shadow
                `inset 0 -4px 7px ${t.rimLo}`,
                // LAW 3, tier 1: Contact shadow (tight, dark, grounding)
                `0 ${lerp(2, 1, sim.pressAmount).toFixed(2)}px ${lerp(4, 2, sim.pressAmount).toFixed(2)}px ${t.contact}`,
                // LAW 3, tier 2: Cast shadow with LAW 5 negative spread
                `0 ${lerp(12, 6, sim.pressAmount).toFixed(2)}px ${lerp(18, 10, sim.pressAmount).toFixed(2)}px -4px ${t.cast}`,
            ].join(', '),
            pointerEvents: 'none' as const,
            overflow: 'hidden',
        },

        // ─── Knob Inner (Specular Polish Layer) ──────────────────
        knobInner: {
            position: 'absolute',
            inset: 3,
            borderRadius: '50%',
            background: [
                // Tight specular near key light
                `radial-gradient(68% 68% at ${hotspotX} ${hotspotY}, ${t.spec} 0%, transparent 28%)`,
                // Lower edge darkening
                `linear-gradient(180deg, transparent 0%, transparent 62%, ${dark ? 'rgba(0,0,0,0.16)' : 'rgba(0,0,0,0.06)'} 100%)`,
            ].join(', '),
            boxShadow: `inset 0 1px 0 ${t.rimHiSoft}`,
            pointerEvents: 'none' as const,
        },
    };
}

// ─── Raised Button CSS Compiler ──────────────────────────────────

export type ButtonCssParts = {
    root: React.CSSProperties;
    surface: React.CSSProperties;
    label: React.CSSProperties;
};

export function compileRaisedButtonCss(params: {
    theme: ThemeMode;
    hoverAmount: number;
    pressAmount: number;
    tiltX: number;
    tiltY: number;
    hotspotX: number;
    hotspotY: number;
    width?: number;
    height?: number;
    radius?: number;
}): ButtonCssParts {
    const { theme, hoverAmount, pressAmount, tiltX, tiltY, hotspotX, hotspotY } = params;
    const t = getSkeuTokens(theme);
    const dark = theme === 'dark';
    const width = params.width ?? 180;
    const height = params.height ?? 48;
    const radius = params.radius ?? 12;

    const hpX = `${(hotspotX * 100).toFixed(1)}%`;
    const hpY = `${(hotspotY * 100).toFixed(1)}%`;
    const hoverLift = lerp(0, 3, hoverAmount);
    const pressDepth = lerp(0, 2, pressAmount);
    const rotX = (-tiltX * 2.5).toFixed(2);
    const rotY = (tiltY * 3).toFixed(2);

    return {
        root: {
            position: 'relative',
            width,
            height,
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            borderRadius: radius,
            background: 'transparent',
            transformStyle: 'preserve-3d',
            transform: `perspective(800px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(${-hoverLift + pressDepth}px)`,
            transition: 'transform 40ms linear',
            userSelect: 'none' as const,
            WebkitTapHighlightColor: 'transparent',
        },

        surface: {
            position: 'absolute',
            inset: 0,
            borderRadius: radius,
            // Convex surface gradient
            background: [
                `radial-gradient(100% 100% at ${hpX} ${hpY}, ${t.spec} 0%, transparent 30%)`,
                `linear-gradient(180deg, ${dark ? '#2a2e3a' : '#ffffff'} 0%, ${dark ? '#1a1e28' : '#e8ecf2'} 100%)`,
            ].join(', '),
            boxShadow: [
                // Top rim highlight
                `inset 0 1px 1px ${t.rimHi}`,
                // Bottom compression
                `inset 0 -2px 4px ${t.rimLo}`,
                // Contact shadow
                `0 ${lerp(1, 0.5, pressAmount).toFixed(1)}px ${lerp(2, 1, pressAmount).toFixed(1)}px ${t.contact}`,
                // Cast shadow
                `0 ${lerp(6, 2, pressAmount).toFixed(1)}px ${lerp(12, 4, pressAmount).toFixed(1)}px -3px ${t.cast}`,
                // Outer bottom bevel
                `0 1px 0 ${t.border}`,
            ].join(', '),
        },

        label: {
            position: 'relative',
            zIndex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            height: '100%',
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            fontSize: 14,
            fontWeight: 600,
            letterSpacing: '0.02em',
            color: dark ? 'rgba(255,255,255,0.88)' : 'rgba(0,0,0,0.82)',
            textShadow: dark
                ? '0 1px 2px rgba(0,0,0,0.4)'
                : '0 1px 0 rgba(255,255,255,0.6)',
            transform: `translateY(${pressDepth * 0.5}px)`,
            transition: 'transform 40ms linear',
        },
    };
}

// ─── Inset Panel CSS Compiler ────────────────────────────────────

export function compileInsetPanelCss(params: {
    theme: ThemeMode;
    radius?: number;
}): React.CSSProperties {
    const { theme } = params;
    const t = getSkeuTokens(theme);
    const dark = theme === 'dark';
    const radius = params.radius ?? 16;

    return {
        position: 'relative',
        borderRadius: radius,
        background: `linear-gradient(180deg, ${dark ? '#0c0f16' : '#d4dce6'} 0%, ${dark ? '#141820' : '#e8eef6'} 100%)`,
        boxShadow: [
            // Inner cavity
            `inset 0 2px 4px ${t.cavity}`,
            `inset 0 8px 16px ${t.cavityDeep}`,
            // Top micro-bevel
            `inset 0 1px 0 ${t.rimHi}`,
            // Bottom inner lip catching light
            `inset 0 -1px 2px ${t.rimHiSoft}`,
            // Outer grounding
            `0 1px 0 ${t.border}`,
        ].join(', '),
        border: `1px solid ${dark ? 'rgba(0,0,0,0.4)' : 'rgba(0,0,0,0.08)'}`,
    };
}
