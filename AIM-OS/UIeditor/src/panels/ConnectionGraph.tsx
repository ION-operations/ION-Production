/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Connection Graph
   Shows upstream/downstream node connections for the selected element.
   Compact SVG graph rendered in the right panel.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useMemo } from 'react';
import { useEditorStore } from '../store/editorStore';
import type { ConnectionType } from '../types';

const TYPE_COLORS: Record<ConnectionType, string> = {
    drives: '#6366f1',
    modulates: '#a78bfa',
    gates: '#f59e0b',
    couples: '#10b981',
    sequences: '#06b6d4',
    blends: '#ec4899',
};

const TYPE_LABELS: Record<ConnectionType, string> = {
    drives: '→',
    modulates: '~',
    gates: '⊣',
    couples: '↔',
    sequences: '⋯',
    blends: '⊕',
};

export default function ConnectionGraph() {
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const nodes = useEditorStore((s) => s.nodes);
    const connections = useEditorStore((s) => s.nodeConnections);
    const selectNode = useEditorStore((s) => s.selectNode);
    const setHoveredNode = useEditorStore((s) => s.setHoveredNode);

    const selId = selectedIds[0];

    // Find upstream and downstream connections
    const { upstream, downstream } = useMemo(() => {
        if (!selId) return { upstream: [], downstream: [] };
        return {
            upstream: connections.filter((c) => c.targetId === selId),
            downstream: connections.filter((c) => c.sourceId === selId),
        };
    }, [selId, connections]);

    if (!selId || (upstream.length === 0 && downstream.length === 0)) {
        return null;
    }

    const node = nodes[selId];
    if (!node) return null;

    // Layout params
    const svgW = 230, svgH = Math.max(80, 30 + Math.max(upstream.length, downstream.length) * 26 + 20);
    const cxCenter = svgW / 2, cyCenter = svgH / 2;
    const colLeft = 40, colRight = svgW - 40;

    return (
        <div className="ob-cg-panel">
            <div className="ob-cg-header">CONNECTIONS</div>
            <svg width={svgW} height={svgH} viewBox={`0 0 ${svgW} ${svgH}`} className="ob-cg-graph">
                {/* Center node */}
                <rect x={cxCenter - 40} y={cyCenter - 11} width={80} height={22} rx="4"
                    fill="var(--ob-accent)" opacity="0.2" stroke="var(--ob-accent)" strokeWidth="1" />
                <text x={cxCenter} y={cyCenter + 4} textAnchor="middle" fill="var(--ob-accent)"
                    fontSize="9" fontWeight="600">{node.componentName || node.tag}</text>

                {/* Upstream connections (left side) */}
                {upstream.map((conn, i) => {
                    const srcNode = nodes[conn.sourceId];
                    if (!srcNode) return null;
                    const y = 20 + i * 26;
                    const color = TYPE_COLORS[conn.type];

                    return (
                        <g key={conn.id}
                            onMouseEnter={() => setHoveredNode(conn.sourceId)}
                            onMouseLeave={() => setHoveredNode(null)}
                            onClick={() => selectNode(conn.sourceId)}
                            style={{ cursor: 'pointer' }}
                        >
                            {/* Arrow line */}
                            <path d={`M ${colLeft + 30} ${y} C ${cxCenter - 50} ${y}, ${cxCenter - 50} ${cyCenter}, ${cxCenter - 42} ${cyCenter}`}
                                fill="none" stroke={color} strokeWidth="1" opacity={conn.strength * 0.7}
                                strokeDasharray={conn.type === 'modulates' ? '3 2' : undefined}
                            />
                            {/* Source node */}
                            <rect x={2} y={y - 9} width={colLeft + 26} height={18} rx="3"
                                fill={color} opacity="0.1" stroke={color} strokeWidth="0.5" />
                            <text x={colLeft / 2 + 14} y={y + 3} textAnchor="middle" fill={color}
                                fontSize="8" fontWeight="500">
                                {srcNode.componentName || srcNode.tag}
                            </text>
                            {/* Type badge */}
                            <text x={colLeft + 38} y={y + 3} textAnchor="middle" fill={color}
                                fontSize="7" opacity="0.6">{TYPE_LABELS[conn.type]}</text>
                        </g>
                    );
                })}

                {/* Downstream connections (right side) */}
                {downstream.map((conn, i) => {
                    const tgtNode = nodes[conn.targetId];
                    if (!tgtNode) return null;
                    const y = 20 + i * 26;
                    const color = TYPE_COLORS[conn.type];

                    return (
                        <g key={conn.id}
                            onMouseEnter={() => setHoveredNode(conn.targetId)}
                            onMouseLeave={() => setHoveredNode(null)}
                            onClick={() => selectNode(conn.targetId)}
                            style={{ cursor: 'pointer' }}
                        >
                            {/* Arrow line */}
                            <path d={`M ${cxCenter + 42} ${cyCenter} C ${cxCenter + 50} ${cyCenter}, ${colRight - 30} ${y}, ${colRight - 30} ${y}`}
                                fill="none" stroke={color} strokeWidth="1" opacity={conn.strength * 0.7}
                                strokeDasharray={conn.type === 'sequences' ? '4 3' : undefined}
                            />
                            {/* Target node */}
                            <rect x={colRight - 30} y={y - 9} width={colRight - (colRight - 30) + 30} height={18} rx="3"
                                fill={color} opacity="0.1" stroke={color} strokeWidth="0.5" />
                            <text x={colRight + 14} y={y + 3} textAnchor="middle" fill={color}
                                fontSize="8" fontWeight="500">
                                {tgtNode.componentName || tgtNode.tag}
                            </text>
                            {/* Type badge */}
                            <text x={colRight - 38} y={y + 3} textAnchor="middle" fill={color}
                                fontSize="7" opacity="0.6">{TYPE_LABELS[conn.type]}</text>
                        </g>
                    );
                })}

                {/* Legend */}
                <g transform={`translate(4, ${svgH - 12})`}>
                    {Object.entries(TYPE_COLORS).slice(0, 4).map(([type, color], i) => (
                        <g key={type} transform={`translate(${i * 55}, 0)`}>
                            <rect width="6" height="6" rx="1" fill={color} opacity="0.6" />
                            <text x="9" y="6" fill="rgba(255,255,255,0.3)" fontSize="6">{type}</text>
                        </g>
                    ))}
                </g>
            </svg>
        </div>
    );
}
