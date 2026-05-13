/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Gradient Strip Editor
   Visual gradient bar with draggable color stops.
   Per OPUS Canon: "They drag color stops on the gradient."
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback, useRef, useEffect } from 'react';

interface GradientStop {
    position: number;   // 0–1
    color: string;
}

interface GradientValue {
    stops: GradientStop[];
    angle: number;      // degrees
    type: 'linear' | 'radial';
}

interface Props {
    value: GradientValue;
    onChange?: (v: GradientValue) => void;
    label?: string;
}

export default function GradientStripEditor({ value, onChange, label }: Props) {
    const [dragging, setDragging] = useState<number | null>(null);
    const [selected, setSelected] = useState<number>(0);
    const [dragAngle, setDragAngle] = useState(false);
    const barRef = useRef<SVGRectElement>(null);
    const angleRef = useRef({ startX: 0, startAngle: 0 });

    const W = 220, barH = 32, barY = 28, barX = 10, barW = W - 20;
    const totalH = 110;

    // Build gradient CSS string
    const gradStr = value.stops
        .map((s) => `${s.color} ${Math.round(s.position * 100)}%`)
        .join(', ');
    const gradientCSS = value.type === 'linear'
        ? `linear-gradient(${value.angle}deg, ${gradStr})`
        : `radial-gradient(circle, ${gradStr})`;

    const handleStopDown = useCallback((e: React.MouseEvent, idx: number) => {
        e.stopPropagation();
        e.preventDefault();
        setDragging(idx);
        setSelected(idx);
    }, []);

    const handleBarClick = useCallback((e: React.MouseEvent) => {
        if (dragging !== null) return;
        const rect = barRef.current?.getBoundingClientRect();
        if (!rect) return;
        const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        // Interpolate color from nearest stops
        const newStop: GradientStop = { position: pos, color: '#ffffff' };
        const next = { ...value, stops: [...value.stops, newStop].sort((a, b) => a.position - b.position) };
        onChange?.(next);
        setSelected(next.stops.findIndex((s) => s === newStop));
    }, [value, onChange, dragging]);

    useEffect(() => {
        if (dragging === null) return;
        const onMove = (e: MouseEvent) => {
            const rect = barRef.current?.getBoundingClientRect();
            if (!rect) return;
            const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            const next = { ...value, stops: value.stops.map((s, i) => i === dragging ? { ...s, position: pos } : s) };
            onChange?.(next);
        };
        const onUp = () => setDragging(null);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    }, [dragging, value, onChange]);

    // Angle drag
    const handleAngleDown = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        e.preventDefault();
        angleRef.current = { startX: e.clientX, startAngle: value.angle };
        setDragAngle(true);
    }, [value.angle]);

    useEffect(() => {
        if (!dragAngle) return;
        const onMove = (e: MouseEvent) => {
            const delta = (e.clientX - angleRef.current.startX) * 1.5;
            const newAngle = Math.round(angleRef.current.startAngle + delta) % 360;
            onChange?.({ ...value, angle: newAngle < 0 ? newAngle + 360 : newAngle });
        };
        const onUp = () => setDragAngle(false);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    }, [dragAngle, value, onChange]);

    return (
        <div className="ob-visual-editor ob-gradient-editor">
            {label && <div className="ob-ve-label"><span className="ob-ve-label-icon">◧</span>{label}</div>}
            <svg width={W} height={totalH} className="ob-gradient-canvas">
                <defs>
                    <linearGradient id="ob-grad-preview" x1="0" x2="1" y1="0" y2="0">
                        {value.stops.map((s, i) => (
                            <stop key={i} offset={s.position} stopColor={s.color} />
                        ))}
                    </linearGradient>
                </defs>

                {/* Gradient bar */}
                <rect ref={barRef}
                    x={barX} y={barY} width={barW} height={barH} rx="4"
                    fill="url(#ob-grad-preview)"
                    className="ob-gradient-bar"
                    onClick={handleBarClick}
                />

                {/* Color stops */}
                {value.stops.map((stop, i) => {
                    const sx = barX + stop.position * barW;
                    const active = selected === i || dragging === i;
                    return (
                        <g key={i}>
                            {/* Stop marker triangle */}
                            <polygon
                                points={`${sx - 5},${barY - 2} ${sx + 5},${barY - 2} ${sx},${barY + 6}`}
                                fill={stop.color}
                                stroke={active ? 'var(--ob-accent)' : 'rgba(255,255,255,.3)'}
                                strokeWidth={active ? 2 : 1}
                                className="ob-gradient-stop-marker"
                                onMouseDown={(e) => handleStopDown(e, i)}
                            />
                            {/* Position label */}
                            <text x={sx} y={barY - 8}
                                textAnchor="middle"
                                className={`ob-gradient-label${active ? ' active' : ''}`}
                            >{Math.round(stop.position * 100)}%</text>
                        </g>
                    );
                })}

                {/* Angle indicator */}
                {value.type === 'linear' && (
                    <g transform={`translate(${W / 2}, ${barY + barH + 24})`}>
                        <circle cx="0" cy="0" r="14" className="ob-gradient-angle-ring" />
                        <line
                            x1="0" y1="0"
                            x2={Math.cos((value.angle - 90) * Math.PI / 180) * 12}
                            y2={Math.sin((value.angle - 90) * Math.PI / 180) * 12}
                            stroke="var(--ob-accent)" strokeWidth="2" strokeLinecap="round"
                        />
                        <circle cx="0" cy="0" r="3" fill="var(--ob-accent)" opacity=".8" />
                        <circle
                            cx={Math.cos((value.angle - 90) * Math.PI / 180) * 12}
                            cy={Math.sin((value.angle - 90) * Math.PI / 180) * 12}
                            r="4" className="ob-gradient-angle-handle"
                            onMouseDown={handleAngleDown}
                            style={{ cursor: 'grab' }}
                        />
                        <text x="22" y="4" className="ob-gradient-angle-text">{value.angle}°</text>
                    </g>
                )}
            </svg>

            {/* Selected stop color */}
            {value.stops[selected] && (
                <div className="ob-gradient-selected">
                    <div className="ob-gradient-swatch" style={{ background: value.stops[selected].color }} />
                    <span className="ob-gradient-color-label">{value.stops[selected].color}</span>
                </div>
            )}
            <div className="ob-ve-hint">↔ Drag stops to reposition • Click bar to add • Drag angle to rotate</div>
        </div>
    );
}
