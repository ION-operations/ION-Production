import React from 'react';

// ═══════════════════════════════════════════════════════════════════
// SPARKLINE — Inline SVG micro-chart for trend visualization
// Renders a polyline from a data array, sized to fit any container
// ═══════════════════════════════════════════════════════════════════

interface SparklineProps {
    data: number[];
    width?: number;
    height?: number;
    color?: string;
    fillOpacity?: number;
    strokeWidth?: number;
    className?: string;
}

export function Sparkline({
    data,
    width = 60,
    height = 20,
    color = 'var(--status-live)',
    fillOpacity = 0.1,
    strokeWidth = 1.2,
    className,
}: SparklineProps) {
    if (data.length < 2) return null;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const padding = 1;

    const points = data.map((v, i) => {
        const x = padding + (i / (data.length - 1)) * (width - padding * 2);
        const y = height - padding - ((v - min) / range) * (height - padding * 2);
        return `${x},${y}`;
    });

    const polyline = points.join(' ');
    const fillPath = `M${padding},${height} ${points.join(' ')} ${width - padding},${height} Z`;

    return (
        <svg
            width={width}
            height={height}
            viewBox={`0 0 ${width} ${height}`}
            className={className}
            style={{ flexShrink: 0, overflow: 'visible' }}
        >
            {/* Fill area */}
            <path d={fillPath} fill={color} opacity={fillOpacity} />
            {/* Stroke line */}
            <polyline
                points={polyline}
                fill="none"
                stroke={color}
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            {/* Current value dot */}
            <circle
                cx={parseFloat(points[points.length - 1].split(',')[0])}
                cy={parseFloat(points[points.length - 1].split(',')[1])}
                r={2}
                fill={color}
            />
        </svg>
    );
}


// ─── Ring Gauge — Small circular progress ─────────────────────

interface RingGaugeProps {
    value: number; // 0-100
    size?: number;
    strokeWidth?: number;
    color?: string;
    bgColor?: string;
    label?: string;
}

export function RingGauge({
    value,
    size = 28,
    strokeWidth = 2.5,
    color = 'var(--status-live)',
    bgColor = 'var(--surface-3)',
    label,
}: RingGaugeProps) {
    const r = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * r;
    const offset = circumference - (value / 100) * circumference;

    return (
        <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                {/* Background ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={r}
                    fill="none"
                    stroke={bgColor}
                    strokeWidth={strokeWidth}
                />
                {/* Value ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={r}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    transform={`rotate(-90 ${size / 2} ${size / 2})`}
                    style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
                />
            </svg>
            {label && (
                <div style={{
                    position: 'absolute',
                    inset: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'var(--font-mono)',
                    fontSize: size < 32 ? 8 : 10,
                    color: 'var(--text-secondary)',
                }}>
                    {label}
                </div>
            )}
        </div>
    );
}
