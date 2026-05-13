// surface-engine-motion.ts
// ═══════════════════════════════════════════════════════════════════
// Hooke's Law spring simulation + high-fidelity pointer tracking.
// Every Surface Engine control gets physically weighted interaction:
//   - hover lift with tilt
//   - press depression with shadow compression
//   - toggle travel with overshoot
//   - pointer-reactive hotspot chasing
//   - caustic energy decay
//   - reduced-motion awareness
// ═══════════════════════════════════════════════════════════════════

import { useEffect, useMemo, useRef, useState } from 'react';
import { clamp01, lerp } from './surface-engine-core';

// ─── Simulation State ────────────────────────────────────────────

export type SurfaceSimState = {
    hoverAmount: number;      // 0..1 — hover lift
    pressAmount: number;      // 0..1 — press depression
    toggleTravel: number;     // 0..1 — toggle knob position
    tiltX: number;            // perspective tilt X
    tiltY: number;            // perspective tilt Y
    hotspotX: number;         // 0..1 — specular hotspot X
    hotspotY: number;         // 0..1 — specular hotspot Y
    causticEnergy: number;    // 0..1 — caustic bloom intensity
    velocity: number;         // current travel velocity (for stretch)
};

// ─── Spring Physics ──────────────────────────────────────────────

type SpringState = { x: number; v: number };

function stepSpring(
    state: SpringState,
    target: number,
    stiffness: number,
    damping: number,
    dt: number,
): SpringState {
    // F = -k(x - target) - c*v
    const force = stiffness * (target - state.x) - damping * state.v;
    const v = state.v + force * dt;
    const x = state.x + v * dt;
    return { x, v };
}

function isSettled(state: SpringState, target: number): boolean {
    return (
        Math.abs(state.v) < 0.0005 &&
        Math.abs(state.x - target) < 0.0005
    );
}

// ─── The Hook ────────────────────────────────────────────────────

export interface SurfaceInteractionConfig {
    /** Spring stiffness for hover/press (default 420) */
    stiffness?: number;
    /** Damping for hover/press (default 28) */
    damping?: number;
    /** Toggle spring stiffness (default 360) */
    toggleStiffness?: number;
    /** Toggle damping (default 26) */
    toggleDamping?: number;
}

export function useSurfaceInteraction(
    checked: boolean,
    config?: SurfaceInteractionConfig,
) {
    const stiffness = config?.stiffness ?? 420;
    const damping = config?.damping ?? 28;
    const toggleStiffness = config?.toggleStiffness ?? 360;
    const toggleDamping = config?.toggleDamping ?? 26;

    const [sim, setSim] = useState<SurfaceSimState>({
        hoverAmount: 0,
        pressAmount: 0,
        toggleTravel: checked ? 1 : 0,
        tiltX: 0,
        tiltY: 0,
        hotspotX: checked ? 0.72 : 0.28,
        hotspotY: 0.35,
        causticEnergy: checked ? 0.6 : 0.2,
        velocity: 0,
    });

    // Spring state refs (not in React state — updated per-frame)
    const springs = useRef({
        hover: { x: 0, v: 0 } as SpringState,
        press: { x: 0, v: 0 } as SpringState,
        travel: { x: checked ? 1 : 0, v: 0 } as SpringState,
        tiltX: { x: 0, v: 0 } as SpringState,
        tiltY: { x: 0, v: 0 } as SpringState,
        hotspotX: { x: checked ? 0.72 : 0.28, v: 0 } as SpringState,
        hotspotY: { x: 0.35, v: 0 } as SpringState,
        caustic: { x: checked ? 0.6 : 0.2, v: 0 } as SpringState,
    });

    // Live pointer state (high frequency, never triggers render)
    const live = useRef({
        inside: false,
        down: false,
        pointerX: checked ? 0.72 : 0.28,
        pointerY: 0.35,
        pressure: 0,
        tiltX: 0,
        tiltY: 0,
    });

    // Reduced motion preference
    const reducedMotion = useRef(false);

    useEffect(() => {
        if (typeof window === 'undefined' || !window.matchMedia) return;
        const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
        const update = () => { reducedMotion.current = mq.matches; };
        update();
        mq.addEventListener?.('change', update);
        return () => mq.removeEventListener?.('change', update);
    }, []);

    // ─── Animation Loop ─────────────────────────────────────────

    useEffect(() => {
        let raf = 0;
        let prev = performance.now();

        const frame = (now: number) => {
            const dt = Math.min(0.032, (now - prev) / 1000); // cap at ~30fps min
            prev = now;

            const s = springs.current;
            const l = live.current;
            const reduced = reducedMotion.current;

            // Targets
            const hoverTarget = l.inside ? 1 : 0;
            const pressTarget = l.down ? 1 : 0;
            const travelTarget = checked ? 1 : 0;
            const hotspotXTarget = lerp(
                travelTarget ? 0.72 : 0.28,
                l.pointerX,
                l.inside ? 0.28 : 0,
            );
            const hotspotYTarget = lerp(0.32, l.pointerY, l.inside ? 0.35 : 0);
            const tiltXTarget = l.inside ? (l.pointerY - 0.5) * -2 : 0;
            const tiltYTarget = l.inside ? (l.pointerX - 0.5) * 2 : 0;
            const causticTarget =
                0.18 +
                0.42 * travelTarget +
                0.16 * hoverTarget +
                0.12 * pressTarget;

            // Reduced motion: stiffer springs, more damping
            const sf = reduced ? 0.52 : 1;
            const df = reduced ? 1.2 : 1;

            // Step all springs
            s.hover = stepSpring(s.hover, hoverTarget, stiffness * sf, damping * df, dt);
            s.press = stepSpring(s.press, pressTarget, stiffness * sf, damping * df, dt);
            s.travel = stepSpring(s.travel, travelTarget, toggleStiffness, toggleDamping, dt);
            s.tiltX = stepSpring(s.tiltX, tiltXTarget, 250 * sf, 24 * df, dt);
            s.tiltY = stepSpring(s.tiltY, tiltYTarget, 250 * sf, 24 * df, dt);
            s.hotspotX = stepSpring(s.hotspotX, hotspotXTarget, 320, 30, dt);
            s.hotspotY = stepSpring(s.hotspotY, hotspotYTarget, 320, 30, dt);
            s.caustic = stepSpring(s.caustic, causticTarget, 220, 26, dt);

            setSim({
                hoverAmount: clamp01(s.hover.x),
                pressAmount: clamp01(s.press.x),
                toggleTravel: clamp01(s.travel.x),
                tiltX: s.tiltX.x,
                tiltY: s.tiltY.x,
                hotspotX: clamp01(s.hotspotX.x),
                hotspotY: clamp01(s.hotspotY.x),
                causticEnergy: clamp01(s.caustic.x),
                velocity: s.travel.v,
            });

            raf = requestAnimationFrame(frame);
        };

        raf = requestAnimationFrame(frame);
        return () => cancelAnimationFrame(raf);
    }, [checked, stiffness, damping, toggleStiffness, toggleDamping]);

    // ─── Pointer Event Bindings ──────────────────────────────────

    const bind = useMemo(
        () => ({
            onPointerEnter: () => {
                live.current.inside = true;
            },

            onPointerLeave: () => {
                live.current.inside = false;
                live.current.down = false;
            },

            onPointerDown: (e: React.PointerEvent<HTMLElement>) => {
                live.current.down = true;
                try {
                    e.currentTarget.setPointerCapture?.(e.pointerId);
                } catch { /* */ }
            },

            onPointerUp: (e: React.PointerEvent<HTMLElement>) => {
                live.current.down = false;
                try {
                    e.currentTarget.releasePointerCapture?.(e.pointerId);
                } catch { /* */ }
            },

            onPointerMove: (e: React.PointerEvent<HTMLElement>) => {
                // Use coalesced events for maximum fidelity
                const native = e.nativeEvent;
                const samples =
                    typeof native.getCoalescedEvents === 'function'
                        ? native.getCoalescedEvents()
                        : [native];

                const last = samples[samples.length - 1] ?? native;
                const rect = e.currentTarget.getBoundingClientRect();
                const x = clamp01((last.clientX - rect.left) / rect.width);
                const y = clamp01((last.clientY - rect.top) / rect.height);

                live.current.pointerX = x;
                live.current.pointerY = y;
                live.current.pressure =
                    'pressure' in last ? (last as PointerEvent).pressure || 0 : 0;
                live.current.tiltX =
                    'tiltX' in last ? (last as PointerEvent).tiltX || 0 : 0;
                live.current.tiltY =
                    'tiltY' in last ? (last as PointerEvent).tiltY || 0 : 0;
            },
        }),
        [],
    );

    return { sim, bind };
}

// ─── Standalone Spring (for non-toggle controls) ────────────────

export function useSurfaceHover() {
    const [sim, setSim] = useState({
        hoverAmount: 0,
        pressAmount: 0,
        tiltX: 0,
        tiltY: 0,
        hotspotX: 0.5,
        hotspotY: 0.35,
    });

    const springs = useRef({
        hover: { x: 0, v: 0 } as SpringState,
        press: { x: 0, v: 0 } as SpringState,
        tiltX: { x: 0, v: 0 } as SpringState,
        tiltY: { x: 0, v: 0 } as SpringState,
        hotspotX: { x: 0.5, v: 0 } as SpringState,
        hotspotY: { x: 0.35, v: 0 } as SpringState,
    });

    const live = useRef({
        inside: false,
        down: false,
        pointerX: 0.5,
        pointerY: 0.35,
    });

    useEffect(() => {
        let raf = 0;
        let prev = performance.now();

        const frame = (now: number) => {
            const dt = Math.min(0.032, (now - prev) / 1000);
            prev = now;
            const s = springs.current;
            const l = live.current;

            s.hover = stepSpring(s.hover, l.inside ? 1 : 0, 400, 28, dt);
            s.press = stepSpring(s.press, l.down ? 1 : 0, 450, 30, dt);
            s.tiltX = stepSpring(s.tiltX, l.inside ? (l.pointerY - 0.5) * -1.5 : 0, 250, 24, dt);
            s.tiltY = stepSpring(s.tiltY, l.inside ? (l.pointerX - 0.5) * 1.5 : 0, 250, 24, dt);
            s.hotspotX = stepSpring(s.hotspotX, l.inside ? l.pointerX : 0.5, 300, 28, dt);
            s.hotspotY = stepSpring(s.hotspotY, l.inside ? l.pointerY : 0.35, 300, 28, dt);

            setSim({
                hoverAmount: clamp01(s.hover.x),
                pressAmount: clamp01(s.press.x),
                tiltX: s.tiltX.x,
                tiltY: s.tiltY.x,
                hotspotX: clamp01(s.hotspotX.x),
                hotspotY: clamp01(s.hotspotY.x),
            });

            raf = requestAnimationFrame(frame);
        };

        raf = requestAnimationFrame(frame);
        return () => cancelAnimationFrame(raf);
    }, []);

    const bind = useMemo(
        () => ({
            onPointerEnter: () => { live.current.inside = true; },
            onPointerLeave: () => { live.current.inside = false; live.current.down = false; },
            onPointerDown: () => { live.current.down = true; },
            onPointerUp: () => { live.current.down = false; },
            onPointerMove: (e: React.PointerEvent<HTMLElement>) => {
                const rect = e.currentTarget.getBoundingClientRect();
                live.current.pointerX = clamp01((e.clientX - rect.left) / rect.width);
                live.current.pointerY = clamp01((e.clientY - rect.top) / rect.height);
            },
        }),
        [],
    );

    return { sim, bind };
}
