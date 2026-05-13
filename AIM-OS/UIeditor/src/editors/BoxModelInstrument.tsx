/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Box Model Instrument
   Visual editor for margin/padding/content — drag edges, not type numbers.
   Per OPUS Canon: "The user sees the box. They drag the edge. The spacing changes."
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback, useRef, useEffect } from 'react';

interface BoxModelValue {
    margin: { top: number; right: number; bottom: number; left: number };
    padding: { top: number; right: number; bottom: number; left: number };
    width: number;
    height: number;
}

interface Props {
    value: BoxModelValue;
    onChange?: (v: BoxModelValue) => void;
    label?: string;
}

type Edge = 'margin-top' | 'margin-right' | 'margin-bottom' | 'margin-left'
    | 'padding-top' | 'padding-right' | 'padding-bottom' | 'padding-left';

export default function BoxModelInstrument({ value, onChange, label }: Props) {
    const [dragging, setDragging] = useState<Edge | null>(null);
    const [hover, setHover] = useState<Edge | null>(null);
    const dragRef = useRef<{ startY: number; startX: number; startVal: number }>({ startY: 0, startX: 0, startVal: 0 });

    const canvasW = 220;
    const canvasH = 160;
    const mT = value.margin.top, mR = value.margin.right, mB = value.margin.bottom, mL = value.margin.left;
    const pT = value.padding.top, pR = value.padding.right, pB = value.padding.bottom, pL = value.padding.left;

    // Scale factors to fit in canvas
    const totalW = mL + pL + 60 + pR + mR; // 60px content zone
    const totalH = mT + pT + 32 + pB + mB;
    const sx = Math.min(1, (canvasW - 20) / Math.max(totalW, 1));
    const sy = Math.min(1, (canvasH - 20) / Math.max(totalH, 1));
    const s = Math.min(sx, sy, 1);

    const cx = canvasW / 2;
    const cy = canvasH / 2;

    // Scaled dimensions
    const smL = mL * s, smR = mR * s, smT = mT * s, smB = mB * s;
    const spL = pL * s, spR = pR * s, spT = pT * s, spB = pB * s;
    const cw = 60 * s, ch = 32 * s;

    // Rectangles (centered)
    const innerW = cw;
    const innerH = ch;
    const paddingW = spL + innerW + spR;
    const paddingH = spT + innerH + spB;
    const marginW = smL + paddingW + smR;
    const marginH = smT + paddingH + smB;

    const marginX = cx - marginW / 2;
    const marginY = cy - marginH / 2;
    const paddingX = marginX + smL;
    const paddingY = marginY + smT;
    const contentX = paddingX + spL;
    const contentY = paddingY + spT;

    const handleMouseDown = useCallback((e: React.MouseEvent, edge: Edge) => {
        e.stopPropagation();
        e.preventDefault();
        const [zone, side] = edge.split('-') as ['margin' | 'padding', 'top' | 'right' | 'bottom' | 'left'];
        dragRef.current = {
            startX: e.clientX,
            startY: e.clientY,
            startVal: value[zone][side as keyof typeof value.margin],
        };
        setDragging(edge);
    }, [value]);

    useEffect(() => {
        if (!dragging) return;
        const onMove = (e: MouseEvent) => {
            const [zone, side] = dragging.split('-') as ['margin' | 'padding', 'top' | 'right' | 'bottom' | 'left'];
            const isVert = side === 'top' || side === 'bottom';
            const delta = isVert
                ? (side === 'top' ? dragRef.current.startY - e.clientY : e.clientY - dragRef.current.startY)
                : (side === 'left' ? dragRef.current.startX - e.clientX : e.clientX - dragRef.current.startX);
            const newVal = Math.max(0, Math.round(dragRef.current.startVal + delta / (s || 1)));
            if (onChange) {
                const next = { ...value, [zone]: { ...value[zone], [side]: newVal } };
                onChange(next);
            }
        };
        const onUp = () => setDragging(null);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    }, [dragging, value, onChange, s]);

    const edgeZone = (edge: Edge, x: number, y: number, w: number, h: number) => (
        <rect
            key={edge}
            x={x} y={y} width={w} height={h}
            fill="transparent"
            style={{ cursor: edge.includes('top') || edge.includes('bottom') ? 'ns-resize' : 'ew-resize' }}
            onMouseDown={(e) => handleMouseDown(e, edge)}
            onMouseEnter={() => setHover(edge)}
            onMouseLeave={() => setHover(null)}
        />
    );

    const valLabel = (val: number, x: number, y: number, active: boolean) => (
        <text
            x={x} y={y}
            textAnchor="middle" dominantBaseline="central"
            className={`ob-bm-value${active ? ' active' : ''}`}
        >{val}</text>
    );

    return (
        <div className="ob-visual-editor ob-boxmodel-editor">
            {label && <div className="ob-ve-label"><span className="ob-ve-label-icon">◻</span>{label}</div>}
            <svg width={canvasW} height={canvasH} className="ob-bm-canvas">
                {/* Margin zone */}
                <rect x={marginX} y={marginY} width={marginW} height={marginH}
                    rx="3" className="ob-bm-margin" />

                {/* Padding zone */}
                <rect x={paddingX} y={paddingY} width={paddingW} height={paddingH}
                    rx="2" className="ob-bm-padding" />

                {/* Content zone */}
                <rect x={contentX} y={contentY} width={innerW} height={innerH}
                    rx="1" className="ob-bm-content" />
                <text x={contentX + innerW / 2} y={contentY + innerH / 2}
                    textAnchor="middle" dominantBaseline="central"
                    className="ob-bm-content-label">content</text>

                {/* Zone labels */}
                <text x={marginX + 4} y={marginY + 10} className="ob-bm-zone-label">margin</text>
                <text x={paddingX + 4} y={paddingY + 10} className="ob-bm-zone-label">padding</text>

                {/* Margin values */}
                {valLabel(mT, cx, marginY + smT / 2, hover === 'margin-top' || dragging === 'margin-top')}
                {valLabel(mB, cx, marginY + marginH - smB / 2, hover === 'margin-bottom' || dragging === 'margin-bottom')}
                {valLabel(mL, marginX + smL / 2, cy, hover === 'margin-left' || dragging === 'margin-left')}
                {valLabel(mR, marginX + marginW - smR / 2, cy, hover === 'margin-right' || dragging === 'margin-right')}

                {/* Padding values */}
                {valLabel(pT, cx, paddingY + spT / 2, hover === 'padding-top' || dragging === 'padding-top')}
                {valLabel(pB, cx, paddingY + paddingH - spB / 2, hover === 'padding-bottom' || dragging === 'padding-bottom')}
                {valLabel(pL, paddingX + spL / 2, cy, hover === 'padding-left' || dragging === 'padding-left')}
                {valLabel(pR, paddingX + paddingW - spR / 2, cy, hover === 'padding-right' || dragging === 'padding-right')}

                {/* Drag hit zones — margin */}
                {edgeZone('margin-top', marginX, marginY, marginW, smT)}
                {edgeZone('margin-bottom', marginX, marginY + marginH - smB, marginW, smB)}
                {edgeZone('margin-left', marginX, marginY, smL, marginH)}
                {edgeZone('margin-right', marginX + marginW - smR, marginY, smR, marginH)}

                {/* Drag hit zones — padding */}
                {edgeZone('padding-top', paddingX, paddingY, paddingW, spT)}
                {edgeZone('padding-bottom', paddingX, paddingY + paddingH - spB, paddingW, spB)}
                {edgeZone('padding-left', paddingX, paddingY, spL, paddingH)}
                {edgeZone('padding-right', paddingX + paddingW - spR, paddingY, spR, paddingH)}

                {/* Highlight active edge */}
                {(hover || dragging) && (
                    <rect
                        x={marginX} y={marginY} width={marginW} height={marginH}
                        fill="none" stroke="var(--ob-accent)" strokeWidth="1" rx="3"
                        opacity={dragging ? 0.8 : 0.4}
                        style={{ pointerEvents: 'none' }}
                    />
                )}
            </svg>
            <div className="ob-ve-hint">↕ Drag edges to adjust spacing</div>
        </div>
    );
}
