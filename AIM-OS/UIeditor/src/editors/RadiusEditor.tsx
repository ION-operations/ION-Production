/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Radius Editor
   Visual border-radius editor with draggable corner arcs.
   Per OPUS Canon: "They drag the corner. The radius changes. They understand."
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback, useRef, useEffect } from 'react';

interface RadiusValue {
    topLeft: number;
    topRight: number;
    bottomRight: number;
    bottomLeft: number;
}

interface Props {
    value: RadiusValue;
    onChange?: (v: RadiusValue) => void;
    linked?: boolean;
    label?: string;
}

type Corner = 'topLeft' | 'topRight' | 'bottomRight' | 'bottomLeft';

const PRESETS = [
    { label: 'none', value: 0 },
    { label: 'sm', value: 4 },
    { label: 'md', value: 8 },
    { label: 'lg', value: 12 },
    { label: 'xl', value: 16 },
    { label: 'full', value: 50 },
];

export default function RadiusEditor({ value, onChange, linked: initialLinked, label }: Props) {
    const [dragging, setDragging] = useState<Corner | null>(null);
    const [hover, setHover] = useState<Corner | null>(null);
    const [linked, setLinked] = useState(initialLinked ?? true);
    const dragRef = useRef({ startX: 0, startY: 0, startVal: 0 });

    const W = 200, H = 140;
    const rectX = 30, rectY = 10, rectW = W - 60, rectH = H - 30;
    const maxR = Math.min(rectW, rectH) / 2;

    const clamp = (v: number) => Math.max(0, Math.min(maxR, v));

    // Corner positions for handles
    const cornerPos = (corner: Corner): { cx: number; cy: number; dx: number; dy: number } => {
        const r = Math.min(value[corner], maxR);
        const scale = r / maxR;
        switch (corner) {
            case 'topLeft': return { cx: rectX + r, cy: rectY + r, dx: -1, dy: -1 };
            case 'topRight': return { cx: rectX + rectW - r, cy: rectY + r, dx: 1, dy: -1 };
            case 'bottomRight': return { cx: rectX + rectW - r, cy: rectY + rectH - r, dx: 1, dy: 1 };
            case 'bottomLeft': return { cx: rectX + r, cy: rectY + rectH - r, dx: -1, dy: 1 };
        }
    };

    const handleMouseDown = useCallback((e: React.MouseEvent, corner: Corner) => {
        e.stopPropagation();
        e.preventDefault();
        dragRef.current = { startX: e.clientX, startY: e.clientY, startVal: value[corner] };
        setDragging(corner);
    }, [value]);

    useEffect(() => {
        if (!dragging) return;
        const onMove = (e: MouseEvent) => {
            // Dragging inward = increase radius
            const pos = cornerPos(dragging);
            const dx = (e.clientX - dragRef.current.startX) * pos.dx;
            const dy = (e.clientY - dragRef.current.startY) * pos.dy;
            const delta = -(dx + dy) / 2; // negative because inward = positive radius
            const newVal = Math.round(clamp(dragRef.current.startVal + delta));
            if (onChange) {
                if (linked) {
                    onChange({ topLeft: newVal, topRight: newVal, bottomRight: newVal, bottomLeft: newVal });
                } else {
                    onChange({ ...value, [dragging]: newVal });
                }
            }
        };
        const onUp = () => setDragging(null);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    }, [dragging, value, onChange, linked]);

    const applyPreset = (v: number) => {
        onChange?.({ topLeft: v, topRight: v, bottomRight: v, bottomLeft: v });
    };

    // Build the rounded rect path with per-corner radii
    const rTL = Math.min(value.topLeft, maxR);
    const rTR = Math.min(value.topRight, maxR);
    const rBR = Math.min(value.bottomRight, maxR);
    const rBL = Math.min(value.bottomLeft, maxR);

    const path = `
        M ${rectX + rTL} ${rectY}
        L ${rectX + rectW - rTR} ${rectY}
        Q ${rectX + rectW} ${rectY} ${rectX + rectW} ${rectY + rTR}
        L ${rectX + rectW} ${rectY + rectH - rBR}
        Q ${rectX + rectW} ${rectY + rectH} ${rectX + rectW - rBR} ${rectY + rectH}
        L ${rectX + rBL} ${rectY + rectH}
        Q ${rectX} ${rectY + rectH} ${rectX} ${rectY + rectH - rBL}
        L ${rectX} ${rectY + rTL}
        Q ${rectX} ${rectY} ${rectX + rTL} ${rectY}
        Z
    `;

    const corners: Corner[] = ['topLeft', 'topRight', 'bottomRight', 'bottomLeft'];

    return (
        <div className="ob-visual-editor ob-radius-editor">
            {label && <div className="ob-ve-label"><span className="ob-ve-label-icon">◐</span>{label}</div>}
            <svg width={W} height={H} className="ob-radius-canvas">
                {/* Grid lines */}
                <line x1={rectX} y1={rectY} x2={rectX + rectW} y2={rectY} className="ob-radius-grid" />
                <line x1={rectX} y1={rectY + rectH} x2={rectX + rectW} y2={rectY + rectH} className="ob-radius-grid" />
                <line x1={rectX} y1={rectY} x2={rectX} y2={rectY + rectH} className="ob-radius-grid" />
                <line x1={rectX + rectW} y1={rectY} x2={rectX + rectW} y2={rectY + rectH} className="ob-radius-grid" />

                {/* Rounded rect preview */}
                <path d={path} className="ob-radius-shape" />

                {/* Corner arcs & handles */}
                {corners.map((c) => {
                    const p = cornerPos(c);
                    const r = Math.min(value[c], maxR);
                    const active = hover === c || dragging === c;
                    return (
                        <g key={c}>
                            {/* Arc indicator */}
                            {r > 2 && (
                                <circle cx={p.cx} cy={p.cy} r={r}
                                    fill="none" stroke="var(--ob-accent)" strokeWidth="1"
                                    strokeDasharray="3 3" opacity={active ? 0.6 : 0.2} />
                            )}
                            {/* Handle dot */}
                            <circle cx={p.cx} cy={p.cy} r={active ? 5 : 4}
                                className={`ob-radius-handle${active ? ' active' : ''}`}
                                onMouseDown={(e) => handleMouseDown(e, c)}
                                onMouseEnter={() => setHover(c)}
                                onMouseLeave={() => setHover(null)}
                            />
                            {/* Value label */}
                            <text x={p.cx + p.dx * 14} y={p.cy + p.dy * 14}
                                textAnchor="middle" dominantBaseline="central"
                                className={`ob-radius-value${active ? ' active' : ''}`}
                            >{value[c]}</text>
                        </g>
                    );
                })}
            </svg>

            <div className="ob-radius-controls">
                <button
                    className={`ob-radius-link${linked ? ' active' : ''}`}
                    onClick={() => setLinked(!linked)}
                    title={linked ? 'Unlink corners' : 'Link corners'}
                >
                    {linked ? '🔗' : '⛓️‍💥'}
                </button>
                <div className="ob-radius-presets">
                    {PRESETS.map((pr) => (
                        <button key={pr.label}
                            className={`ob-radius-preset${value.topLeft === pr.value && linked ? ' active' : ''}`}
                            onClick={() => applyPreset(pr.value)}
                        >{pr.label}</button>
                    ))}
                </div>
            </div>
            <div className="ob-ve-hint">↖ Drag corners to reshape • Click presets for quick values</div>
        </div>
    );
}
