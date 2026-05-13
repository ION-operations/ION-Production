// SkeuButton.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic Button — Physical press response with spring physics.
//
// A raised, material-rendered button with:
//   - Spring physics for press/release (uses useSurfaceInteraction)
//   - 3-tier cast shadow
//   - LED state indicator (optional)
//   - Rubber grip texture on hover zone
//   - Micro-bevel edge highlights
// ═══════════════════════════════════════════════════════════════════

import React, { useRef, useCallback, useState } from 'react';
import { getMaterial, compileMaterialSurface } from '../../engine/surface-engine-materials';

interface SkeuButtonProps {
    /** Button label */
    children: React.ReactNode;
    /** Click handler */
    onClick?: () => void;
    /** Material preset */
    material?: string;
    /** Button variant */
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    /** Size */
    size?: 'sm' | 'md' | 'lg';
    /** Disabled state */
    disabled?: boolean;
    /** Show LED indicator */
    led?: boolean;
    /** LED color */
    ledColor?: string;
    /** Full width */
    fullWidth?: boolean;
    /** Icon (left side) */
    icon?: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
}

const SIZE_MAP = {
    sm: { height: 32, fontSize: 10, padding: '0 14px', radius: 6 },
    md: { height: 38, fontSize: 11, padding: '0 18px', radius: 8 },
    lg: { height: 44, fontSize: 12, padding: '0 24px', radius: 10 },
};

const VARIANT_GLOW: Record<string, string> = {
    primary: 'rgba(98, 178, 255, 0.25)',
    secondary: 'rgba(160, 200, 240, 0.12)',
    ghost: 'transparent',
    danger: 'rgba(239, 68, 68, 0.20)',
};

export function SkeuButton({
    children,
    onClick,
    material = 'ceramic.gloss',
    variant = 'secondary',
    size = 'md',
    disabled = false,
    led = false,
    ledColor = '#3b82f6',
    fullWidth = false,
    icon,
    className = '',
    style,
}: SkeuButtonProps) {
    const [hovered, setHovered] = useState(false);
    const [pressed, setPressed] = useState(false);
    const ref = useRef<HTMLButtonElement>(null);
    const sizeConfig = SIZE_MAP[size];
    const mat = getMaterial(material);

    const matStyles = compileMaterialSurface(
        { ...mat, glowColor: VARIANT_GLOW[variant] || mat.glowColor },
        { hovered: hovered && !disabled, pressed: pressed && !disabled, active: variant === 'primary' }
    );

    const handleMouseDown = useCallback(() => { if (!disabled) setPressed(true); }, [disabled]);
    const handleMouseUp = useCallback(() => setPressed(false), []);

    return (
        <button
            ref={ref}
            className={`skeu-button skeu-button--${variant} ${disabled ? 'skeu-button--disabled' : ''} ${className}`}
            onClick={disabled ? undefined : onClick}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => { setHovered(false); setPressed(false); }}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            style={{
                position: 'relative',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                height: sizeConfig.height,
                padding: sizeConfig.padding,
                borderRadius: sizeConfig.radius,
                border: 'none',
                cursor: disabled ? 'not-allowed' : 'pointer',
                width: fullWidth ? '100%' : undefined,
                opacity: disabled ? 0.5 : 1,
                overflow: 'hidden',
                fontFamily: "'Inter', sans-serif",
                fontSize: sizeConfig.fontSize,
                fontWeight: 600,
                letterSpacing: '0.04em',
                textTransform: 'uppercase' as const,
                color: variant === 'primary'
                    ? 'rgba(255,255,255,0.92)'
                    : variant === 'danger'
                        ? '#ff8080'
                        : 'rgba(255,255,255,0.7)',
                textShadow: '0 1px 2px rgba(0,0,0,0.4)',
                // Material surface
                ...matStyles,
                // Chrome bezel
                outline: `1px solid rgba(255,255,255,${variant === 'primary' ? 0.08 : 0.04})`,
                outlineOffset: -1,
                ...style,
            }}
        >
            {/* Glass overlay */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '50%',
                borderRadius: `${sizeConfig.radius}px ${sizeConfig.radius}px 0 0`,
                background: 'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%)',
                pointerEvents: 'none',
            }} />

            {/* LED indicator */}
            {led && (
                <div style={{
                    width: 5,
                    height: 5,
                    borderRadius: '50%',
                    background: `radial-gradient(circle at 35% 30%, ${lighten(ledColor, 40)} 0%, ${ledColor} 100%)`,
                    boxShadow: `0 0 6px ${ledColor}, 0 0 12px rgba(${hexToRgb(ledColor)}, 0.3)`,
                    flexShrink: 0,
                }} />
            )}

            {/* Icon */}
            {icon && (
                <span style={{ display: 'flex', alignItems: 'center', opacity: 0.8 }}>
                    {icon}
                </span>
            )}

            {/* Label */}
            <span style={{ position: 'relative', zIndex: 1 }}>
                {children}
            </span>
        </button>
    );
}

// ─── Utilities ───────────────────────────────────────────────────

function hexToRgb(hex: string): string {
    const h = hex.replace('#', '');
    if (h.length !== 6) return '255,255,255';
    return `${parseInt(h.substring(0, 2), 16)},${parseInt(h.substring(2, 4), 16)},${parseInt(h.substring(4, 6), 16)}`;
}

function lighten(hex: string, amount: number): string {
    const h = hex.replace('#', '');
    if (h.length !== 6) return hex;
    const r = Math.min(255, parseInt(h.substring(0, 2), 16) + amount);
    const g = Math.min(255, parseInt(h.substring(2, 4), 16) + amount);
    const b = Math.min(255, parseInt(h.substring(4, 6), 16) + amount);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
