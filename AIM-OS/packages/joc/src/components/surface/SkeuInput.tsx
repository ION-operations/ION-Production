// SkeuInput.tsx
// ═══════════════════════════════════════════════════════════════════
// Skeuomorphic Input — Recessed glass input field.
//
// A machined cavity input with:
//   - Chrome trim surrounding a recessed well
//   - Glass lens overlay
//   - Focus state with glow
//   - Micro-bevel edge highlighting (LAW 4)
// ═══════════════════════════════════════════════════════════════════

import React, { useState, useRef } from 'react';

interface SkeuInputProps {
    /** Input value */
    value?: string;
    /** Change handler */
    onChange?: (value: string) => void;
    /** Placeholder text */
    placeholder?: string;
    /** Left icon */
    icon?: React.ReactNode;
    /** Glow color on focus */
    focusGlow?: string;
    /** Full width */
    fullWidth?: boolean;
    /** Height */
    height?: number;
    /** Border radius */
    radius?: number;
    /** Input type */
    type?: string;
    /** Disabled */
    disabled?: boolean;
    /** On key down handler */
    onKeyDown?: (e: React.KeyboardEvent) => void;
    className?: string;
    style?: React.CSSProperties;
}

export function SkeuInput({
    value,
    onChange,
    placeholder = '',
    icon,
    focusGlow = 'rgba(98, 178, 255, 0.25)',
    fullWidth = true,
    height = 38,
    radius = 8,
    type = 'text',
    disabled = false,
    onKeyDown,
    className = '',
    style,
}: SkeuInputProps) {
    const [focused, setFocused] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    return (
        <div
            className={`skeu-input ${focused ? 'skeu-input--focused' : ''} ${className}`}
            onClick={() => inputRef.current?.focus()}
            style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                height,
                width: fullWidth ? '100%' : undefined,
                borderRadius: radius,
                cursor: disabled ? 'not-allowed' : 'text',
                opacity: disabled ? 0.5 : 1,

                // Recessed cavity
                background: 'linear-gradient(180deg, #0a0d14 0%, #10141c 100%)',
                boxShadow: [
                    // Cavity shadows (LAW 3)
                    'inset 0 2px 6px rgba(0,0,0,0.5)',
                    'inset 0 6px 16px rgba(0,0,0,0.25)',
                    // Top micro-bevel (LAW 4)
                    'inset 0 1px 0 rgba(255,255,255,0.04)',
                    // Bottom inner lip
                    'inset 0 -1px 2px rgba(255,255,255,0.02)',
                    // Outer grounding shadow
                    '0 1px 0 rgba(255,255,255,0.03)',
                    // Focus glow
                    focused ? `0 0 0 2px ${focusGlow}` : '',
                    focused ? `0 0 16px -4px ${focusGlow}` : '',
                ].filter(Boolean).join(', '),
                border: `1px solid ${focused ? 'rgba(98, 178, 255, 0.2)' : 'rgba(0,0,0,0.4)'}`,
                transition: 'all 150ms cubic-bezier(0.22, 1, 0.36, 1)',
                ...style,
            }}
        >
            {/* Icon */}
            {icon && (
                <span style={{
                    display: 'flex',
                    alignItems: 'center',
                    paddingLeft: 12,
                    color: focused ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.25)',
                    transition: 'color 150ms ease',
                    flexShrink: 0,
                }}>
                    {icon}
                </span>
            )}

            {/* Input */}
            <input
                ref={inputRef}
                type={type}
                value={value}
                onChange={e => onChange?.(e.target.value)}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                onKeyDown={onKeyDown}
                placeholder={placeholder}
                disabled={disabled}
                style={{
                    width: '100%',
                    height: '100%',
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    padding: `0 ${icon ? 10 : 14}px`,
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 12,
                    fontWeight: 400,
                    color: 'rgba(255,255,255,0.85)',
                    letterSpacing: '0.01em',
                    // Phosphor text shadow on content
                    textShadow: focused ? '0 0 4px rgba(98, 178, 255, 0.15)' : 'none',
                    caretColor: 'rgba(98, 178, 255, 0.7)',
                }}
            />

            {/* Glass reflection */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '40%',
                borderRadius: `${radius}px ${radius}px 0 0`,
                background: 'linear-gradient(180deg, rgba(255,255,255,0.02) 0%, transparent 100%)',
                pointerEvents: 'none',
            }} />
        </div>
    );
}
