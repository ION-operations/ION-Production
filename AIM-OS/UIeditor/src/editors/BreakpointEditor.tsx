/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Responsive Breakpoint Editor
   Draggable breakpoint ruler with mini layout previews at each viewport.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback } from 'react';
import { useEditorStore } from '../store/editorStore';

interface BreakpointDef {
    key: string;
    label: string;
    width: number;
    icon: string;
    color: string;
}

const BREAKPOINTS: BreakpointDef[] = [
    { key: 'desktop', label: 'Desktop', width: 1440, icon: '🖥', color: 'var(--ob-accent)' },
    { key: 'tablet', label: 'Tablet', width: 768, icon: '📱', color: 'var(--ob-purple)' },
    { key: 'mobile', label: 'Mobile', width: 375, icon: '📲', color: 'var(--ob-success)' },
];

const MAX_W = 1600;

export default function BreakpointEditor() {
    const breakpoint = useEditorStore((s) => s.breakpoint);
    const setBreakpoint = useEditorStore((s) => s.setBreakpoint);
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const nodes = useEditorStore((s) => s.nodes);
    const [dragging, setDragging] = useState<string | null>(null);

    const node = selectedIds[0] ? nodes[selectedIds[0]] : null;
    const rulerW = 220;

    const widthToX = useCallback((w: number) => (w / MAX_W) * rulerW, []);

    const handleBreakpointClick = useCallback((key: string) => {
        setBreakpoint(key as 'desktop' | 'tablet' | 'mobile');
    }, [setBreakpoint]);

    return (
        <div className="ob-bp-editor">
            <div className="ob-bp-header">RESPONSIVE BREAKPOINTS</div>

            {/* Ruler */}
            <svg width={rulerW + 20} height={100} viewBox={`-10 0 ${rulerW + 20} 100`} className="ob-bp-ruler">
                {/* Ruler track */}
                <rect x="0" y="20" width={rulerW} height="6" rx="3" fill="rgba(255,255,255,0.06)" />

                {/* Ruler ticks */}
                {[0, 200, 400, 600, 800, 1000, 1200, 1400, 1600].map((w) => (
                    <g key={w}>
                        <line x1={widthToX(w)} y1="18" x2={widthToX(w)} y2="28" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                        <text x={widthToX(w)} y="38" textAnchor="middle" fill="rgba(255,255,255,0.2)" fontSize="7" fontFamily="var(--ob-font-mono)">
                            {w}
                        </text>
                    </g>
                ))}

                {/* Active range */}
                {BREAKPOINTS.map((bp, i) => {
                    const nextW = BREAKPOINTS[i + 1]?.width ?? 0;
                    const x1 = widthToX(nextW);
                    const x2 = widthToX(bp.width);
                    return (
                        <rect key={bp.key}
                            x={x1} y="20" width={x2 - x1} height="6" rx="3"
                            fill={bp.color} opacity={breakpoint === bp.key ? 0.5 : 0.1}
                        />
                    );
                })}

                {/* Breakpoint markers */}
                {BREAKPOINTS.map((bp) => {
                    const x = widthToX(bp.width);
                    const isActive = breakpoint === bp.key;
                    return (
                        <g key={bp.key}
                            onClick={() => handleBreakpointClick(bp.key)}
                            onMouseDown={() => setDragging(bp.key)}
                            onMouseUp={() => setDragging(null)}
                            style={{ cursor: 'pointer' }}
                        >
                            {/* Marker line */}
                            <line x1={x} y1="10" x2={x} y2="32" stroke={bp.color}
                                strokeWidth={isActive ? 2 : 1} opacity={isActive ? 1 : 0.5} />

                            {/* Marker dot */}
                            <circle cx={x} cy="23" r={isActive ? 5 : 3.5}
                                fill={isActive ? bp.color : 'rgba(255,255,255,0.1)'}
                                stroke={bp.color} strokeWidth={isActive ? 0 : 1}
                            />

                            {/* Label */}
                            <text x={x} y="50" textAnchor="middle" fill={isActive ? bp.color : 'rgba(255,255,255,0.3)'}
                                fontSize="8" fontWeight={isActive ? '600' : '400'}>
                                {bp.label}
                            </text>
                            <text x={x} y="60" textAnchor="middle" fill="rgba(255,255,255,0.2)" fontSize="7"
                                fontFamily="var(--ob-font-mono)">
                                {bp.width}px
                            </text>
                        </g>
                    );
                })}
            </svg>

            {/* Mini preview cards */}
            <div className="ob-bp-previews">
                {BREAKPOINTS.map((bp) => {
                    const isActive = breakpoint === bp.key;
                    const scale = bp.width / MAX_W;
                    return (
                        <button key={bp.key}
                            className={`ob-bp-preview${isActive ? ' active' : ''}`}
                            onClick={() => handleBreakpointClick(bp.key)}
                            style={{ borderColor: isActive ? bp.color : undefined }}
                        >
                            <div className="ob-bp-preview-frame" style={{ width: `${scale * 100}%` }}>
                                {/* Simplified layout preview */}
                                <div className="ob-bp-preview-bar" />
                                <div className="ob-bp-preview-hero" />
                                <div className="ob-bp-preview-grid" style={{
                                    gridTemplateColumns: bp.key === 'mobile' ? '1fr' : bp.key === 'tablet' ? '1fr 1fr' : '1fr 1fr 1fr',
                                }}>
                                    <div className="ob-bp-preview-card" />
                                    <div className="ob-bp-preview-card" />
                                    {bp.key !== 'mobile' && <div className="ob-bp-preview-card" />}
                                </div>
                            </div>
                            <span className="ob-bp-preview-label" style={{ color: isActive ? bp.color : undefined }}>
                                {bp.icon} {bp.label}
                            </span>
                        </button>
                    );
                })}
            </div>

            {/* Node responsive info */}
            {node && (
                <div className="ob-bp-node-info">
                    <span className="ob-bp-node-name">{node.componentName || node.tag}</span>
                    <span className="ob-bp-node-size">{node.bounds.w} × {node.bounds.h}</span>
                </div>
            )}
        </div>
    );
}
