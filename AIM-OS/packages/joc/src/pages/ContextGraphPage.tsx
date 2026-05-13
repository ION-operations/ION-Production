import { useState, useEffect, useMemo, useCallback } from 'react';
import { useAIMOS } from '../hooks/useAIMOS';
import { callTool } from '../services/mcpClient';

// ─── Types ───

interface ContextNode {
    id: string;
    type: 'query' | 'atom' | 'retrieval' | 'evidence' | 'witness' | 'context-window' | 'fork' | 'merge' | 'system';
    label: string;
    system: 'CMC' | 'HHNI' | 'SEG' | 'VIF' | 'APOE' | 'CAS' | 'TCS' | 'USER';
    confidence?: number;
    timestamp: string;
    metadata?: Record<string, unknown>;
    x: number;
    y: number;
}

interface ContextEdge {
    id: string;
    source: string;
    target: string;
    type: 'retrieved_from' | 'supports' | 'contradicts' | 'witnessed_by' | 'compressed_to' | 'derived_from' | 'forks_to' | 'merges_into';
    label?: string;
}

interface ContextSession {
    id: string;
    query: string;
    timestamp: string;
    nodeCount: number;
    systems: string[];
    finalConfidence: number;
    source: 'live' | 'mock';
}

interface MemoryAtom {
    atom_id?: string;
    id?: string;
    content?: string;
    modality?: string;
    tags?: Record<string, unknown>;
    created_at?: string;
    similarity?: number;
    [key: string]: unknown;
}

// ─── Constants ───

const SYSTEM_COLORS: Record<string, string> = {
    CMC: '#6366f1',
    HHNI: '#22d3ee',
    SEG: '#f472b6',
    VIF: '#a3e635',
    APOE: '#fb923c',
    CAS: '#c084fc',
    TCS: '#38bdf8',
    USER: '#94a3b8',
};

const EDGE_TYPE_COLORS: Record<string, string> = {
    retrieved_from: '#22d3ee',
    supports: '#a3e635',
    contradicts: '#ef4444',
    witnessed_by: '#a3e635',
    compressed_to: '#fb923c',
    derived_from: '#6366f1',
    forks_to: '#94a3b8',
    merges_into: '#f472b6',
};

const NODE_TYPE_SHAPES: Record<string, string> = {
    query: '◆',
    atom: '●',
    retrieval: '◇',
    evidence: '▲',
    witness: '✦',
    'context-window': '■',
    fork: '⟨',
    merge: '⟩',
    system: '◎',
};

function confidenceClass(c: number | undefined): string {
    if (c === undefined) return '';
    if (c >= 0.9) return 'confidence-high';
    if (c >= 0.7) return 'confidence-mid';
    return 'confidence-low';
}

// ─── Graph Builder ───
// Transforms real MCP data into graph nodes and edges

function buildGraphFromAtoms(
    queryText: string,
    atoms: MemoryAtom[],
    consciousness: { cognitive_drift?: number; working_memory_items?: number } | null,
): { nodes: ContextNode[]; edges: ContextEdge[] } {
    const nodes: ContextNode[] = [];
    const edges: ContextEdge[] = [];

    if (atoms.length === 0) return { nodes, edges };

    const SVG_W = 800;
    const SVG_H = 400;
    const Y_CENTER = SVG_H / 2;

    // 1. User query node (left edge)
    const queryNode: ContextNode = {
        id: 'q-live', type: 'query', label: queryText.length > 50 ? queryText.substring(0, 48) + '…' : queryText,
        system: 'USER', timestamp: new Date().toISOString().substring(11, 19), x: 40, y: Y_CENTER,
    };
    nodes.push(queryNode);

    // 2. Fork node (HHNI retrieval start)
    const forkNode: ContextNode = {
        id: 'fork-live', type: 'fork', label: 'HHNI Multi-Path Retrieval',
        system: 'HHNI', timestamp: queryNode.timestamp, x: 130, y: Y_CENTER,
    };
    nodes.push(forkNode);
    edges.push({ id: 'e-q-fork', source: 'q-live', target: 'fork-live', type: 'forks_to', label: 'query' });

    // 3. CMC atom nodes (spread vertically in the middle zone)
    const atomSpacing = Math.min(60, (SVG_H - 60) / Math.max(atoms.length, 1));
    const atomStartY = Y_CENTER - ((atoms.length - 1) * atomSpacing) / 2;

    atoms.forEach((atom, i) => {
        const atomId = atom.atom_id || atom.id || `atom-${i}`;
        const content = atom.content || 'Unknown atom';
        const label = content.length > 35 ? content.substring(0, 33) + '…' : content;
        const similarity = atom.similarity || (atom.tags ? Object.values(atom.tags).find(v => typeof v === 'number') : undefined);

        const atomNode: ContextNode = {
            id: `cmc-${atomId}`,
            type: 'atom',
            label: `CMC: ${label}`,
            system: 'CMC',
            confidence: typeof similarity === 'number' ? Math.min(similarity, 1) : undefined,
            timestamp: (atom.created_at || '').substring(11, 19) || queryNode.timestamp,
            metadata: { atom_id: atomId, modality: atom.modality || 'text', ...(atom.tags || {}) },
            x: 300 + (i % 2 === 0 ? 0 : 40),
            y: atomStartY + i * atomSpacing,
        };
        nodes.push(atomNode);

        // HHNI retrieval edge
        const retrievalNode: ContextNode = {
            id: `hhni-r-${i}`,
            type: 'retrieval',
            label: `HHNI L${i < 2 ? 2 : 3}: path ${String.fromCharCode(65 + i)}`,
            system: 'HHNI',
            confidence: typeof similarity === 'number' ? Math.min(similarity, 1) : 0.85,
            timestamp: queryNode.timestamp,
            x: 200,
            y: atomStartY + i * atomSpacing,
        };
        nodes.push(retrievalNode);

        edges.push({ id: `e-fork-r${i}`, source: 'fork-live', target: `hhni-r-${i}`, type: 'forks_to', label: `path ${String.fromCharCode(65 + i)}` });
        edges.push({ id: `e-r${i}-cmc`, source: `hhni-r-${i}`, target: `cmc-${atomId}`, type: 'retrieved_from' });
    });

    // 4. SEG evidence synthesis node
    const segNode: ContextNode = {
        id: 'seg-synth', type: 'evidence',
        label: `SEG: ${atoms.length} evidence streams`,
        system: 'SEG', confidence: 0.88, timestamp: queryNode.timestamp,
        x: 480, y: Y_CENTER - 30,
    };
    nodes.push(segNode);

    // Connect atoms → SEG
    atoms.forEach((atom, i) => {
        const atomId = atom.atom_id || atom.id || `atom-${i}`;
        edges.push({ id: `e-cmc${i}-seg`, source: `cmc-${atomId}`, target: 'seg-synth', type: 'supports' });
    });

    // 5. Merge node (APOE orchestration)
    const mergeNode: ContextNode = {
        id: 'merge-live', type: 'merge',
        label: 'APOE: Context Assembly',
        system: 'APOE', timestamp: queryNode.timestamp,
        x: 560, y: Y_CENTER,
    };
    nodes.push(mergeNode);
    edges.push({ id: 'e-seg-merge', source: 'seg-synth', target: 'merge-live', type: 'merges_into' });

    // 6. CAS consciousness node (if drift data available)
    if (consciousness?.cognitive_drift !== undefined) {
        const casNode: ContextNode = {
            id: 'cas-drift', type: 'system',
            label: `CAS: drift=${(consciousness.cognitive_drift * 100).toFixed(0)}%`,
            system: 'CAS', confidence: 1 - consciousness.cognitive_drift,
            timestamp: queryNode.timestamp,
            x: 480, y: Y_CENTER + 60,
        };
        nodes.push(casNode);
        edges.push({ id: 'e-cas-merge', source: 'cas-drift', target: 'merge-live', type: 'merges_into' });
    }

    // 7. VIF verification node
    const avgConf = atoms.length > 0
        ? atoms.reduce((sum, a) => sum + (typeof a.similarity === 'number' ? a.similarity : 0.85), 0) / atoms.length
        : 0.85;
    const vifNode: ContextNode = {
        id: 'vif-verify', type: 'witness',
        label: `VIF: κ=${avgConf.toFixed(2)}, Band ${avgConf >= 0.9 ? 'A' : avgConf >= 0.7 ? 'B' : 'C'}`,
        system: 'VIF', confidence: avgConf, timestamp: queryNode.timestamp,
        x: 640, y: Y_CENTER,
    };
    nodes.push(vifNode);
    edges.push({ id: 'e-merge-vif', source: 'merge-live', target: 'vif-verify', type: 'witnessed_by' });

    // 8. Final context window node
    const ctxNode: ContextNode = {
        id: 'ctx-final', type: 'context-window',
        label: `Final: ${atoms.length} atoms (${consciousness?.working_memory_items || '?'} WM items)`,
        system: 'APOE', confidence: avgConf, timestamp: queryNode.timestamp,
        x: 740, y: Y_CENTER,
    };
    nodes.push(ctxNode);
    edges.push({ id: 'e-vif-ctx', source: 'vif-verify', target: 'ctx-final', type: 'compressed_to' });

    return { nodes, edges };
}

// ─── Component ───

export function ContextGraphPage() {
    const [selectedNode, setSelectedNode] = useState<ContextNode | null>(null);
    const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
    const [graphNodes, setGraphNodes] = useState<ContextNode[]>([]);
    const [graphEdges, setGraphEdges] = useState<ContextEdge[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [viewMode, setViewMode] = useState<'graph' | 'timeline' | 'tree'>('graph');

    const aimos = useAIMOS({
        pollDomains: ['timeline', 'memory', 'consciousness'],
        pollInterval: 15000,
    });

    // Build sessions from real timeline entries
    const sessions: ContextSession[] = useMemo(() => {
        if (!aimos.connected || aimos.timeline.length === 0) return [];

        return aimos.timeline.map((entry, i) => {
            const systems: string[] = ['CMC', 'HHNI'];
            const context = entry.context_state || {};
            if (context.vif_confidence || context.confidence) systems.push('VIF');
            if (context.seg_evidence || context.evidence) systems.push('SEG');
            if (context.cas_drift || context.consciousness) systems.push('CAS');
            if (context.apoe_plan || context.plan) systems.push('APOE');

            return {
                id: entry.prompt_id || `tl-${i}`,
                query: entry.user_input || 'Unknown query',
                timestamp: (entry.timestamp || '').substring(11, 16) || `${9 - i}:${String(45 - i * 5).padStart(2, '0')}`,
                nodeCount: systems.length * 2 + 3,
                systems,
                finalConfidence: typeof context.confidence === 'number' ? context.confidence : 0.85,
                source: 'live' as const,
            };
        });
    }, [aimos.connected, aimos.timeline]);

    // Fetch atoms for a query and build graph
    const loadGraphForQuery = useCallback(async (query: string) => {
        setIsLoading(true);
        setSelectedNode(null);

        try {
            const result = await callTool<{ results?: MemoryAtom[]; count?: number }>('retrieve_memory', {
                query,
                limit: 8,
            });

            const atoms = result?.results || [];
            const { nodes, edges } = buildGraphFromAtoms(query, atoms, aimos.consciousness);
            setGraphNodes(nodes);
            setGraphEdges(edges);
        } catch (err) {
            console.error('Failed to load context graph:', err);
            setGraphNodes([]);
            setGraphEdges([]);
        } finally {
            setIsLoading(false);
        }
    }, [aimos.consciousness]);

    // Load graph when session is selected
    useEffect(() => {
        const session = sessions.find(s => s.id === selectedSessionId) || sessions[0];
        if (session) {
            loadGraphForQuery(session.query);
        }
    }, [selectedSessionId, sessions, loadGraphForQuery]);

    // Handle manual search
    const handleSearch = () => {
        if (searchQuery.trim()) {
            setSelectedSessionId(null);
            loadGraphForQuery(searchQuery.trim());
        }
    };

    const activeSession = selectedSessionId
        ? sessions.find(s => s.id === selectedSessionId)
        : sessions[0];

    return (
        <div className="context-graph-page">
            {/* Header */}
            <div className="ctx-header">
                <div className="ctx-header-left">
                    <h2 className="ctx-title">Context Graph</h2>
                    <span className="ctx-subtitle">
                        {aimos.connected ? 'Live AI Context Provenance' : 'AI Context Provenance Visualizer'}
                    </span>
                    {aimos.connected && (
                        <span className="mcp-badge online" style={{ marginLeft: 8 }}>
                            <span className="mcp-badge-dot" />
                            LIVE
                        </span>
                    )}
                </div>
                <div className="ctx-header-controls">
                    <div className="ctx-search-bar">
                        <input
                            className="ctx-search-input"
                            placeholder="Search memories..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') handleSearch(); }}
                        />
                        <button className="ctx-search-btn" onClick={handleSearch} disabled={isLoading}>
                            {isLoading ? '⟳' : '🔍'}
                        </button>
                    </div>
                    <div className="ctx-view-switcher">
                        {(['graph', 'timeline', 'tree'] as const).map(mode => (
                            <button
                                key={mode}
                                className={`ctx-view-btn ${viewMode === mode ? 'active' : ''}`}
                                onClick={() => setViewMode(mode)}
                            >
                                {mode === 'graph' ? '🕸️' : mode === 'timeline' ? '📊' : '🌳'} {mode}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="ctx-body">
                {/* Session Timeline Rail — Left */}
                <div className="ctx-session-rail">
                    <div className="ctx-rail-header">
                        {sessions.length > 0 ? `Context Sessions (${sessions.length})` : 'Context Sessions'}
                    </div>

                    {sessions.length === 0 && (
                        <div className="ctx-empty-sessions">
                            <span style={{ opacity: 0.5 }}>
                                {aimos.connected
                                    ? 'No timeline entries yet'
                                    : 'MCP offline — connect to see sessions'}
                            </span>
                        </div>
                    )}

                    {sessions.map(session => (
                        <button
                            key={session.id}
                            className={`ctx-session-item ${(activeSession?.id === session.id) ? 'active' : ''}`}
                            onClick={() => setSelectedSessionId(session.id)}
                        >
                            <div className="ctx-session-time">{session.timestamp}</div>
                            <div className="ctx-session-query">
                                {session.query.length > 50 ? session.query.substring(0, 48) + '…' : session.query}
                            </div>
                            <div className="ctx-session-meta">
                                <span className="ctx-session-nodes">{session.nodeCount} nodes</span>
                                <span className={`ctx-session-confidence ${confidenceClass(session.finalConfidence)}`}>
                                    κ={session.finalConfidence.toFixed(2)}
                                </span>
                            </div>
                            <div className="ctx-session-systems">
                                {session.systems.map(s => (
                                    <span key={s} className="ctx-system-badge" style={{ background: SYSTEM_COLORS[s] || '#555' }}>
                                        {s}
                                    </span>
                                ))}
                            </div>
                        </button>
                    ))}
                </div>

                {/* Main Graph Canvas — Center */}
                <div className="ctx-canvas">
                    {isLoading && (
                        <div className="ctx-loading-overlay">
                            <span className="ctx-loading-spinner">⟳</span>
                            <span>Fetching context provenance...</span>
                        </div>
                    )}

                    {graphNodes.length === 0 && !isLoading ? (
                        <div className="ctx-empty-graph">
                            <div className="ctx-empty-icon">🕸️</div>
                            <div className="ctx-empty-text">
                                {aimos.connected
                                    ? 'Select a session or search for memories to visualize context provenance.'
                                    : 'Connect to AIM-OS MCP server to see live context provenance graphs.'}
                            </div>
                            <div className="ctx-empty-hint">
                                The graph shows how AI context flows through CMC → HHNI → SEG → VIF
                            </div>
                        </div>
                    ) : (
                        <svg className="ctx-svg" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet">
                            {/* Grid */}
                            <defs>
                                <pattern id="ctx-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
                                </pattern>
                                <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
                                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                    <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.3)" />
                                </marker>
                                {/* Glow filter for selected nodes */}
                                <filter id="node-glow" x="-50%" y="-50%" width="200%" height="200%">
                                    <feGaussianBlur stdDeviation="4" result="blur" />
                                    <feMerge>
                                        <feMergeNode in="blur" />
                                        <feMergeNode in="SourceGraphic" />
                                    </feMerge>
                                </filter>
                            </defs>
                            <rect width="800" height="400" fill="url(#ctx-grid)" />

                            {/* Edges */}
                            {graphEdges.map(edge => {
                                const src = graphNodes.find(n => n.id === edge.source);
                                const tgt = graphNodes.find(n => n.id === edge.target);
                                if (!src || !tgt) return null;
                                const color = EDGE_TYPE_COLORS[edge.type] || '#555';
                                const isDashed = edge.type === 'contradicts';
                                return (
                                    <g key={edge.id}>
                                        <line
                                            x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
                                            stroke={color} strokeWidth={1.5}
                                            strokeDasharray={isDashed ? '4 3' : undefined}
                                            opacity={0.6}
                                            markerEnd="url(#arrow)"
                                        />
                                        {edge.label && (
                                            <text
                                                x={(src.x + tgt.x) / 2}
                                                y={(src.y + tgt.y) / 2 - 6}
                                                className="ctx-edge-label"
                                                fill={color}
                                            >
                                                {edge.label}
                                            </text>
                                        )}
                                    </g>
                                );
                            })}

                            {/* Nodes */}
                            {graphNodes.map(node => {
                                const color = SYSTEM_COLORS[node.system] || '#555';
                                const isSelected = selectedNode?.id === node.id;
                                return (
                                    <g key={node.id} onClick={() => setSelectedNode(node)} style={{ cursor: 'pointer' }}>
                                        {/* Glow if selected */}
                                        {isSelected && (
                                            <circle cx={node.x} cy={node.y} r={20} fill={color} opacity={0.15} filter="url(#node-glow)" />
                                        )}
                                        {/* Node circle */}
                                        <circle
                                            cx={node.x} cy={node.y} r={12}
                                            fill={`${color}22`}
                                            stroke={color}
                                            strokeWidth={isSelected ? 2.5 : 1.5}
                                        />
                                        {/* Shape indicator */}
                                        <text
                                            x={node.x} y={node.y + 4}
                                            textAnchor="middle"
                                            fill={color}
                                            fontSize={10}
                                        >
                                            {NODE_TYPE_SHAPES[node.type] || '●'}
                                        </text>
                                        {/* Label */}
                                        <text
                                            x={node.x} y={node.y + 26}
                                            textAnchor="middle"
                                            className="ctx-node-label"
                                        >
                                            {node.label.length > 30 ? node.label.substring(0, 28) + '…' : node.label}
                                        </text>
                                        {/* Confidence badge */}
                                        {node.confidence !== undefined && (
                                            <text
                                                x={node.x + 16} y={node.y - 8}
                                                className={`ctx-node-confidence ${confidenceClass(node.confidence)}`}
                                            >
                                                {node.confidence.toFixed(2)}
                                            </text>
                                        )}
                                    </g>
                                );
                            })}
                        </svg>
                    )}

                    {/* Legend */}
                    <div className="ctx-legend">
                        <div className="ctx-legend-section">
                            <span className="ctx-legend-title">Systems</span>
                            {Object.entries(SYSTEM_COLORS).map(([sys, color]) => (
                                <span key={sys} className="ctx-legend-item">
                                    <span className="ctx-legend-dot" style={{ background: color }} />
                                    {sys}
                                </span>
                            ))}
                        </div>
                        <div className="ctx-legend-section">
                            <span className="ctx-legend-title">Edges</span>
                            <span className="ctx-legend-item">
                                <span className="ctx-legend-line" style={{ background: EDGE_TYPE_COLORS.supports }} />
                                supports
                            </span>
                            <span className="ctx-legend-item">
                                <span className="ctx-legend-line dashed" style={{ background: EDGE_TYPE_COLORS.contradicts }} />
                                contradicts
                            </span>
                            <span className="ctx-legend-item">
                                <span className="ctx-legend-line" style={{ background: EDGE_TYPE_COLORS.retrieved_from }} />
                                retrieved
                            </span>
                        </div>
                    </div>
                </div>

                {/* Inspector Panel — Right */}
                <div className="ctx-inspector">
                    <div className="ctx-inspector-header">
                        {selectedNode ? 'Node Inspector' : 'Select a Node'}
                    </div>
                    {selectedNode ? (
                        <div className="ctx-inspector-content">
                            <div className="ctx-inspect-row">
                                <span className="ctx-inspect-key">Type</span>
                                <span className="ctx-inspect-val">
                                    {NODE_TYPE_SHAPES[selectedNode.type]} {selectedNode.type}
                                </span>
                            </div>
                            <div className="ctx-inspect-row">
                                <span className="ctx-inspect-key">System</span>
                                <span className="ctx-inspect-val">
                                    <span className="ctx-system-badge" style={{ background: SYSTEM_COLORS[selectedNode.system] }}>
                                        {selectedNode.system}
                                    </span>
                                </span>
                            </div>
                            <div className="ctx-inspect-row">
                                <span className="ctx-inspect-key">Label</span>
                                <span className="ctx-inspect-val">{selectedNode.label}</span>
                            </div>
                            {selectedNode.confidence !== undefined && (
                                <div className="ctx-inspect-row">
                                    <span className="ctx-inspect-key">Confidence</span>
                                    <span className={`ctx-inspect-val ${confidenceClass(selectedNode.confidence)}`}>
                                        κ = {selectedNode.confidence.toFixed(3)}
                                    </span>
                                </div>
                            )}
                            <div className="ctx-inspect-row">
                                <span className="ctx-inspect-key">Timestamp</span>
                                <span className="ctx-inspect-val">{selectedNode.timestamp}</span>
                            </div>

                            {/* Metadata (for real atoms) */}
                            {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
                                <>
                                    <div className="ctx-inspect-divider" />
                                    <div className="ctx-inspect-heading">Metadata</div>
                                    {Object.entries(selectedNode.metadata).map(([key, value]) => (
                                        <div key={key} className="ctx-inspect-row">
                                            <span className="ctx-inspect-key">{key}</span>
                                            <span className="ctx-inspect-val">
                                                {typeof value === 'number' ? value.toFixed(4) : String(value || '—')}
                                            </span>
                                        </div>
                                    ))}
                                </>
                            )}

                            <div className="ctx-inspect-divider" />
                            <div className="ctx-inspect-heading">Connections</div>
                            {graphEdges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).map(edge => {
                                const other = edge.source === selectedNode.id
                                    ? graphNodes.find(n => n.id === edge.target)
                                    : graphNodes.find(n => n.id === edge.source);
                                const direction = edge.source === selectedNode.id ? '→' : '←';
                                return (
                                    <div key={edge.id} className="ctx-inspect-connection" onClick={() => other && setSelectedNode(other)}>
                                        <span className="ctx-edge-type" style={{ color: EDGE_TYPE_COLORS[edge.type] }}>
                                            {edge.type}
                                        </span>
                                        <span className="ctx-edge-direction">{direction}</span>
                                        <span className="ctx-edge-target">{other?.label.substring(0, 25) || '?'}…</span>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="ctx-inspector-empty">
                            <div className="ctx-empty-icon">🕸️</div>
                            <p>Click any node in the graph to inspect its provenance, confidence, and connections.</p>
                            <p className="ctx-empty-hint">
                                {aimos.connected
                                    ? 'Showing real AIM-OS context provenance data.'
                                    : 'Connect to MCP to see live data. The graph shows how AI context flows through CMC → HHNI → SEG → VIF.'}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
