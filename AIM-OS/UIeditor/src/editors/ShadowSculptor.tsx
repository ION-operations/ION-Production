/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Shadow Sculptor
   3D light-source metaphor for box-shadow editing.
   Per OPUS Canon: "They drag the light. The shadow follows. They understand."
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback, useRef, useEffect } from 'react';

interface ShadowValue {
    offsetX: number;
    offsetY: number;
    blur: number;
    spread: number;
    color: string;
    inset: boolean;
}

interface Props {
    value: ShadowValue;
    onChange?: (v: ShadowValue) => void;
    label?: string;
}

export default function ShadowSculptor({ value, onChange, label }: Props) {
    const [draggingLight, setDraggingLight] = useState(false);
    const [draggingSpread, setDraggingSpread] = useState(false);
    const dragRef = useRef({ startX: 0, startY: 0, startOX: 0, startOY: 0, startSpread: 0 });

    const W = 220, H = 160;
    const centerX = W / 2, centerY = H / 2;
    const elemW = 50, elemH = 36;
    const maxOffset = 30;

    // Light position is opposite to shadow offset
    const lightX = centerX - value.offsetX * 2;
    const lightY = centerY - value.offsetY * 2;

    // Clamp offsets
    const shadowOpacity = Math.max(0.1, Math.min(0.8, 0.5 - value.blur / 100));

    const handleLightDown = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        e.preventDefault();
        dragRef.current = {
            startX: e.clientX, startY: e.clientY,
            startOX: value.offsetX, startOY: value.offsetY, startSpread: 0
        };
        setDraggingLight(true);
    }, [value]);

    const handleSpreadDown = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        e.preventDefault();
        dragRef.current = {
            startX: e.clientX, startY: e.clientY,
            startOX: 0, startOY: 0, startSpread: value.spread
        };
        setDraggingSpread(true);
    }, [value]);

    useEffect(() => {
        if (!draggingLight && !draggingSpread) return;
        const onMove = (e: MouseEvent) => {
            if (draggingLight) {
                const dx = -(e.clientX - dragRef.current.startX) / 2;
                const dy = -(e.clientY - dragRef.current.startY) / 2;
                const ox = Math.round(Math.max(-maxOffset, Math.min(maxOffset, dragRef.current.startOX + dx)));
                const oy = Math.round(Math.max(-maxOffset, Math.min(maxOffset, dragRef.current.startOY + dy)));
                // Blur = distance from center
                const dist = Math.sqrt(ox * ox + oy * oy);
                const blur = Math.round(Math.max(0, dist));
                onChange?.({ ...value, offsetX: ox, offsetY: oy, blur });
            }
            if (draggingSpread) {
                const delta = -(e.clientY - dragRef.current.startY) / 2;
                const spread = Math.round(Math.max(-10, Math.min(30, dragRef.current.startSpread + delta)));
                onChange?.({ ...value, spread });
            }
        };
        const onUp = () => { setDraggingLight(false); setDraggingSpread(false); };
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    }, [draggingLight, draggingSpread, value, onChange]);

    // Shadow CSS for preview element
    const shadowCSS = `${value.inset ? 'inset ' : ''}${value.offsetX}px ${value.offsetY}px ${value.blur}px ${value.spread}px ${value.color}`;

    return (
        <div className="ob-visual-editor ob-shadow-editor">
            {label && <div className="ob-ve-label"><span className="ob-ve-label-icon">◫</span>{label}</div>}
            <svg width={W} height={H} className="ob-shadow-canvas">
                {/* Radial guide rings */}
                {[20, 40, 60].map((r) => (
                    <circle key={r} cx={centerX} cy={centerY} r={r}
                        fill="none" stroke="rgba(255,255,255,.04)" strokeWidth="1" />
                ))}

                {/* Shadow (rendered as offset blurred rect) */}
                <defs>
                    <filter id="ob-shadow-blur" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation={Math.max(1, value.blur / 3)} />
                    </filter>
                </defs>
                <rect
                    x={centerX - elemW / 2 + value.offsetX}
                    y={centerY - elemH / 2 + value.offsetY}
                    width={elemW + value.spread * 2}
                    height={elemH + value.spread * 2}
                    rx="6"
                    fill={value.color}
                    filter="url(#ob-shadow-blur)"
                    opacity={0.6}
                />

                {/* Element preview */}
                <rect
                    x={centerX - elemW / 2}
                    y={centerY - elemH / 2}
                    width={elemW} height={elemH}
                    rx="6"
                    className="ob-shadow-element"
                />
                <text x={centerX} y={centerY}
                    textAnchor="middle" dominantBaseline="central"
                    className="ob-shadow-el-label">elem</text>

                {/* Connection line from light to element */}
                <line x1={lightX} y1={lightY} x2={centerX} y2={centerY}
                    stroke="var(--ob-accent)" strokeWidth="1" strokeDasharray="3 3" opacity=".4" />

                {/* Light source handle */}
                <g className={`ob-shadow-light${draggingLight ? ' dragging' : ''}`}
                    onMouseDown={handleLightDown}
                    style={{ cursor: 'grab' }}
                >
                    <circle cx={lightX} cy={lightY} r="12"
                        fill="rgba(255,200,50,.15)" stroke="rgba(255,200,50,.6)" strokeWidth="1" />
                    <circle cx={lightX} cy={lightY} r="5"
                        fill="rgba(255,220,80,.9)" stroke="none" />
                    {/* Rays */}
                    {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => (
                        <line key={a}
                            x1={lightX + Math.cos(a * Math.PI / 180) * 8}
                            y1={lightY + Math.sin(a * Math.PI / 180) * 8}
                            x2={lightX + Math.cos(a * Math.PI / 180) * 14}
                            y2={lightY + Math.sin(a * Math.PI / 180) * 14}
                            stroke="rgba(255,220,80,.4)" strokeWidth="1" strokeLinecap="round"
                        />
                    ))}
                </g>

                {/* Spread ring */}
                <circle cx={centerX} cy={centerY + elemH / 2 + 8 + value.spread}
                    r="4"
                    className={`ob-shadow-spread-handle${draggingSpread ? ' active' : ''}`}
                    onMouseDown={handleSpreadDown}
                    style={{ cursor: 'ns-resize' }}
                />
                <text x={centerX + 10} y={centerY + elemH / 2 + 12 + value.spread}
                    className="ob-shadow-spread-label">spread {value.spread}</text>
            </svg>

            {/* Values readout */}
            <div className="ob-shadow-values">
                <span>x: {value.offsetX}</span>
                <span>y: {value.offsetY}</span>
                <span>blur: {value.blur}</span>
                <span>spread: {value.spread}</span>
                <span className="ob-shadow-swatch" style={{ background: value.color }} />
            </div>

            <div className="ob-shadow-css-preview">
                <code>{shadowCSS}</code>
            </div>
            <div className="ob-ve-hint">☀ Drag light source to shape shadow • ↕ Drag spread handle</div>
        </div>
    );
}
