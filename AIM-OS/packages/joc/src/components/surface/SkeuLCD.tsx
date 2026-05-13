// SkeuLCD.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic LCD Display — Recessed screen with phosphor text.
//
// A machined cavity containing an LCD-style display with:
//   - Chrome frame
//   - Dark blue-green screen gradient
//   - Optional scanline overlay
//   - Monospace phosphor text (green/amber/cyan variants)
//   - Inner cavity shadows for depth
// ═══════════════════════════════════════════════════════════════════

import React from 'react';

type PhosphorColor = 'green' | 'amber' | 'cyan' | 'blue';

interface SkeuLCDProps {
    /** Content to display (can be text or React nodes) */
    children?: React.ReactNode;
    /** Phosphor color preset */
    phosphor?: PhosphorColor;
    /** Width */
    width?: number | string;
    /** Height */
    height?: number | string;
    /** Show scanlines */
    scanlines?: boolean;
    /** Show screen reflection */
    reflection?: boolean;
    /** Chrome frame thickness */
    frameWidth?: number;
    /** Font size for text content */
    fontSize?: number;
    /** Border radius */
    radius?: number;
    /** Optional title above screen */
    title?: string;
    className?: string;
    style?: React.CSSProperties;
}

const PHOSPHOR_COLORS: Record<PhosphorColor, { text: string; glow: string; bg: string }> = {
    green: { text: '#22c55e', glow: 'rgba(34, 197, 94, 0.15)', bg: '#0a1a0f' },
    amber: { text: '#f5a623', glow: 'rgba(245, 166, 35, 0.12)', bg: '#1a140a' },
    cyan: { text: '#00d4ff', glow: 'rgba(0, 212, 255, 0.15)', bg: '#0a141a' },
    blue: { text: '#4a90d9', glow: 'rgba(74, 144, 217, 0.12)', bg: '#0a1428' },
};

export function SkeuLCD({
    children,
    phosphor = 'cyan',
    width = '100%',
    height = 'auto',
    scanlines = true,
    reflection = true,
    frameWidth = 2,
    fontSize = 11,
    radius = 8,
    title,
    className = '',
    style,
}: SkeuLCDProps) {
    const colors = PHOSPHOR_COLORS[phosphor];

    return (
        <div
            className={`skeu-lcd ${className}`}
            style={{
                position: 'relative',
                width,
                ...style,
            }}
        >
            {/* Title label */}
            {title && (
                <div style={{
                    fontSize: 9,
                    fontFamily: "'Inter', sans-serif",
                    fontWeight: 600,
                    color: 'rgba(255,255,255,0.35)',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    marginBottom: 6,
                }}>
                    {title}
                </div>
            )}

            {/* Chrome frame */}
            <div style={{
                position: 'relative',
                borderRadius: radius,
                padding: frameWidth,
                // Brushed metal frame gradient
                background: 'linear-gradient(180deg, #3a3f4a 0%, #2a2e36 40%, #2a2e36 60%, #3a3f4a 100%)',
                boxShadow: [
                    '0 1px 3px rgba(0,0,0,0.4)',
                    '0 4px 12px -4px rgba(0,0,0,0.3)',
                    'inset 0 1px 0 rgba(255,255,255,0.08)',
                ].join(', '),
            }}>
                {/* Screen cavity */}
                <div style={{
                    position: 'relative',
                    borderRadius: radius - 1,
                    overflow: 'hidden',
                    height,
                    // LCD background gradient
                    background: `linear-gradient(180deg, ${colors.bg} 0%, ${darken(colors.bg)} 100%)`,
                    boxShadow: [
                        `inset 0 2px 6px rgba(0,0,0,0.6)`,
                        `inset 0 -1px 0 rgba(255,255,255,0.03)`,
                        `inset 0 0 20px ${colors.glow}`,
                    ].join(', '),
                }}>
                    {/* Scanline overlay */}
                    {scanlines && (
                        <div style={{
                            position: 'absolute',
                            inset: 0,
                            backgroundImage: `repeating-linear-gradient(0deg, transparent 0px, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px)`,
                            pointerEvents: 'none',
                            zIndex: 2,
                        }} />
                    )}

                    {/* Screen reflection (glass) */}
                    {reflection && (
                        <div style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            height: '40%',
                            borderRadius: `${radius - 1}px ${radius - 1}px 0 0`,
                            background: 'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%)',
                            pointerEvents: 'none',
                            zIndex: 3,
                        }} />
                    )}

                    {/* Content */}
                    <div style={{
                        position: 'relative',
                        zIndex: 1,
                        padding: '10px 12px',
                        fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
                        fontSize,
                        lineHeight: 1.5,
                        color: colors.text,
                        textShadow: `0 0 8px ${colors.glow}, 0 0 2px ${colors.text}`,
                        minHeight: typeof height === 'number' ? height - 20 : undefined,
                    }}>
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
}

// ─── Utility ─────────────────────────────────────────────────────

function darken(color: string): string {
    // Simple darken for bg colors
    return color.replace(/#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i, (_, r, g, b) => {
        const dr = Math.max(0, parseInt(r, 16) - 8).toString(16).padStart(2, '0');
        const dg = Math.max(0, parseInt(g, 16) - 8).toString(16).padStart(2, '0');
        const db = Math.max(0, parseInt(b, 16) - 8).toString(16).padStart(2, '0');
        return `#${dr}${dg}${db}`;
    });
}
