// SkeuPanel.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic Panel — The foundational container for all JOC content.
//
// Two variants:
//   raised  — elevated chrome-bezeled card (like a hardware module faceplate)
//   inset   — recessed cavity (like a machined well in a camera body)
//
// Both enforce all 5 Laws. Both support material presets.
// ═══════════════════════════════════════════════════════════════════

import React, { useState, useRef } from 'react';
import { getMaterial, compileMaterialSurface, type MaterialPreset } from '../../engine/surface-engine-materials';

export type PanelVariant = 'raised' | 'inset';

interface SkeuPanelProps {
    variant?: PanelVariant;
    material?: string; // preset key from MATERIAL_PRESETS
    children?: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
    /** Padding in px */
    padding?: number;
    /** Border radius in px */
    radius?: number;
    /** Enable glass overlay on raised panels */
    glassOverlay?: boolean;
    /** Chrome bezel thickness (0 = none) */
    bezel?: number;
    /** Header slot */
    header?: React.ReactNode;
    /** Glow color override for active state */
    glowColor?: string;
    /** Whether this panel is in active state */
    active?: boolean;
    onClick?: () => void;
}

export function SkeuPanel({
    variant = 'raised',
    material = 'ceramic.gloss',
    children,
    className = '',
    style,
    padding = 16,
    radius = 12,
    glassOverlay = true,
    bezel = 1,
    header,
    glowColor,
    active = false,
    onClick,
}: SkeuPanelProps) {
    const [hovered, setHovered] = useState(false);
    const ref = useRef<HTMLDivElement>(null);
    const mat = getMaterial(material);

    // Override glow if provided
    const effectiveMat: MaterialPreset = glowColor
        ? { ...mat, glowColor }
        : mat;

    if (variant === 'inset') {
        return (
            <div
                ref={ref}
                className={`skeu-panel skeu-panel--inset ${className}`}
                style={{
                    position: 'relative',
                    borderRadius: radius,
                    padding,
                    // LAW 2: Volume gradient (concave)
                    background: `linear-gradient(180deg, #0c0f16 0%, #141820 100%)`,
                    // LAW 3 + 4: Cavity shadows + micro-bevel
                    boxShadow: [
                        `inset 0 2px 6px rgba(0,0,0,${(0.4 * mat.cavityDepth).toFixed(2)})`,
                        `inset 0 8px 20px rgba(0,0,0,${(0.3 * mat.cavityDepth).toFixed(2)})`,
                        `inset 0 1px 0 rgba(255,255,255,0.06)`,
                        `inset 0 -1px 2px rgba(255,255,255,0.03)`,
                        `0 1px 0 rgba(255,255,255,0.03)`,
                    ].join(', '),
                    border: '1px solid rgba(0,0,0,0.4)',
                    ...style,
                }}
                onClick={onClick}
            >
                {header && (
                    <div style={{
                        marginBottom: 12,
                        paddingBottom: 10,
                        borderBottom: '1px solid rgba(255,255,255,0.04)',
                    }}>
                        {header}
                    </div>
                )}
                {children}
            </div>
        );
    }

    // ─── Raised variant ──────────────────────────────────────────
    const matStyles = compileMaterialSurface(effectiveMat, {
        hovered,
        active,
    });

    return (
        <div
            ref={ref}
            className={`skeu-panel skeu-panel--raised ${className}`}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            onClick={onClick}
            style={{
                position: 'relative',
                borderRadius: radius,
                overflow: 'hidden',
                cursor: onClick ? 'pointer' : undefined,
                ...matStyles,
                ...style,
            }}
        >
            {/* Chrome bezel frame */}
            {bezel > 0 && (
                <div style={{
                    position: 'absolute',
                    inset: 0,
                    borderRadius: radius,
                    border: `${bezel}px solid rgba(255,255,255,0.06)`,
                    pointerEvents: 'none',
                }} />
            )}

            {/* Glass overlay (LAW 2: convex curvature hint) */}
            {glassOverlay && (
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '50%',
                    borderRadius: `${radius}px ${radius}px 0 0`,
                    background: 'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%)',
                    pointerEvents: 'none',
                }} />
            )}

            {/* Content */}
            <div style={{ position: 'relative', zIndex: 1, padding }}>
                {header && (
                    <div style={{
                        marginBottom: 12,
                        paddingBottom: 10,
                        borderBottom: '1px solid rgba(255,255,255,0.06)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}>
                        {header}
                    </div>
                )}
                {children}
            </div>
        </div>
    );
}
