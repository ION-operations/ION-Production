import { useEffect, useRef, useState, useCallback } from 'react';
import { callTool } from '../services/mcpClient';
import { useAIMOS } from '../hooks/useAIMOS';

// ─── Types ───

interface AtlasNode {
    id: string;
    label: string;
    type: string;
    zoomMin: number;
    layer?: number;
    color?: string;
    description?: string;
    status?: string;
    systemId?: string;
    parent?: string;
    responsibility?: string;
    // Physics state
    x: number;
    y: number;
    vx: number;
    vy: number;
    fx?: number;
    fy?: number;
}

interface AtlasLink {
    source: string;
    target: string;
    type?: string;
    zoomMin: number;
    strength?: 'critical' | 'required' | 'optional' | 'related';
    category?: string;
    bidirectional?: boolean;
}

interface GraphData {
    nodes: AtlasNode[];
    links: AtlasLink[];
    metadata?: {
        systemsCount: number;
        subsystemsCount: number;
        internalNodesCount: number;
        docCount: number;
        fileCount: number;
        tagCount: number;
        funcCount: number;
        conceptCount: number;
        linksCount: number;
    };
}

type ZoomLevel = 0 | 1 | 2 | 3 | 4 | 5;

const ZOOM_LABELS: Record<ZoomLevel, string> = {
    0: 'Galaxy',
    1: 'Solar System',
    2: 'Planetary',
    3: 'Surface',
    4: 'Molecular',
    5: 'Atomic'
};

const ZOOM_ICONS: Record<ZoomLevel, string> = {
    0: '🌌',
    1: '☀️',
    2: '🪐',
    3: '🌍',
    4: '🔬',
    5: '⚛️'
};

// System layer colors matching the atlas
const LAYER_COLORS: Record<number, string> = {
    1: '#ff6b35',  // Memory & Knowledge — warm orange
    2: '#4ecdc4',  // Intelligence Processing — teal
    3: '#a855f7',  // Orchestration — purple
    4: '#f43f5e',  // Consciousness Engine — rose
    5: '#84cc16',  // Consciousness Infrastructure — lime
    6: '#38bdf8',  // Application & Integration — sky blue
};

const DEFAULT_NODE_COLOR = '#58a6ff';

// ─── Embedded AIM-OS Systems Data ───
// Core systems for when graph.json isn't available

const EMBEDDED_SYSTEMS: GraphData = {
    nodes: [
        // Layer 1: Memory & Knowledge
        { id: 'system:cmc', label: 'CMC', type: 'system', zoomMin: 0, layer: 1, color: '#ff6b35', description: 'Context Memory Core — Atom storage, snapshots, write/read pipelines', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:hhni', label: 'HHNI', type: 'system', zoomMin: 0, layer: 1, color: '#ff8a5c', description: 'Hierarchical Hypergraph Neural Index — 6-level hierarchy, DVNS physics', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:seg', label: 'SEG', type: 'system', zoomMin: 0, layer: 1, color: '#ffb088', description: 'Shared Evidence Graph — Contradiction detection, knowledge synthesis', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },

        // Layer 2: Intelligence Processing
        { id: 'system:vif', label: 'VIF', type: 'system', zoomMin: 0, layer: 2, color: '#4ecdc4', description: 'Verifiable Intelligence Framework — Confidence tracking, witnesses, provenance', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:sdfcvf', label: 'SDFCVF', type: 'system', zoomMin: 0, layer: 2, color: '#7eddd6', description: 'Atomic Evolution Framework — Quartet validation, blast radius, DORA metrics', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },

        // Layer 3: Orchestration
        { id: 'system:apoe', label: 'APOE', type: 'system', zoomMin: 0, layer: 3, color: '#a855f7', description: 'AI-Powered Orchestration Engine — ACL compiler, DAG executor, 8 roles', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },

        // Layer 4: Consciousness Engine
        { id: 'system:cas', label: 'CAS', type: 'system', zoomMin: 0, layer: 4, color: '#f43f5e', description: 'Cognitive Analysis System — Attention, failure detection, introspection', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:iis', label: 'IIS', type: 'system', zoomMin: 0, layer: 4, color: '#fb7185', description: 'Intuitive Intelligence System — Pattern recognition, meta-analysis', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:tcs', label: 'TCS', type: 'system', zoomMin: 0, layer: 4, color: '#fda4af', description: 'Timeline Context System — Temporal tracking, consciousness journal', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },

        // Layer 5: Infrastructure
        { id: 'system:intent', label: 'Intent', type: 'system', zoomMin: 0, layer: 5, color: '#84cc16', description: 'Intent Classification — Pattern matching, risk assessment', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:scor', label: 'SCOR', type: 'system', zoomMin: 0, layer: 5, color: '#a3e635', description: 'Safety Consciousness — Invariant checking, baseline probes, red cell sim', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },

        // Layer 6: Application
        { id: 'system:joc', label: 'JOC', type: 'system', zoomMin: 0, layer: 6, color: '#38bdf8', description: 'Joint Operations Center — AI cockpit, fleet, missions, code editor', status: 'active', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'system:console', label: 'Console', type: 'system', zoomMin: 0, layer: 6, color: '#7dd3fc', description: 'Lucid Core Console — Voice I/O, RPC, Gemini integration', status: 'production', x: 0, y: 0, vx: 0, vy: 0 },

        // Subsystems (Z1)
        { id: 'sub:cmc:atoms', label: 'Atom Manager', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff6b35', systemId: 'cmc', parent: 'system:cmc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cmc:write', label: 'Write Pipeline', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff6b35', systemId: 'cmc', parent: 'system:cmc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cmc:read', label: 'Read Pipeline', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff6b35', systemId: 'cmc', parent: 'system:cmc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cmc:storage', label: 'Storage Manager', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff6b35', systemId: 'cmc', parent: 'system:cmc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cmc:snapshot', label: 'Snapshot Engine', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff6b35', systemId: 'cmc', parent: 'system:cmc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:hhni:index', label: 'Hierarchical Index', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff8a5c', systemId: 'hhni', parent: 'system:hhni', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:hhni:dvns', label: 'DVNS Physics', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff8a5c', systemId: 'hhni', parent: 'system:hhni', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:hhni:retrieval', label: 'Coarse Retrieval', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ff8a5c', systemId: 'hhni', parent: 'system:hhni', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:seg:graph', label: 'Graph Builder', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ffb088', systemId: 'seg', parent: 'system:seg', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:seg:contradict', label: 'Contradiction Detector', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ffb088', systemId: 'seg', parent: 'system:seg', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:seg:synth', label: 'Knowledge Synthesizer', type: 'subsystem', zoomMin: 1, layer: 1, color: '#ffb088', systemId: 'seg', parent: 'system:seg', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:vif:confidence', label: 'Confidence Tracker', type: 'subsystem', zoomMin: 1, layer: 2, color: '#4ecdc4', systemId: 'vif', parent: 'system:vif', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:vif:witness', label: 'Witness Manager', type: 'subsystem', zoomMin: 1, layer: 2, color: '#4ecdc4', systemId: 'vif', parent: 'system:vif', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:vif:provenance', label: 'Provenance Engine', type: 'subsystem', zoomMin: 1, layer: 2, color: '#4ecdc4', systemId: 'vif', parent: 'system:vif', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:apoe:acl', label: 'ACL Compiler', type: 'subsystem', zoomMin: 1, layer: 3, color: '#a855f7', systemId: 'apoe', parent: 'system:apoe', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:apoe:dag', label: 'DAG Executor', type: 'subsystem', zoomMin: 1, layer: 3, color: '#a855f7', systemId: 'apoe', parent: 'system:apoe', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:apoe:roles', label: 'Role Dispatcher', type: 'subsystem', zoomMin: 1, layer: 3, color: '#a855f7', systemId: 'apoe', parent: 'system:apoe', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cas:attention', label: 'Attention Monitor', type: 'subsystem', zoomMin: 1, layer: 4, color: '#f43f5e', systemId: 'cas', parent: 'system:cas', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cas:failure', label: 'Failure Detector', type: 'subsystem', zoomMin: 1, layer: 4, color: '#f43f5e', systemId: 'cas', parent: 'system:cas', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:cas:introspect', label: 'Introspection', type: 'subsystem', zoomMin: 1, layer: 4, color: '#f43f5e', systemId: 'cas', parent: 'system:cas', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:tcs:timeline', label: 'Timeline Tracker', type: 'subsystem', zoomMin: 1, layer: 4, color: '#fda4af', systemId: 'tcs', parent: 'system:tcs', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:tcs:journal', label: 'Consciousness Journal', type: 'subsystem', zoomMin: 1, layer: 4, color: '#fda4af', systemId: 'tcs', parent: 'system:tcs', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:joc:fleet', label: 'AI Fleet', type: 'subsystem', zoomMin: 1, layer: 6, color: '#38bdf8', systemId: 'joc', parent: 'system:joc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:joc:missions', label: 'Missions', type: 'subsystem', zoomMin: 1, layer: 6, color: '#38bdf8', systemId: 'joc', parent: 'system:joc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:joc:editor', label: 'Code Editor', type: 'subsystem', zoomMin: 1, layer: 6, color: '#38bdf8', systemId: 'joc', parent: 'system:joc', x: 0, y: 0, vx: 0, vy: 0 },
        { id: 'sub:joc:atlas', label: 'System Atlas', type: 'subsystem', zoomMin: 1, layer: 6, color: '#38bdf8', systemId: 'joc', parent: 'system:joc', x: 0, y: 0, vx: 0, vy: 0 },
    ],
    links: [
        // Critical inter-system connections
        { source: 'system:cmc', target: 'system:hhni', zoomMin: 0, strength: 'critical', category: 'provides_to', bidirectional: true },
        { source: 'system:cmc', target: 'system:seg', zoomMin: 0, strength: 'critical', category: 'provides_to', bidirectional: true },
        { source: 'system:cmc', target: 'system:vif', zoomMin: 0, strength: 'critical', category: 'provides_to', bidirectional: true },
        { source: 'system:cmc', target: 'system:apoe', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:hhni', target: 'system:apoe', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:hhni', target: 'system:vif', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:seg', target: 'system:hhni', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:seg', target: 'system:vif', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:vif', target: 'system:apoe', zoomMin: 0, strength: 'critical', category: 'provides_to', bidirectional: true },
        { source: 'system:cas', target: 'system:apoe', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:cas', target: 'system:vif', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:cas', target: 'system:cmc', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:iis', target: 'system:cas', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:iis', target: 'system:vif', zoomMin: 0, strength: 'optional', category: 'provides_to', bidirectional: true },
        { source: 'system:tcs', target: 'system:cmc', zoomMin: 0, strength: 'critical', category: 'provides_to', bidirectional: true },
        { source: 'system:tcs', target: 'system:cas', zoomMin: 0, strength: 'required', category: 'provides_to', bidirectional: true },
        { source: 'system:intent', target: 'system:apoe', zoomMin: 0, strength: 'required', category: 'provides_to' },
        { source: 'system:intent', target: 'system:cmc', zoomMin: 0, strength: 'required', category: 'provides_to' },
        { source: 'system:scor', target: 'system:cas', zoomMin: 0, strength: 'critical', category: 'provides_to' },
        { source: 'system:scor', target: 'system:apoe', zoomMin: 0, strength: 'required', category: 'provides_to' },
        { source: 'system:joc', target: 'system:cmc', zoomMin: 0, strength: 'critical', category: 'depends_on' },
        { source: 'system:joc', target: 'system:apoe', zoomMin: 0, strength: 'critical', category: 'depends_on' },
        { source: 'system:joc', target: 'system:tcs', zoomMin: 0, strength: 'required', category: 'depends_on' },
        { source: 'system:console', target: 'system:cmc', zoomMin: 0, strength: 'critical', category: 'depends_on' },
        { source: 'system:console', target: 'system:intent', zoomMin: 0, strength: 'required', category: 'depends_on' },
        // Subsystem links
        { source: 'sub:cmc:write', target: 'sub:cmc:atoms', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:cmc:atoms', target: 'sub:cmc:snapshot', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:cmc:snapshot', target: 'sub:cmc:storage', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:cmc:read', target: 'sub:cmc:storage', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:hhni:index', target: 'sub:hhni:retrieval', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:hhni:dvns', target: 'sub:hhni:retrieval', zoomMin: 1, strength: 'required', category: 'provides_to' },
        { source: 'sub:seg:graph', target: 'sub:seg:contradict', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:seg:contradict', target: 'sub:seg:synth', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:apoe:acl', target: 'sub:apoe:dag', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:apoe:dag', target: 'sub:apoe:roles', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:vif:confidence', target: 'sub:vif:witness', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:vif:witness', target: 'sub:vif:provenance', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:cas:attention', target: 'sub:cas:failure', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:cas:failure', target: 'sub:cas:introspect', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:tcs:timeline', target: 'sub:tcs:journal', zoomMin: 1, strength: 'critical', category: 'provides_to' },
        { source: 'sub:joc:fleet', target: 'sub:joc:missions', zoomMin: 1, strength: 'required', category: 'provides_to' },
        { source: 'sub:joc:editor', target: 'sub:joc:atlas', zoomMin: 1, strength: 'optional', category: 'related' },
    ],
    metadata: {
        systemsCount: 13, subsystemsCount: 24, internalNodesCount: 0,
        docCount: 0, fileCount: 0, tagCount: 0, funcCount: 0, conceptCount: 0, linksCount: 41
    }
};

// ─── Force Simulation ───

function initializePositions(nodes: AtlasNode[], width: number, height: number) {
    const cx = width / 2;
    const cy = height / 2;
    // Arrange by layer in concentric rings
    const layerGroups: Record<number, AtlasNode[]> = {};
    nodes.forEach(n => {
        const layer = n.layer || 0;
        if (!layerGroups[layer]) layerGroups[layer] = [];
        layerGroups[layer].push(n);
    });

    const layerKeys = Object.keys(layerGroups).map(Number).sort();
    const maxRadius = Math.min(width, height) * 0.38;

    layerKeys.forEach((layer, li) => {
        const radius = (maxRadius * (li + 1)) / (layerKeys.length + 0.5);
        const group = layerGroups[layer];
        group.forEach((node, ni) => {
            const angle = (2 * Math.PI * ni) / group.length - Math.PI / 2;
            node.x = cx + radius * Math.cos(angle) + (Math.random() - 0.5) * 20;
            node.y = cy + radius * Math.sin(angle) + (Math.random() - 0.5) * 20;
            node.vx = 0;
            node.vy = 0;
        });
    });
}

function simulateForces(
    nodes: AtlasNode[],
    links: AtlasLink[],
    width: number,
    height: number,
    alpha: number
) {
    const cx = width / 2;
    const cy = height / 2;
    const nodeMap = new Map<string, AtlasNode>();
    nodes.forEach(n => nodeMap.set(n.id, n));
    const N = nodes.length;

    // Center gravity
    nodes.forEach(n => {
        n.vx += (cx - n.x) * 0.001 * alpha;
        n.vy += (cy - n.y) * 0.001 * alpha;
    });

    // Optimized repulsion: use spatial hash for large graphs
    if (N > 200) {
        // Grid-based spatial hashing — O(n·k) instead of O(n²)
        const cellSize = 80;
        const grid = new Map<string, AtlasNode[]>();
        nodes.forEach(n => {
            const key = `${Math.floor(n.x / cellSize)},${Math.floor(n.y / cellSize)}`;
            if (!grid.has(key)) grid.set(key, []);
            grid.get(key)!.push(n);
        });
        nodes.forEach(a => {
            const gx = Math.floor(a.x / cellSize);
            const gy = Math.floor(a.y / cellSize);
            for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                    const neighbors = grid.get(`${gx + dx},${gy + dy}`);
                    if (!neighbors) continue;
                    for (const b of neighbors) {
                        if (a === b) continue;
                        let ddx = b.x - a.x;
                        let ddy = b.y - a.y;
                        const dist = Math.sqrt(ddx * ddx + ddy * ddy) || 1;
                        if (dist > cellSize * 2) continue;
                        const strength = a.type === 'system' ? 600 : 150;
                        const force = strength * alpha / (dist * dist);
                        ddx /= dist; ddy /= dist;
                        a.vx -= ddx * force;
                        a.vy -= ddy * force;
                    }
                }
            }
        });
    } else {
        // O(n²) is fine for small graphs
        for (let i = 0; i < N; i++) {
            for (let j = i + 1; j < N; j++) {
                const a = nodes[i], b = nodes[j];
                let dx = b.x - a.x;
                let dy = b.y - a.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = (a.type === 'system' ? 800 : 200) * alpha / (dist * dist);
                dx /= dist; dy /= dist;
                a.vx -= dx * force;
                a.vy -= dy * force;
                b.vx += dx * force;
                b.vy += dy * force;
            }
        }
    }

    // Link attraction
    links.forEach(link => {
        const source = nodeMap.get(link.source);
        const target = nodeMap.get(link.target);
        if (!source || !target) return;
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const idealDist = link.strength === 'critical' ? 100 : link.strength === 'required' ? 140 : 180;
        const force = (dist - idealDist) * 0.005 * alpha;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        source.vx += fx;
        source.vy += fy;
        target.vx -= fx;
        target.vy -= fy;
    });

    // Parent-child attraction (subsystems cluster near their parent)
    nodes.forEach(n => {
        if (n.parent) {
            const parent = nodeMap.get(n.parent);
            if (parent) {
                const dx = parent.x - n.x;
                const dy = parent.y - n.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = (dist - 60) * 0.02 * alpha;
                n.vx += (dx / dist) * force;
                n.vy += (dy / dist) * force;
            }
        }
    });

    // Velocity damping + position update
    nodes.forEach(n => {
        if (n.fx !== undefined) { n.x = n.fx; n.vx = 0; }
        else {
            n.vx *= 0.6;
            n.x += n.vx;
            n.x = Math.max(30, Math.min(width - 30, n.x));
        }
        if (n.fy !== undefined) { n.y = n.fy; n.vy = 0; }
        else {
            n.vy *= 0.6;
            n.y += n.vy;
            n.y = Math.max(30, Math.min(height - 30, n.y));
        }
    });
}

// ─── Component ───

export function SystemAtlas() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [graphData, setGraphData] = useState<GraphData>(EMBEDDED_SYSTEMS);
    const [zoomLevel, setZoomLevel] = useState<ZoomLevel>(0);
    const [selectedNode, setSelectedNode] = useState<AtlasNode | null>(null);
    const [hoveredNode, setHoveredNode] = useState<AtlasNode | null>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [isSimulating, setIsSimulating] = useState(true);
    const [dataSource, setDataSource] = useState<'embedded' | 'loaded'>('embedded');
    const [isLoading, setIsLoading] = useState(false);
    const [totalNodes, setTotalNodes] = useState(0);
    const [totalLinks, setTotalLinks] = useState(0);
    const alphaRef = useRef(1.0);
    const frameRef = useRef<number>(0);
    const dragRef = useRef<{ node: AtlasNode | null; offsetX: number; offsetY: number }>({ node: null, offsetX: 0, offsetY: 0 });

    // ─── Live MCP Data ───
    const aimos = useAIMOS({
        pollDomains: ['memory', 'consciousness', 'goals', 'problems', 'timeline'],
        pollInterval: 15000,
    });

    // Build real-time health map for system nodes (stored in ref to avoid render cycles)
    const healthMapRef = useRef<Map<string, { intensity: number; pulseSpeed: number; statusColor: string }>>(new Map());

    useEffect(() => {
        const hm = new Map<string, { intensity: number; pulseSpeed: number; statusColor: string }>();

        // Default: all systems get baseline glow when MCP is connected
        const base = aimos.connected ? 0.3 : 0.0;

        // CMC — driven by atom count
        const atomCount = aimos.memory?.total_atoms || 0;
        hm.set('system:cmc', {
            intensity: atomCount > 100 ? 0.9 : atomCount > 10 ? 0.6 : base,
            pulseSpeed: atomCount > 100 ? 400 : 800,
            statusColor: atomCount > 0 ? '#a3e635' : '#ef4444',
        });

        // HHNI — driven by memory total (indexed atoms)
        hm.set('system:hhni', {
            intensity: atomCount > 50 ? 0.8 : atomCount > 5 ? 0.5 : base,
            pulseSpeed: 600,
            statusColor: atomCount > 0 ? '#22d3ee' : '#666',
        });

        // SEG — driven by memory molecules (evidence synthesis)
        const molecules = aimos.memory?.total_molecules || 0;
        hm.set('system:seg', {
            intensity: molecules > 5 ? 0.7 : molecules > 0 ? 0.4 : base,
            pulseSpeed: 700,
            statusColor: molecules > 0 ? '#f472b6' : '#666',
        });

        // VIF — driven by last latency (proxy for verification freshness)
        const freshVIF = aimos.latency > 0 && aimos.latency < 2000;
        hm.set('system:vif', {
            intensity: freshVIF ? 0.7 : base,
            pulseSpeed: 500,
            statusColor: freshVIF ? '#4ecdc4' : '#666',
        });

        // CAS — driven by cognitive drift (lower is better)
        const drift = aimos.consciousness?.cognitive_drift;
        hm.set('system:cas', {
            intensity: drift !== undefined ? (drift < 0.3 ? 0.8 : drift < 0.6 ? 0.5 : 0.3) : base,
            pulseSpeed: drift !== undefined ? (drift < 0.3 ? 900 : 400) : 800,
            statusColor: drift !== undefined ? (drift < 0.3 ? '#a3e635' : drift < 0.6 ? '#fb923c' : '#ef4444') : '#666',
        });

        // IIS — driven by attention load
        const attention = aimos.consciousness?.attention_load;
        hm.set('system:iis', {
            intensity: attention !== undefined ? 0.5 : base,
            pulseSpeed: 700,
            statusColor: attention !== undefined ? '#fb7185' : '#666',
        });

        // TCS — driven by timeline entry count
        const timelineCount = aimos.timeline.length;
        hm.set('system:tcs', {
            intensity: timelineCount > 10 ? 0.8 : timelineCount > 0 ? 0.5 : base,
            pulseSpeed: 600,
            statusColor: timelineCount > 0 ? '#fda4af' : '#666',
        });

        // APOE — driven by goals (active plans)
        const goalCount = aimos.goals.length;
        hm.set('system:apoe', {
            intensity: goalCount > 3 ? 0.7 : goalCount > 0 ? 0.4 : base,
            pulseSpeed: 800,
            statusColor: goalCount > 0 ? '#a855f7' : '#666',
        });

        // JOC — always active (we ARE the JOC)
        hm.set('system:joc', {
            intensity: 0.9,
            pulseSpeed: 600,
            statusColor: '#38bdf8',
        });

        // SCOR — driven by problem count (safety)
        const problemCount = (aimos.problems?.errors || 0) + (aimos.problems?.warnings || 0);
        hm.set('system:scor', {
            intensity: problemCount > 0 ? 0.6 : base,
            pulseSpeed: problemCount > 5 ? 300 : 700,
            statusColor: problemCount === 0 ? '#a3e635' : problemCount < 5 ? '#fb923c' : '#ef4444',
        });

        // Intent — baseline
        hm.set('system:intent', { intensity: base, pulseSpeed: 800, statusColor: aimos.connected ? '#84cc16' : '#666' });
        // Console — baseline
        hm.set('system:console', { intensity: base, pulseSpeed: 800, statusColor: aimos.connected ? '#7dd3fc' : '#666' });
        // SDFCVF — baseline
        hm.set('system:sdfcvf', { intensity: base, pulseSpeed: 800, statusColor: aimos.connected ? '#7eddd6' : '#666' });

        healthMapRef.current = hm;
    }, [aimos.connected, aimos.memory, aimos.consciousness, aimos.timeline, aimos.goals, aimos.problems, aimos.latency]);

    // ─── Context Web State ───
    const [knowledgeTab, setKnowledgeTab] = useState<'memory' | 'evidence' | 'confidence' | null>(null);
    const [knowledgeData, setKnowledgeData] = useState<any>(null);
    const [knowledgeLoading, setKnowledgeLoading] = useState(false);

    const fetchKnowledge = useCallback(async (tab: 'memory' | 'evidence' | 'confidence', node: AtlasNode) => {
        setKnowledgeTab(tab);
        setKnowledgeLoading(true);
        setKnowledgeData(null);
        try {
            if (tab === 'memory') {
                const result = await callTool<any>('retrieve_memory', {
                    query: `${node.label} ${node.systemId || ''} ${node.description || ''}`.trim(),
                    limit: 8
                });
                setKnowledgeData({ memories: result?.memories || result?.results || (Array.isArray(result) ? result : []) });
            } else if (tab === 'evidence') {
                const result = await callTool<any>('synthesize_knowledge', {
                    topics: [node.label, node.systemId || node.id].filter(Boolean),
                    depth: 'medium',
                    format: 'summary'
                });
                setKnowledgeData({ synthesis: result?.synthesis || result?.summary || result });
            } else if (tab === 'confidence') {
                const result = await callTool<any>('track_confidence', {
                    task: `${node.label} system assessment`,
                    confidence: 0.5,
                    reasoning: `Assessing ${node.label} in AIM-OS architecture`,
                    evidence: [`System type: ${node.type}`, `Status: ${node.status || 'unknown'}`]
                });
                setKnowledgeData({
                    confidence: result?.confidence ?? result?.score ?? 0.5,
                    reasoning: result?.reasoning || result?.assessment || `VIF assessment for ${node.label}`,
                    evidence: result?.evidence || []
                });
            }
        } catch (err) {
            console.warn('[ContextWeb] MCP query failed:', err);
            if (tab === 'memory') setKnowledgeData({ memories: [] });
            else if (tab === 'evidence') setKnowledgeData({ synthesis: null });
            else setKnowledgeData({ confidence: undefined });
        } finally {
            setKnowledgeLoading(false);
        }
    }, []);

    // Try to load external graph.json
    useEffect(() => {
        setIsLoading(true);
        fetch('/data/graph.json')
            .then(r => { if (!r.ok) throw new Error('not found'); return r.json(); })
            .then((data: GraphData) => {
                data.nodes.forEach(n => { n.x = 0; n.y = 0; n.vx = 0; n.vy = 0; });
                setTotalNodes(data.nodes.length);
                setTotalLinks(data.links.length);
                setGraphData(data);
                setDataSource('loaded');
                alphaRef.current = 1.0;
                setIsLoading(false);
            })
            .catch(() => {
                setTotalNodes(EMBEDDED_SYSTEMS.nodes.length);
                setTotalLinks(EMBEDDED_SYSTEMS.links.length);
                setDataSource('embedded');
                setIsLoading(false);
            });
    }, []);

    // Resize observer
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;
        const observer = new ResizeObserver(entries => {
            const entry = entries[0];
            if (entry) {
                const { width, height } = entry.contentRect;
                setDimensions({ width: Math.floor(width), height: Math.floor(height) });
            }
        });
        observer.observe(container);
        return () => observer.disconnect();
    }, []);

    // Initialize positions when data or dimensions change
    useEffect(() => {
        if (dimensions.width > 0 && dimensions.height > 0) {
            initializePositions(graphData.nodes, dimensions.width, dimensions.height);
            alphaRef.current = 1.0;
            setIsSimulating(true);
        }
    }, [graphData, dimensions.width, dimensions.height]);

    // Filter by zoom
    const filteredNodes = graphData.nodes.filter(n => (n.zoomMin ?? 0) <= zoomLevel);
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = graphData.links.filter(
        l => filteredNodeIds.has(l.source) && filteredNodeIds.has(l.target) && (l.zoomMin ?? 0) <= zoomLevel
    );

    // Animation + rendering loop
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        canvas.width = dimensions.width * window.devicePixelRatio;
        canvas.height = dimensions.height * window.devicePixelRatio;
        canvas.style.width = dimensions.width + 'px';
        canvas.style.height = dimensions.height + 'px';
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        const nodeMap = new Map<string, AtlasNode>();
        filteredNodes.forEach(n => nodeMap.set(n.id, n));

        function render() {
            if (!ctx) return;
            const { width, height } = dimensions;

            // Run physics
            if (alphaRef.current > 0.001) {
                simulateForces(filteredNodes, filteredLinks, width, height, alphaRef.current);
                alphaRef.current *= 0.995;
            } else {
                if (isSimulating) setIsSimulating(false);
            }

            // Clear
            ctx.clearRect(0, 0, width, height);

            // Background gradient
            const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, width * 0.7);
            bgGrad.addColorStop(0, '#0d1220');
            bgGrad.addColorStop(0.5, '#0a0f1a');
            bgGrad.addColorStop(1, '#060a12');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, width, height);

            // Subtle grid
            ctx.strokeStyle = 'rgba(88, 166, 255, 0.03)';
            ctx.lineWidth = 0.5;
            for (let x = 0; x < width; x += 40) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
            }
            for (let y = 0; y < height; y += 40) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
            }

            // Draw links
            filteredLinks.forEach(link => {
                const source = nodeMap.get(link.source);
                const target = nodeMap.get(link.target);
                if (!source || !target) return;

                ctx.beginPath();
                ctx.moveTo(source.x, source.y);
                ctx.lineTo(target.x, target.y);

                // Style by strength
                const isHovered = hoveredNode && (link.source === hoveredNode.id || link.target === hoveredNode.id);
                const isSelected = selectedNode && (link.source === selectedNode.id || link.target === selectedNode.id);

                if (isSelected) {
                    ctx.strokeStyle = source.color || DEFAULT_NODE_COLOR;
                    ctx.lineWidth = 2.5;
                    ctx.globalAlpha = 0.9;
                } else if (isHovered) {
                    ctx.strokeStyle = source.color || DEFAULT_NODE_COLOR;
                    ctx.lineWidth = 1.5;
                    ctx.globalAlpha = 0.7;
                } else {
                    ctx.lineWidth = link.strength === 'critical' ? 1.5 : link.strength === 'required' ? 1 : 0.5;
                    ctx.globalAlpha = link.strength === 'critical' ? 0.3 : link.strength === 'required' ? 0.2 : 0.1;
                    ctx.strokeStyle = link.category === 'partOf' || link.category === 'contains' ? '#484f58' : source.color || '#30363d';
                }

                if (link.strength === 'optional' || link.strength === 'related') {
                    ctx.setLineDash([4, 4]);
                } else {
                    ctx.setLineDash([]);
                }

                ctx.stroke();
                ctx.globalAlpha = 1;
                ctx.setLineDash([]);

                // Arrow for directed links
                if (!link.bidirectional && (isSelected || isHovered)) {
                    const angle = Math.atan2(target.y - source.y, target.x - source.x);
                    const dist = Math.sqrt((target.x - source.x) ** 2 + (target.y - source.y) ** 2);
                    const headSize = target.type === 'system' ? 16 : 10;
                    const arrowX = source.x + (dist - headSize) * Math.cos(angle);
                    const arrowY = source.y + (dist - headSize) * Math.sin(angle);
                    ctx.beginPath();
                    ctx.moveTo(arrowX, arrowY);
                    ctx.lineTo(arrowX - 8 * Math.cos(angle - 0.4), arrowY - 8 * Math.sin(angle - 0.4));
                    ctx.lineTo(arrowX - 8 * Math.cos(angle + 0.4), arrowY - 8 * Math.sin(angle + 0.4));
                    ctx.closePath();
                    ctx.fillStyle = source.color || DEFAULT_NODE_COLOR;
                    ctx.globalAlpha = 0.6;
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
            });

            // Draw nodes
            filteredNodes.forEach(node => {
                const isHovered = hoveredNode?.id === node.id;
                const isSelected = selectedNode?.id === node.id;
                const isConnected = selectedNode && filteredLinks.some(
                    l => (l.source === selectedNode.id && l.target === node.id) ||
                        (l.target === selectedNode.id && l.source === node.id)
                );
                const color = node.color || LAYER_COLORS[node.layer || 0] || DEFAULT_NODE_COLOR;
                const radius = node.type === 'system' ? 14 : node.type === 'subsystem' ? 8 : 5;

                // Glow effect for system nodes — now driven by live MCP health data
                if (node.type === 'system') {
                    const health = healthMapRef.current.get(node.id);
                    const liveIntensity = health?.intensity || 0;
                    const pulseSpeed = health?.pulseSpeed || 800;
                    const statusColor = health?.statusColor;

                    // Live health pulse ring (outermost) — only when MCP is connected
                    if (liveIntensity > 0) {
                        const liveGlowRadius = 28 + Math.sin(Date.now() / pulseSpeed) * 6 * liveIntensity;
                        const liveGrad = ctx.createRadialGradient(node.x, node.y, radius, node.x, node.y, liveGlowRadius);
                        liveGrad.addColorStop(0, (statusColor || color) + Math.round(liveIntensity * 80).toString(16).padStart(2, '0'));
                        liveGrad.addColorStop(1, 'transparent');
                        ctx.fillStyle = liveGrad;
                        ctx.beginPath();
                        ctx.arc(node.x, node.y, liveGlowRadius, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    // Standard glow
                    const glowRadius = isSelected ? 35 : isHovered ? 28 : 22;
                    const glowGrad = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, glowRadius);
                    glowGrad.addColorStop(0, color + (isSelected ? '50' : isHovered ? '35' : '20'));
                    glowGrad.addColorStop(1, 'transparent');
                    ctx.fillStyle = glowGrad;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2);
                    ctx.fill();

                    // Status dot indicator (small dot at top-right of node)
                    if (statusColor && liveIntensity > 0) {
                        ctx.beginPath();
                        ctx.arc(node.x + radius * 0.8, node.y - radius * 0.8, 3, 0, Math.PI * 2);
                        ctx.fillStyle = statusColor;
                        ctx.fill();
                        ctx.strokeStyle = '#0a0f1a';
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }

                // Node circle
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);

                // Dimming when something is selected
                if (selectedNode && !isSelected && !isConnected) {
                    ctx.globalAlpha = 0.25;
                }

                // Fill
                const nodeGrad = ctx.createRadialGradient(
                    node.x - radius * 0.3, node.y - radius * 0.3, 0,
                    node.x, node.y, radius
                );
                nodeGrad.addColorStop(0, color);
                nodeGrad.addColorStop(1, color + 'aa');
                ctx.fillStyle = nodeGrad;
                ctx.fill();

                // Ring
                if (isSelected) {
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2.5;
                } else if (isHovered) {
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1.5;
                } else {
                    ctx.strokeStyle = color + '80';
                    ctx.lineWidth = 1;
                }
                ctx.stroke();
                ctx.globalAlpha = 1;

                // All system nodes get a live pulse ring when MCP is connected
                if (node.type === 'system' && !isSelected) {
                    const health = healthMapRef.current.get(node.id);
                    const speed = health?.pulseSpeed || 600;
                    const intensity = health?.intensity || 0;
                    if (intensity > 0.2) {
                        const pulseRadiusAnim = 18 + Math.sin(Date.now() / speed) * 4 * intensity;
                        ctx.beginPath();
                        ctx.arc(node.x, node.y, pulseRadiusAnim, 0, Math.PI * 2);
                        ctx.strokeStyle = (health?.statusColor || color) + Math.round(intensity * 64).toString(16).padStart(2, '0');
                        ctx.lineWidth = 1.5;
                        ctx.stroke();
                    }
                }

                // Label
                if (selectedNode && !isSelected && !isConnected) {
                    ctx.globalAlpha = 0.2;
                }
                // Skip labels for tiny nodes when many visible (performance)
                const showLabel = node.type === 'system' || node.type === 'subsystem' || filteredNodes.length < 100;
                if (!showLabel) { ctx.globalAlpha = 1; return; }
                ctx.font = node.type === 'system'
                    ? 'bold 11px system-ui, -apple-system, sans-serif'
                    : '9px system-ui, -apple-system, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillStyle = isSelected || isHovered ? '#ffffff' : '#c0c8d4';
                ctx.fillText(node.label, node.x, node.y + radius + 4);
                ctx.globalAlpha = 1;
            });

            // Tooltip for hovered node
            if (hoveredNode && !selectedNode) {
                const tooltipX = hoveredNode.x + 20;
                const tooltipY = hoveredNode.y - 10;
                const text = hoveredNode.description || hoveredNode.label;
                ctx.font = '10px system-ui, -apple-system, sans-serif';
                const textWidth = ctx.measureText(text).width;
                const padding = 8;

                ctx.fillStyle = 'rgba(13, 17, 27, 0.95)';
                ctx.strokeStyle = (hoveredNode.color || DEFAULT_NODE_COLOR) + '60';
                ctx.lineWidth = 1;
                const rx = tooltipX - padding;
                const ry = tooltipY - padding;
                const rw = textWidth + padding * 2;
                const rh = 14 + padding * 2;
                ctx.beginPath();
                ctx.roundRect(rx, ry, rw, rh, 4);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = '#e0e0e0';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';
                ctx.fillText(text, tooltipX, tooltipY);

                if (hoveredNode.type === 'system') {
                    const layerLabel = `Layer ${hoveredNode.layer}`;
                    ctx.font = '8px system-ui, -apple-system, sans-serif';
                    ctx.fillStyle = hoveredNode.color || DEFAULT_NODE_COLOR;
                    ctx.fillText(layerLabel, tooltipX, tooltipY + 14);
                }
            }

            frameRef.current = requestAnimationFrame(render);
        }

        frameRef.current = requestAnimationFrame(render);
        return () => cancelAnimationFrame(frameRef.current);
    }, [filteredNodes, filteredLinks, dimensions, hoveredNode, selectedNode, isSimulating]);

    // Mouse interaction
    const findNodeAtPosition = useCallback((mx: number, my: number): AtlasNode | null => {
        for (let i = filteredNodes.length - 1; i >= 0; i--) {
            const n = filteredNodes[i];
            const radius = n.type === 'system' ? 14 : n.type === 'subsystem' ? 8 : 5;
            const dx = mx - n.x;
            const dy = my - n.y;
            if (dx * dx + dy * dy <= (radius + 4) * (radius + 4)) {
                return n;
            }
        }
        return null;
    }, [filteredNodes]);

    const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        if (dragRef.current.node) {
            dragRef.current.node.fx = mx;
            dragRef.current.node.fy = my;
            alphaRef.current = Math.max(alphaRef.current, 0.1);
            canvas.style.cursor = 'grabbing';
            return;
        }

        const node = findNodeAtPosition(mx, my);
        setHoveredNode(node);
        canvas.style.cursor = node ? 'pointer' : 'default';
    }, [findNodeAtPosition]);

    const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const node = findNodeAtPosition(mx, my);
        if (node) {
            dragRef.current = { node, offsetX: mx - node.x, offsetY: my - node.y };
            node.fx = mx;
            node.fy = my;
        }
    }, [findNodeAtPosition]);

    const handleMouseUp = useCallback(() => {
        if (dragRef.current.node) {
            const node = dragRef.current.node;
            // If barely moved, treat as click
            delete node.fx;
            delete node.fy;
            dragRef.current = { node: null, offsetX: 0, offsetY: 0 };
        }
    }, []);

    const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const node = findNodeAtPosition(mx, my);
        setSelectedNode(prev => prev?.id === node?.id ? null : node || null);
    }, [findNodeAtPosition]);

    // Count stats
    const systemsVisible = filteredNodes.filter(n => n.type === 'system').length;
    const subsystemsVisible = filteredNodes.filter(n => n.type === 'subsystem').length;
    const internalVisible = filteredNodes.filter(n => n.type === 'internalNode').length;
    const linksVisible = filteredLinks.length;

    return (
        <div className="atlas-container" ref={containerRef}>
            {/* Header Bar */}
            <div className="atlas-header">
                <div className="atlas-header-left">
                    <span className="atlas-title">
                        <span className="atlas-title-icon">🌌</span>
                        System Atlas
                    </span>
                    <span className="atlas-subtitle">AIM-OS Architecture Map</span>
                </div>
                <div className="atlas-header-center">
                    <div className="atlas-zoom-controller">
                        {([0, 1, 2, 3, 4, 5] as ZoomLevel[]).map(z => (
                            <button
                                key={z}
                                className={`atlas-zoom-btn ${z === zoomLevel ? 'active' : ''} ${z <= zoomLevel ? 'visible' : ''}`}
                                onClick={() => { setZoomLevel(z); alphaRef.current = 0.5; setIsSimulating(true); }}
                                title={`Z${z}: ${ZOOM_LABELS[z]}`}
                            >
                                <span className="atlas-zoom-icon">{ZOOM_ICONS[z]}</span>
                                <span className="atlas-zoom-label">Z{z}</span>
                            </button>
                        ))}
                    </div>
                </div>
                <div className="atlas-header-right">
                    <span className="atlas-stat">{systemsVisible} systems</span>
                    <span className="atlas-stat-sep">·</span>
                    <span className="atlas-stat">{subsystemsVisible} subs</span>
                    {internalVisible > 0 && <><span className="atlas-stat-sep">·</span><span className="atlas-stat">{internalVisible} nodes</span></>}
                    <span className="atlas-stat-sep">·</span>
                    <span className="atlas-stat">{linksVisible} links</span>
                    {totalNodes > 0 && <><span className="atlas-stat-sep">·</span><span className="atlas-stat" style={{ color: '#4ecdc4' }}>{totalNodes} total</span></>}
                    <span className="atlas-stat-sep">·</span>
                    <span className={`atlas-data-badge ${dataSource}`}>
                        {dataSource === 'loaded' ? '📡 Live' : '📦 Core'}
                    </span>
                    <span className="atlas-stat-sep">·</span>
                    <span className={`atlas-mcp-badge ${aimos.connected ? 'online' : 'offline'}`}>
                        <span className={`atlas-mcp-dot ${aimos.connected ? 'online' : 'offline'}`} />
                        MCP: {aimos.connected ? `${aimos.latency}ms` : '✗'}
                    </span>
                </div>
            </div>

            {/* Canvas */}
            <canvas
                ref={canvasRef}
                className="atlas-canvas"
                onMouseMove={handleMouseMove}
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onClick={handleClick}
                onMouseLeave={() => { setHoveredNode(null); handleMouseUp(); }}
            />

            {/* Layer Legend */}
            <div className="atlas-legend">
                {Object.entries(LAYER_COLORS).map(([layer, color]) => (
                    <div key={layer} className="atlas-legend-item">
                        <span className="atlas-legend-dot" style={{ background: color }} />
                        <span className="atlas-legend-text">L{layer}</span>
                    </div>
                ))}
            </div>

            {selectedNode && (
                <div className="atlas-detail-panel">
                    <div className="atlas-detail-header">
                        <span
                            className="atlas-detail-color"
                            style={{ background: selectedNode.color || DEFAULT_NODE_COLOR }}
                        />
                        <span className="atlas-detail-title">{selectedNode.label}</span>
                        <button className="atlas-detail-close" onClick={() => { setSelectedNode(null); setKnowledgeTab(null); setKnowledgeData(null); }}>✕</button>
                    </div>
                    <div className="atlas-detail-body">
                        <div className="atlas-detail-row">
                            <span className="atlas-detail-label">Type</span>
                            <span className="atlas-detail-value">{selectedNode.type}</span>
                        </div>
                        {selectedNode.layer && (
                            <div className="atlas-detail-row">
                                <span className="atlas-detail-label">Layer</span>
                                <span className="atlas-detail-value" style={{ color: LAYER_COLORS[selectedNode.layer] }}>
                                    Layer {selectedNode.layer}
                                </span>
                            </div>
                        )}
                        {selectedNode.systemId && (
                            <div className="atlas-detail-row">
                                <span className="atlas-detail-label">System</span>
                                <span className="atlas-detail-value">{selectedNode.systemId.toUpperCase()}</span>
                            </div>
                        )}
                        {selectedNode.description && (
                            <div className="atlas-detail-description">{selectedNode.description}</div>
                        )}
                        {selectedNode.status && (
                            <div className="atlas-detail-row">
                                <span className="atlas-detail-label">Status</span>
                                <span className={`atlas-detail-status ${selectedNode.status}`}>
                                    {selectedNode.status === 'production' ? '● Production' :
                                        selectedNode.status === 'active' ? '◉ Active' : selectedNode.status}
                                </span>
                            </div>
                        )}

                        {/* ─── Graph Stats ─── */}
                        {(() => {
                            const childNodes = graphData.nodes.filter(n => n.parent === selectedNode.id || n.systemId === selectedNode.id);
                            const connCount = filteredLinks.filter(l => l.source === selectedNode.id || l.target === selectedNode.id).length;
                            if (childNodes.length > 0 || connCount > 0) {
                                return (
                                    <div className="atlas-detail-stats">
                                        {childNodes.length > 0 && (
                                            <div className="atlas-stat-chip">
                                                <span className="atlas-stat-num">{childNodes.length}</span>
                                                <span className="atlas-stat-lbl">children</span>
                                            </div>
                                        )}
                                        <div className="atlas-stat-chip">
                                            <span className="atlas-stat-num">{connCount}</span>
                                            <span className="atlas-stat-lbl">links</span>
                                        </div>
                                    </div>
                                );
                            }
                            return null;
                        })()}

                        {/* ─── Context Web — Knowledge Section ─── */}
                        <div className="atlas-knowledge-section">
                            <div className="atlas-knowledge-header">
                                <span className="atlas-knowledge-title">🧠 Context Web</span>
                            </div>
                            <div className="atlas-knowledge-tabs">
                                {(['memory', 'evidence', 'confidence'] as const).map(tab => (
                                    <button
                                        key={tab}
                                        className={`atlas-knowledge-tab ${knowledgeTab === tab ? 'active' : ''}`}
                                        onClick={() => fetchKnowledge(tab, selectedNode)}
                                    >
                                        {tab === 'memory' ? '⬡ Memory' : tab === 'evidence' ? '◈ Evidence' : '◎ Confidence'}
                                    </button>
                                ))}
                            </div>
                            {knowledgeLoading && (
                                <div className="atlas-knowledge-loading">
                                    <span className="atlas-knowledge-spinner">⟳</span> Querying MCP...
                                </div>
                            )}
                            {knowledgeTab && knowledgeData && !knowledgeLoading && (
                                <div className="atlas-knowledge-content">
                                    {knowledgeTab === 'memory' && (
                                        <div className="atlas-knowledge-memories">
                                            {knowledgeData.memories && knowledgeData.memories.length > 0 ? (
                                                knowledgeData.memories.slice(0, 8).map((mem: any, i: number) => (
                                                    <div key={i} className="atlas-memory-item">
                                                        <div className="atlas-memory-content">
                                                            {typeof mem === 'string' ? mem : (mem.content || mem.text || JSON.stringify(mem)).slice(0, 120)}
                                                            {(typeof mem === 'string' ? mem : (mem.content || '')).length > 120 ? '…' : ''}
                                                        </div>
                                                        {mem.tags && (
                                                            <div className="atlas-memory-tags">
                                                                {Object.entries(mem.tags).slice(0, 3).map(([k, v]) => (
                                                                    <span key={k} className="atlas-memory-tag">{k}: {String(v)}</span>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="atlas-knowledge-empty">No memories found for "{selectedNode.label}"</div>
                                            )}
                                        </div>
                                    )}
                                    {knowledgeTab === 'evidence' && (
                                        <div className="atlas-knowledge-evidence">
                                            {knowledgeData.synthesis ? (
                                                <div className="atlas-evidence-item">
                                                    <div className="atlas-evidence-text">
                                                        {typeof knowledgeData.synthesis === 'string'
                                                            ? knowledgeData.synthesis.slice(0, 500)
                                                            : (knowledgeData.synthesis.summary || knowledgeData.synthesis.content || JSON.stringify(knowledgeData.synthesis)).slice(0, 500)}
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="atlas-knowledge-empty">No evidence graph for "{selectedNode.label}"</div>
                                            )}
                                        </div>
                                    )}
                                    {knowledgeTab === 'confidence' && (
                                        <div className="atlas-knowledge-confidence">
                                            {knowledgeData.confidence !== undefined ? (
                                                <div className="atlas-confidence-display">
                                                    <div className="atlas-confidence-ring" style={{
                                                        background: `conic-gradient(
                                                            ${knowledgeData.confidence > 0.7 ? '#4ecdc4' : knowledgeData.confidence > 0.4 ? '#f59e0b' : '#f43f5e'} ${knowledgeData.confidence * 360}deg,
                                                            rgba(255,255,255,0.05) 0deg
                                                        )`
                                                    }}>
                                                        <span className="atlas-confidence-pct">
                                                            {Math.round(knowledgeData.confidence * 100)}%
                                                        </span>
                                                    </div>
                                                    <div className="atlas-confidence-meta">
                                                        <div className="atlas-confidence-label">VIF Score</div>
                                                        {knowledgeData.reasoning && (
                                                            <div className="atlas-confidence-reason">{knowledgeData.reasoning}</div>
                                                        )}
                                                        {knowledgeData.evidence && Array.isArray(knowledgeData.evidence) && (
                                                            <div className="atlas-confidence-evidence-count">
                                                                {knowledgeData.evidence.length} evidence items
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="atlas-knowledge-empty">No confidence tracking for "{selectedNode.label}"</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* ─── Connections ─── */}
                        <div className="atlas-detail-connections">
                            <span className="atlas-detail-label">Connections</span>
                            <div className="atlas-detail-conn-list">
                                {filteredLinks
                                    .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                                    .slice(0, 12)
                                    .map((l, i) => {
                                        const otherId = l.source === selectedNode.id ? l.target : l.source;
                                        const otherNode = filteredNodes.find(n => n.id === otherId);
                                        return (
                                            <div key={i} className="atlas-detail-conn" onClick={() => {
                                                if (otherNode) { setSelectedNode(otherNode); setKnowledgeTab(null); setKnowledgeData(null); }
                                            }}>
                                                <span className="atlas-conn-dot" style={{ background: otherNode?.color || DEFAULT_NODE_COLOR }} />
                                                <span className="atlas-conn-name">{otherNode?.label || otherId}</span>
                                                <span className={`atlas-conn-strength ${l.strength}`}>
                                                    {l.strength === 'critical' ? '⚡' : l.strength === 'required' ? '●' : '○'}
                                                </span>
                                            </div>
                                        );
                                    })}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Simulation indicator */}
            {isSimulating && (
                <div className="atlas-sim-indicator">
                    <span className="atlas-sim-dot" />
                    Simulating...
                </div>
            )}
        </div>
    );
}
