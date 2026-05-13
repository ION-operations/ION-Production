/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Typography Scale
   Visual type hierarchy editor with draggable size lines.
   Per OPUS Canon: "They see the type scale. They drag the line. The size changes."
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback, useRef, useEffect } from 'react';

interface TypographyValue {
    fontSize: number;
    fontWeight: number;
    lineHeight: number;
    letterSpacing: number;
    color: string;
}

interface Props {
    value: TypographyValue;
    onChange?: (v: TypographyValue) => void;
    label?: string;
    sampleText?: string;
}

const WEIGHT_LABELS: Record<number, string> = {
    100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular',
    500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black',
};

const SCALE_STEPS = [
    { label: 'xs', size: 10 },
    { label: 'sm', size: 12 },
    { label: 'base', size: 14 },
    { label: 'md', size: 16 },
    { label: 'lg', size: 20 },
    { label: 'xl', size: 24 },
    { label: '2xl', size: 32 },
    { label: '3xl', size: 40 },
    { label: '4xl', size: 48 },
    { label: 'display', size: 64 },
];

export default function TypographyScale({ value, onChange, label, sampleText = 'Aa' }: Props) {
    const [draggingSize, setDraggingSize] = useState(false);
    const [draggingWeight, setDraggingWeight] = useState(false);
    const [draggingLeading, setDraggingLeading] = useState(false);
    const dragRef = useRef({ startY: 0, startX: 0, startVal: 0 });

    const W = 220, H = 92;

    // Scale visualization — horizontal bar showing where current size falls
    const minSize = 8, maxSize = 72;
    const normalizedSize = Math.max(0, Math.min(1, (value.fontSize - minSize) / (maxSize - minSize)));
    const sizeX = 10 + normalizedSize * (W - 30);

    // Weight as horizontal position
    const normalizedWeight = (value.fontWeight - 100) / 800;

    // Line height indicator
    const leadingRatio = value.lineHeight;

    const handleSizeDown = useCallback((e: React.MouseEvent) => {
        e.stopPropagation(); e.preventDefault();
        dragRef.current = { startX: e.clientX, startY: 0, startVal: value.fontSize };
        setDraggingSize(true);
    }, [value]);

    const handleWeightDown = useCallback((e: React.MouseEvent) => {
        e.stopPropagation(); e.preventDefault();
        dragRef.current = { startX: e.clientX, startY: 0, startVal: value.fontWeight };
        setDraggingWeight(true);
    }, [value]);

    const handleLeadingDown = useCallback((e: React.MouseEvent) => {
        e.stopPropagation(); e.preventDefault();
        dragRef.current = { startX: 0, startY: e.clientY, startVal: value.lineHeight };
        setDraggingLeading(true);
    }, [value]);

    useEffect(() => {
        if (!draggingSize && !draggingWeight && !draggingLeading) return;
        const onMove = (e: MouseEvent) => {
            if (draggingSize) {
                const delta = (e.clientX - dragRef.current.startX) * 0.5;
                const newSize = Math.round(Math.max(minSize, Math.min(maxSize, dragRef.current.startVal + delta)));
                onChange?.({ ...value, fontSize: newSize });
            }
            if (draggingWeight) {
                const delta = (e.clientX - dragRef.current.startX) * 2;
                const newWeight = Math.round((dragRef.current.startVal + delta) / 100) * 100;
                onChange?.({ ...value, fontWeight: Math.max(100, Math.min(900, newWeight)) });
            }
            if (draggingLeading) {
                const delta = -(e.clientY - dragRef.current.startY) * 0.01;
                const newLH = Math.round((dragRef.current.startVal + delta) * 100) / 100;
                onChange?.({ ...value, lineHeight: Math.max(0.8, Math.min(3, newLH)) });
            }
        };
        const onUp = () => { setDraggingSize(false); setDraggingWeight(false); setDraggingLeading(false); };
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
        return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    }, [draggingSize, draggingWeight, draggingLeading, value, onChange]);

    return (
        <div className="ob-visual-editor ob-typography-editor">
            {label && <div className="ob-ve-label"><span className="ob-ve-label-icon">T</span>{label}</div>}

            {/* Live preview */}
            <div className="ob-typo-preview" style={{
                fontSize: `${Math.min(value.fontSize, 42)}px`,
                fontWeight: value.fontWeight,
                lineHeight: value.lineHeight,
                letterSpacing: `${value.letterSpacing}px`,
                color: value.color,
            }}>
                {sampleText}
                <span className="ob-typo-size-badge">{value.fontSize}px</span>
            </div>

            {/* Scale ruler */}
            <svg width={W} height={H} className="ob-typo-canvas">
                {/* Size scale */}
                <text x="4" y="14" className="ob-typo-section-label">size</text>
                <line x1="10" y1="20" x2={W - 10} y2="20" className="ob-typo-track" />
                {SCALE_STEPS.map((step) => {
                    const x = 10 + ((step.size - minSize) / (maxSize - minSize)) * (W - 30);
                    return (
                        <g key={step.label}>
                            <line x1={x} y1="17" x2={x} y2="23" className="ob-typo-tick" />
                            <text x={x} y="30" textAnchor="middle" className="ob-typo-tick-label">{step.label}</text>
                        </g>
                    );
                })}
                {/* Size handle */}
                <circle cx={sizeX} cy="20" r={draggingSize ? 6 : 5}
                    className={`ob-typo-handle${draggingSize ? ' active' : ''}`}
                    onMouseDown={handleSizeDown}
                    style={{ cursor: 'ew-resize' }} />

                {/* Weight scale */}
                <text x="4" y="48" className="ob-typo-section-label">weight</text>
                <line x1="10" y1="55" x2={W - 10} y2="55" className="ob-typo-track" />
                {[100, 200, 300, 400, 500, 600, 700, 800, 900].map((w) => {
                    const x = 10 + ((w - 100) / 800) * (W - 30);
                    return (
                        <line key={w} x1={x} y1="52" x2={x} y2="58" className="ob-typo-tick" />
                    );
                })}
                <text x={10 + normalizedWeight * (W - 30)} y="67" textAnchor="middle"
                    className="ob-typo-weight-label">{WEIGHT_LABELS[value.fontWeight] || value.fontWeight}</text>
                <circle cx={10 + normalizedWeight * (W - 30)} cy="55" r={draggingWeight ? 6 : 5}
                    className={`ob-typo-handle${draggingWeight ? ' active' : ''}`}
                    onMouseDown={handleWeightDown}
                    style={{ cursor: 'ew-resize' }} />

                {/* Line-height indicator */}
                <text x="4" y="82" className="ob-typo-section-label">leading</text>
                <rect x="55" y="75" width="24" height="14" rx="2" className="ob-typo-leading-box" />
                <text x="67" y="84" textAnchor="middle" dominantBaseline="central"
                    className="ob-typo-leading-text">Aa</text>

                {/* Leading lines above/below */}
                <line x1="55" y1={75 - (leadingRatio - 1) * 10} x2="79"
                    y2={75 - (leadingRatio - 1) * 10}
                    stroke="var(--ob-accent)" strokeWidth="1" strokeDasharray="2 2" />
                <line x1="55" y1={89 + (leadingRatio - 1) * 10} x2="79"
                    y2={89 + (leadingRatio - 1) * 10}
                    stroke="var(--ob-accent)" strokeWidth="1" strokeDasharray="2 2" />

                {/* Leading drag zone */}
                <rect x="50" y={70 - (leadingRatio - 1) * 10} width="34"
                    height={24 + (leadingRatio - 1) * 20}
                    fill="transparent"
                    onMouseDown={handleLeadingDown}
                    style={{ cursor: 'ns-resize' }} />

                <text x="95" y="84" className="ob-typo-leading-val">{leadingRatio.toFixed(2)}</text>
            </svg>

            <div className="ob-ve-hint">↔ Drag size/weight handles • ↕ Drag leading lines</div>
        </div>
    );
}
