// SkeuHealthBar.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic Health Bar — VU-meter style segmented indicator.
//
// Not a flat CSS fill bar. Each segment is an individually-lit LED
// element inside a machined track, like a professional audio VU meter.
// ═══════════════════════════════════════════════════════════════════

import React from 'react';

interface SkeuHealthBarProps {
    /** Value 0–1 */
    value: number;
    /** Number of segments */
    segments?: number;
    /** Width in px */
    width?: number;
    /** Height in px */
    height?: number;
    /** Color scheme: green→amber→red thresholds */
    thresholds?: { green: number; amber: number; red: number };
    /** Label text */
    label?: string;
    /** Show percentage text */
    showValue?: boolean;
    /** Orientation */
    direction?: 'horizontal' | 'vertical';
    className?: string;
    style?: React.CSSProperties;
}

const DEFAULT_THRESHOLDS = { green: 0.6, amber: 0.8, red: 0.95 };

export function SkeuHealthBar({
    value,
    segments = 12,
    width = 120,
    height = 14,
    thresholds = DEFAULT_THRESHOLDS,
    label,
    showValue = false,
    direction = 'horizontal',
    className = '',
    style,
}: SkeuHealthBarProps) {
    const clampedValue = Math.max(0, Math.min(1, value));
    const litSegments = Math.round(clampedValue * segments);
    const isVertical = direction === 'vertical';

    const getSegmentColor = (index: number): string => {
        const pos = index / segments;
        if (pos >= thresholds.red) return '#ef4444';
        if (pos >= thresholds.amber) return '#f59e0b';
        return '#22c55e';
    };

    const segmentGap = 2;
    const trackPad = 3;
    const segmentWidth = isVertical
        ? width - trackPad * 2
        : (width - trackPad * 2 - (segments - 1) * segmentGap) / segments;
    const segmentHeight = isVertical
        ? (height - trackPad * 2 - (segments - 1) * segmentGap) / segments
        : height - trackPad * 2;

    return (
        <div
            className={`skeu-health-bar ${className}`}
            style={{
                display: 'inline-flex',
                flexDirection: isVertical ? 'column' : 'row',
                alignItems: 'center',
                gap: 8,
                ...style,
            }}
        >
            {label && (
                <span style={{
                    fontSize: 9,
                    fontFamily: "'Inter', sans-serif",
                    fontWeight: 600,
                    color: 'rgba(255,255,255,0.45)',
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    minWidth: isVertical ? undefined : 44,
                }}>
                    {label}
                </span>
            )}

            {/* Track housing (machined cavity) */}
            <div style={{
                position: 'relative',
                width: isVertical ? width : width,
                height: isVertical ? height : height,
                borderRadius: 4,
                // Recessed track
                background: 'linear-gradient(180deg, #0a0c12 0%, #12151d 100%)',
                boxShadow: [
                    'inset 0 1px 3px rgba(0,0,0,0.6)',
                    'inset 0 -1px 0 rgba(255,255,255,0.04)',
                    '0 1px 0 rgba(255,255,255,0.03)',
                ].join(', '),
                border: '1px solid rgba(0,0,0,0.5)',
                padding: trackPad,
                display: 'flex',
                flexDirection: isVertical ? 'column-reverse' : 'row',
                gap: segmentGap,
                alignItems: 'stretch',
            }}>
                {Array.from({ length: segments }, (_, i) => {
                    const isLit = i < litSegments;
                    const segColor = getSegmentColor(i);

                    return (
                        <div
                            key={i}
                            style={{
                                width: isVertical ? undefined : segmentWidth,
                                height: isVertical ? segmentHeight : undefined,
                                flex: isVertical ? undefined : undefined,
                                borderRadius: 2,
                                background: isLit
                                    ? `linear-gradient(180deg, ${lightenColor(segColor, 20)} 0%, ${segColor} 50%, ${darkenColor(segColor, 30)} 100%)`
                                    : 'rgba(255,255,255,0.03)',
                                boxShadow: isLit
                                    ? `0 0 4px ${segColor}, inset 0 1px 0 rgba(255,255,255,0.15)`
                                    : 'inset 0 1px 1px rgba(0,0,0,0.3)',
                                transition: 'all 80ms ease-out',
                            }}
                        />
                    );
                })}
            </div>

            {showValue && (
                <span style={{
                    fontSize: 10,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontWeight: 600,
                    color: 'rgba(255,255,255,0.6)',
                    minWidth: 32,
                    textAlign: 'right',
                }}>
                    {Math.round(clampedValue * 100)}%
                </span>
            )}
        </div>
    );
}

// ─── Utilities ───────────────────────────────────────────────────

function lightenColor(hex: string, amount: number): string {
    const h = hex.replace('#', '');
    const r = Math.min(255, parseInt(h.substring(0, 2), 16) + amount);
    const g = Math.min(255, parseInt(h.substring(2, 4), 16) + amount);
    const b = Math.min(255, parseInt(h.substring(4, 6), 16) + amount);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

function darkenColor(hex: string, amount: number): string {
    const h = hex.replace('#', '');
    const r = Math.max(0, parseInt(h.substring(0, 2), 16) - amount);
    const g = Math.max(0, parseInt(h.substring(2, 4), 16) - amount);
    const b = Math.max(0, parseInt(h.substring(4, 6), 16) - amount);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
