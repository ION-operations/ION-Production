// SkeuCard.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic Card — Mission-control module card.
//
// A chrome-bezeled, glass-overlaid card with:
//   - Brushed metal title bar with LED status indicator
//   - Recessed content area
//   - 3-tier cast shadow
//   - Material presets
//
// This is the primary display unit for dashboard instruments.
// ═══════════════════════════════════════════════════════════════════

import React, { useState } from 'react';
import { getMaterial, compileMaterialSurface } from '../../engine/surface-engine-materials';
import { SkeuLED, LED_COLORS } from './SkeuLED';

export type CardStatus = 'online' | 'warning' | 'danger' | 'idle' | 'info';

interface SkeuCardProps {
    /** Card title (displayed in brushed metal header) */
    title: string;
    /** Icon element or emoji */
    icon?: React.ReactNode;
    /** Status LED in header */
    status?: CardStatus;
    /** Subtitle text (right side of header) */
    subtitle?: string;
    /** Material preset key */
    material?: string;
    /** Content */
    children?: React.ReactNode;
    /** Footer content */
    footer?: React.ReactNode;
    /** Border radius */
    radius?: number;
    /** Content padding */
    padding?: number;
    /** Make full width */
    fullWidth?: boolean;
    /** Click handler (makes card interactive) */
    onClick?: () => void;
    className?: string;
    style?: React.CSSProperties;
}

const STATUS_LED_MAP: Record<CardStatus, string> = {
    online: LED_COLORS.online,
    warning: LED_COLORS.warning,
    danger: LED_COLORS.danger,
    idle: LED_COLORS.idle,
    info: LED_COLORS.info,
};

export function SkeuCard({
    title,
    icon,
    status = 'online',
    subtitle,
    material = 'ceramic.gloss',
    children,
    footer,
    radius = 12,
    padding = 16,
    fullWidth = false,
    onClick,
    className = '',
    style,
}: SkeuCardProps) {
    const [hovered, setHovered] = useState(false);
    const mat = getMaterial(material);
    const matStyles = compileMaterialSurface(mat, { hovered });

    return (
        <div
            className={`skeu-card ${className}`}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            onClick={onClick}
            style={{
                position: 'relative',
                borderRadius: radius,
                overflow: 'hidden',
                width: fullWidth ? '100%' : undefined,
                cursor: onClick ? 'pointer' : undefined,
                ...matStyles,
                ...style,
            }}
        >
            {/* Chrome bezel */}
            <div style={{
                position: 'absolute',
                inset: 0,
                borderRadius: radius,
                border: '1px solid rgba(255,255,255,0.06)',
                pointerEvents: 'none',
                zIndex: 2,
            }} />

            {/* Glass overlay */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '45%',
                borderRadius: `${radius}px ${radius}px 0 0`,
                background: 'linear-gradient(180deg, rgba(255,255,255,0.035) 0%, transparent 100%)',
                pointerEvents: 'none',
                zIndex: 2,
            }} />

            {/* ─── Header (Brushed Metal Title Bar) ─── */}
            <div style={{
                position: 'relative',
                zIndex: 1,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: `10px ${padding}px`,
                // Brushed metal header gradient
                background: 'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%)',
                borderBottom: '1px solid rgba(0,0,0,0.3)',
                // Header bottom shadow
                boxShadow: '0 1px 0 rgba(255,255,255,0.03)',
            }}>
                {/* Status LED */}
                <SkeuLED
                    color={STATUS_LED_MAP[status]}
                    active={status !== 'idle'}
                    size={6}
                    pulse={status === 'online'}
                />

                {/* Icon */}
                {icon && (
                    <span style={{
                        fontSize: 14,
                        color: 'rgba(255,255,255,0.6)',
                        display: 'flex',
                        alignItems: 'center',
                    }}>
                        {icon}
                    </span>
                )}

                {/* Title */}
                <span style={{
                    fontSize: 11,
                    fontFamily: "'Inter', sans-serif",
                    fontWeight: 600,
                    color: 'rgba(255,255,255,0.75)',
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    flex: 1,
                }}>
                    {title}
                </span>

                {/* Subtitle */}
                {subtitle && (
                    <span style={{
                        fontSize: 10,
                        fontFamily: "'JetBrains Mono', monospace",
                        color: 'rgba(255,255,255,0.35)',
                        letterSpacing: '0.02em',
                    }}>
                        {subtitle}
                    </span>
                )}
            </div>

            {/* ─── Content Area (Recessed) ─── */}
            <div style={{
                position: 'relative',
                zIndex: 1,
                padding,
                // Subtle inset for content cavity
                background: 'linear-gradient(180deg, rgba(0,0,0,0.1) 0%, transparent 20%)',
            }}>
                {children}
            </div>

            {/* ─── Footer ─── */}
            {footer && (
                <div style={{
                    position: 'relative',
                    zIndex: 1,
                    padding: `8px ${padding}px`,
                    borderTop: '1px solid rgba(0,0,0,0.3)',
                    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.03)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }}>
                    {footer}
                </div>
            )}
        </div>
    );
}
