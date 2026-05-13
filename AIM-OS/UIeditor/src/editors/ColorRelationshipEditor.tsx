/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Color Relationship Editor
   Visual hue wheel showing all colors in the selected component.
   Drag one color → entire palette shifts proportionally.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useMemo, useCallback } from 'react';
import { useEditorStore } from '../store/editorStore';

type HarmonyMode = 'free' | 'complementary' | 'analogous' | 'triadic' | 'split';

interface ColorNode {
    property: string;
    value: string;
    hue: number;
    saturation: number;
    lightness: number;
}

/** Parse a CSS color to HSL (basic support for hex, rgb, hsl, named) */
function parseToHSL(color: string): { h: number; s: number; l: number } | null {
    // Hex
    const hex = color.match(/^#([a-f0-9]{3,8})$/i);
    if (hex) {
        let h = hex[1];
        if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
        const r = parseInt(h.slice(0, 2), 16) / 255;
        const g = parseInt(h.slice(2, 4), 16) / 255;
        const b = parseInt(h.slice(4, 6), 16) / 255;
        return rgbToHsl(r, g, b);
    }
    // rgb/rgba
    const rgb = color.match(/rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/);
    if (rgb) return rgbToHsl(+rgb[1] / 255, +rgb[2] / 255, +rgb[3] / 255);
    // hsl
    const hsl = color.match(/hsla?\(\s*([\d.]+)[,\s]+([\d.]+)%[,\s]+([\d.]+)%/);
    if (hsl) return { h: +hsl[1], s: +hsl[2], l: +hsl[3] };
    // Named colors (basic subset)
    const named: Record<string, string> = {
        'white': '#ffffff', 'black': '#000000', 'red': '#ff0000', 'blue': '#0000ff',
        'green': '#008000', 'purple': '#800080', 'orange': '#ffa500', 'yellow': '#ffff00',
    };
    if (named[color.toLowerCase()]) return parseToHSL(named[color.toLowerCase()]);
    return null;
}

function rgbToHsl(r: number, g: number, b: number) {
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    const l = (max + min) / 2;
    if (max === min) return { h: 0, s: 0, l: l * 100 };
    const d = max - min;
    const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    let h = 0;
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
    return { h: h * 360, s: s * 100, l: l * 100 };
}

export default function ColorRelationshipEditor() {
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const propertyStacks = useEditorStore((s) => s.propertyStacks);
    const [harmonyMode, setHarmonyMode] = useState<HarmonyMode>('free');
    const [activeColor, setActiveColor] = useState<number | null>(null);

    // Extract all color properties from the selected node
    const colors = useMemo<ColorNode[]>(() => {
        const selId = selectedIds[0];
        if (!selId) return [];
        const stack = propertyStacks[selId] ?? [];
        const colorProps = stack.filter((p) =>
            ['color', 'background-color', 'border-color', 'background', 'fill', 'stroke'].includes(p.property) ||
            p.property.includes('color')
        );
        const result: ColorNode[] = [];
        for (const p of colorProps) {
            const hsl = parseToHSL(p.computedValue);
            if (hsl) {
                result.push({
                    property: p.property,
                    value: p.computedValue,
                    hue: hsl.h,
                    saturation: hsl.s,
                    lightness: hsl.l,
                });
            }
        }
        return result;
    }, [selectedIds, propertyStacks]);

    // If no colors found, show demo colors
    const displayColors = useMemo<ColorNode[]>(() => {
        if (colors.length > 0) return colors;
        return [
            { property: 'accent', value: '#6366f1', hue: 239, saturation: 84, lightness: 67 },
            { property: 'background', value: '#0f1117', hue: 225, saturation: 20, lightness: 8 },
            { property: 'text-primary', value: '#e2e8f0', hue: 214, saturation: 32, lightness: 91 },
            { property: 'success', value: '#10b981', hue: 160, saturation: 84, lightness: 39 },
            { property: 'warning', value: '#f59e0b', hue: 38, saturation: 92, lightness: 50 },
            { property: 'purple', value: '#a78bfa', hue: 256, saturation: 93, lightness: 76 },
        ];
    }, [colors]);

    const wheelR = 90;
    const cx = 110, cy = 110;

    const handleColorDrag = useCallback((_idx: number) => {
        // In a real system, this would update the CSS variable/token
        // For now it sets the active highlight
        setActiveColor(_idx);
    }, []);

    return (
        <div className="ob-color-editor">
            <div className="ob-ce-header">COLOR RELATIONSHIPS</div>

            {/* Harmony mode buttons */}
            <div className="ob-ce-modes">
                {(['free', 'complementary', 'analogous', 'triadic', 'split'] as const).map((m) => (
                    <button
                        key={m}
                        className={`ob-ce-mode-btn${harmonyMode === m ? ' active' : ''}`}
                        onClick={() => setHarmonyMode(m)}
                    >
                        {m.slice(0, 4)}
                    </button>
                ))}
            </div>

            {/* Hue wheel SVG */}
            <svg width={220} height={220} viewBox="0 0 220 220" className="ob-ce-wheel">
                <defs>
                    {/* Conic-like hue ring via multiple arc segments */}
                    {Array.from({ length: 36 }, (_, i) => {
                        const a1 = i * 10 * Math.PI / 180;
                        const a2 = (i + 1) * 10 * Math.PI / 180;
                        return (
                            <path key={i}
                                d={`M ${cx + Math.cos(a1) * wheelR} ${cy + Math.sin(a1) * wheelR} A ${wheelR} ${wheelR} 0 0 1 ${cx + Math.cos(a2) * wheelR} ${cy + Math.sin(a2) * wheelR} L ${cx + Math.cos(a2) * (wheelR - 18)} ${cy + Math.sin(a2) * (wheelR - 18)} A ${wheelR - 18} ${wheelR - 18} 0 0 0 ${cx + Math.cos(a1) * (wheelR - 18)} ${cy + Math.sin(a1) * (wheelR - 18)} Z`}
                                fill={`hsl(${i * 10}, 80%, 55%)`}
                                opacity="0.6"
                                stroke="none"
                            />
                        );
                    })}
                </defs>

                {/* Center label */}
                <text x={cx} y={cy - 2} textAnchor="middle" className="ob-ce-center-label" fill="rgba(255,255,255,0.3)" fontSize="8">
                    {harmonyMode.toUpperCase()}
                </text>
                <text x={cx} y={cy + 10} textAnchor="middle" className="ob-ce-center-count" fill="rgba(255,255,255,0.5)" fontSize="10" fontWeight="600">
                    {displayColors.length} colors
                </text>

                {/* Color nodes on the wheel */}
                {displayColors.map((c, i) => {
                    const angle = (c.hue - 90) * Math.PI / 180;
                    const r = wheelR - 9; // middle of the ring
                    const nx = cx + Math.cos(angle) * r;
                    const ny = cy + Math.sin(angle) * r;
                    const isActive = activeColor === i;

                    return (
                        <g key={i} onClick={() => handleColorDrag(i)} style={{ cursor: 'pointer' }}>
                            {/* Connection line to center */}
                            <line x1={cx} y1={cy} x2={nx} y2={ny}
                                stroke={c.value} strokeWidth="1" opacity={isActive ? 0.5 : 0.15} />
                            {/* Node circle */}
                            <circle cx={nx} cy={ny} r={isActive ? 8 : 5}
                                fill={c.value}
                                stroke={isActive ? '#fff' : 'rgba(255,255,255,0.3)'}
                                strokeWidth={isActive ? 2 : 0.5}
                                filter={isActive ? undefined : undefined}
                            />
                        </g>
                    );
                })}

                {/* Harmony guides */}
                {harmonyMode === 'complementary' && activeColor != null && (() => {
                    const c = displayColors[activeColor];
                    const a = ((c.hue + 180) % 360 - 90) * Math.PI / 180;
                    return <circle cx={cx + Math.cos(a) * (wheelR - 9)} cy={cy + Math.sin(a) * (wheelR - 9)}
                        r="4" fill="none" stroke="#fff" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />;
                })()}
            </svg>

            {/* Color swatches */}
            <div className="ob-ce-swatches">
                {displayColors.map((c, i) => (
                    <button key={i}
                        className={`ob-ce-swatch${activeColor === i ? ' active' : ''}`}
                        onClick={() => setActiveColor(i)}
                        title={`${c.property}: ${c.value}`}
                    >
                        <div className="ob-ce-swatch-color" style={{ background: c.value }} />
                        <span className="ob-ce-swatch-label">{c.property}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
