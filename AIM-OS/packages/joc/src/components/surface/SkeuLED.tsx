// SkeuLED.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic LED — Status indicator with physical depth.
//
// A recessed housing (machined cavity) containing a colored LED
// element with glow, pulse animation, and ring indicators.
// ═══════════════════════════════════════════════════════════════════

import React from 'react';

interface SkeuLEDProps {
    /** LED color */
    color?: string;
    /** Whether LED is active (glowing) */
    active?: boolean;
    /** Size in px */
    size?: number;
    /** Pulse animation (for active state) */
    pulse?: boolean;
    /** Label text next to LED */
    label?: string;
    /** Label position */
    labelPosition?: 'right' | 'bottom';
    className?: string;
    style?: React.CSSProperties;
}

// Status color presets
export const LED_COLORS = {
    online: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    accent: '#a855f7',
    cyan: '#00ffff',
    idle: '#555',
} as const;

export function SkeuLED({
    color = LED_COLORS.online,
    active = true,
    size = 8,
    pulse = false,
    label,
    labelPosition = 'right',
    className = '',
    style,
}: SkeuLEDProps) {
    const effectiveColor = active ? color : '#333';
    const housingSize = size + 6;

    const led = (
        <div
            className={`skeu-led ${active ? 'skeu-led--active' : ''} ${className}`}
            style={{
                position: 'relative',
                width: housingSize,
                height: housingSize,
                flexShrink: 0,
                ...style,
            }}
        >
            {/* Recessed housing (machined well) */}
            <div style={{
                position: 'absolute',
                inset: 0,
                borderRadius: '50%',
                background: 'linear-gradient(180deg, #0a0c10 0%, #1a1e28 100%)',
                boxShadow: [
                    'inset 0 1px 2px rgba(0,0,0,0.7)',
                    'inset 0 -1px 0 rgba(255,255,255,0.05)',
                    '0 1px 0 rgba(255,255,255,0.04)',
                ].join(', '),
            }} />

            {/* LED element */}
            <div style={{
                position: 'absolute',
                top: 3,
                left: 3,
                width: size,
                height: size,
                borderRadius: '50%',
                background: `radial-gradient(circle at 35% 30%, ${active ? lighten(effectiveColor, 40) : '#444'} 0%, ${effectiveColor} 60%, ${active ? darken(effectiveColor, 30) : '#222'} 100%)`,
                boxShadow: active
                    ? [
                        `0 0 ${size}px ${effectiveColor}`,
                        `0 0 ${size * 2.5}px rgba(${hexToRgb(effectiveColor)}, 0.3)`,
                    ].join(', ')
                    : 'none',
                animation: pulse && active ? 'skeuLedPulse 2s ease-in-out infinite' : undefined,
            }} />
        </div>
    );

    if (!label) return led;

    return (
        <div style={{
            display: 'flex',
            flexDirection: labelPosition === 'bottom' ? 'column' : 'row',
            alignItems: 'center',
            gap: labelPosition === 'bottom' ? 4 : 6,
        }}>
            {led}
            <span style={{
                fontSize: 10,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 500,
                color: active ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.3)',
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
                whiteSpace: 'nowrap',
            }}>
                {label}
            </span>
        </div>
    );
}

// ─── Color Utilities ─────────────────────────────────────────────

function hexToRgb(hex: string): string {
    const h = hex.replace('#', '');
    if (h.length !== 6) return '255,255,255';
    const r = parseInt(h.substring(0, 2), 16);
    const g = parseInt(h.substring(2, 4), 16);
    const b = parseInt(h.substring(4, 6), 16);
    return `${r},${g},${b}`;
}

function lighten(hex: string, pct: number): string {
    const h = hex.replace('#', '');
    if (h.length !== 6) return hex;
    const r = Math.min(255, parseInt(h.substring(0, 2), 16) + pct);
    const g = Math.min(255, parseInt(h.substring(2, 4), 16) + pct);
    const b = Math.min(255, parseInt(h.substring(4, 6), 16) + pct);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

function darken(hex: string, pct: number): string {
    const h = hex.replace('#', '');
    if (h.length !== 6) return hex;
    const r = Math.max(0, parseInt(h.substring(0, 2), 16) - pct);
    const g = Math.max(0, parseInt(h.substring(2, 4), 16) - pct);
    const b = Math.max(0, parseInt(h.substring(4, 6), 16) - pct);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
