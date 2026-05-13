import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import '../styles/timeline-v2.css';

// ─── Core Types ───

type AgentId = 'opus' | 'aether' | 'gemini' | 'sev' | 'braden' | 'codex' | 'unknown';
type SemanticState = 'planning' | 'building' | 'testing' | 'deployed';
type CommitSize = 'small' | 'normal' | 'large' | 'milestone';

interface CommitV2 {
    hash: string;
    author: string;
    agent: AgentId;
    message: string;
    timestamp: string;
    branch: string;
    state: SemanticState; // what KIND of work this commit represents
    impact: number;       // 0-1 how much this commit changes (file count, LOC)
    size: CommitSize;     // visual weight of this commit
    isMerge: boolean;
    mission?: string;     // mission ID this belongs to
    files?: { name: string; action: 'add' | 'modify' | 'delete' }[];
    dependsOn?: string;   // hash of commit this depends on (cross-agent link)
}

interface MissionArc {
    id: string;
    title: string;
    color: string;
    startIdx: number;
    endIdx: number;
}

// ─── Agent Config ───

const AGENTS: { id: AgentId; label: string; color: string }[] = [
    { id: 'opus', label: 'OPUS', color: '#CC7722' },
    { id: 'aether', label: 'AETHER', color: '#7C4DFF' },
    { id: 'gemini', label: 'GEMINI', color: '#4285F4' },
    { id: 'sev', label: 'SEV', color: '#00D4FF' },
    { id: 'braden', label: 'BRADEN', color: '#E8E8E8' },
    { id: 'codex', label: 'CODEX', color: '#4CAF50' },
];

const STATE_CONFIG: Record<SemanticState, { color: string; y: number; label: string }> = {
    planning: { color: '#7C4DFF', y: 0.15, label: 'Plan' },
    building: { color: '#00D4FF', y: 0.45, label: 'Build' },
    testing: { color: '#4CAF50', y: 0.70, label: 'Test' },
    deployed: { color: '#FFB74D', y: 0.90, label: 'Ship' },
};

const AGENT_MAP: Record<AgentId, string> = {
    opus: '#CC7722', aether: '#7C4DFF', gemini: '#4285F4',
    sev: '#00D4FF', braden: '#E8E8E8', codex: '#4CAF50', unknown: '#666',
};

// ─── Custom SVG Icons ───

function LayersIcon({ size = 11 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <polygon points="12,2 2,7 12,12 22,7" />
            <polyline points="2,17 12,22 22,17" />
            <polyline points="2,12 12,17 22,12" />
        </svg>
    );
}

// ─── Mock Data — Real Today's Session ───

function generateAdvancedCommits(): CommitV2[] {
    return ([
        // Dec 2025 — WebGPU work (Braden)
        { hash: '1a6b2b3', author: 'Braden', agent: 'braden', message: 'Depth Pyramid, VB Shading, Forward+ demos, ParticleLife WebGPU', timestamp: '2025-12-05T20:20:59', branch: 'ionv4x-orbital-weather-mvp', state: 'building', impact: 0.8, size: 'large', isMerge: false, files: [{ name: 'depthPyramid.wgsl', action: 'add' }, { name: 'forwardPlus.ts', action: 'add' }] },
        { hash: '8c97033', author: 'Braden', agent: 'braden', message: 'Forward+/Visibility pipeline scaffolding', timestamp: '2025-12-05T20:30:17', branch: 'ionv4x-orbital-weather-mvp', state: 'building', impact: 0.6, size: 'normal', isMerge: false },
        { hash: '6f2dfbc', author: 'Braden', agent: 'braden', message: 'Forward+/Clustered light data wiring and depth pyramid compute scaffolds', timestamp: '2025-12-05T20:37:05', branch: 'ionv4x-orbital-weather-mvp', state: 'building', impact: 0.7, size: 'normal', isMerge: false },

        // Feb 2026 — Docs (Braden)
        { hash: '1661afa', author: 'Braden', agent: 'braden', message: 'docs: enhance README — clone, systems, MCP tools, repo contents, setup pointers', timestamp: '2026-02-21T22:59:51', branch: 'clean-master', state: 'planning', impact: 0.3, size: 'small', isMerge: false },
        { hash: 'a57d790', author: 'Braden', agent: 'braden', message: 'docs: README full system names; gitignore + untrack ProEarth, planet-engine', timestamp: '2026-02-21T23:44:00', branch: 'clean-master', state: 'planning', impact: 0.4, size: 'normal', isMerge: false },
        { hash: '5077616', author: 'Braden', agent: 'braden', message: 'README source-of-truth updates, chip diagram, System Atlas, major systems doc', timestamp: '2026-02-22T00:36:40', branch: 'clean-master', state: 'planning', impact: 0.5, size: 'normal', isMerge: false, mission: 'M-40' },

        // Mar 2 — JOC Design Phase (Opus)
        { hash: 'aa11bb2', author: 'Opus', agent: 'opus', message: 'docs: JOC Master Vision, Architecture, UI Design, Compute Layout (4 docs, ~2500 lines)', timestamp: '2026-03-02T09:00:00', branch: 'opus/M-42/joc-build', state: 'planning', impact: 0.9, size: 'milestone', isMerge: false, mission: 'M-42', files: [{ name: 'OPUS1_JOC_MASTER_VISION.md', action: 'add' }, { name: 'OPUS1_JOC_ARCHITECTURE.md', action: 'add' }, { name: 'OPUS1_JOC_UI_DESIGN.md', action: 'add' }] },

        // Aether sign-off
        { hash: 'bb22cc3', author: 'Aether', agent: 'aether', message: 'Sign-off granted for JOC Phase A — scope locked, constraints set', timestamp: '2026-03-02T10:14:00', branch: 'main', state: 'planning', impact: 0.2, size: 'normal', isMerge: false, mission: 'M-42', dependsOn: 'aa11bb2' },

        // Phase A Build (Opus)
        { hash: 'd4e5f6a', author: 'Opus', agent: 'opus', message: 'feat(joc): Package scaffold + Vite config', timestamp: '2026-03-02T09:15:00', branch: 'opus/M-42/joc-build', state: 'building', impact: 0.4, size: 'normal', isMerge: false, mission: 'M-42' },
        { hash: 'f1a2b3c', author: 'Opus', agent: 'opus', message: 'feat(joc): Shell layout, dashboard, 14 custom SVG icons, design system', timestamp: '2026-03-02T09:45:00', branch: 'opus/M-42/joc-build', state: 'building', impact: 0.9, size: 'large', isMerge: false, mission: 'M-42', files: [{ name: 'App.tsx', action: 'add' }, { name: 'joc.css', action: 'add' }, { name: 'icons.tsx', action: 'add' }, { name: 'DashboardPage.tsx', action: 'add' }] },

        // Phase B1 (Opus)
        { hash: 'c7d8e9f', author: 'Opus', agent: 'opus', message: 'feat(joc): Session page with automation overlay + debug rail + pipeline', timestamp: '2026-03-02T10:45:00', branch: 'opus/M-42/joc-build', state: 'building', impact: 0.85, size: 'large', isMerge: false, mission: 'M-42', files: [{ name: 'SessionPage.tsx', action: 'add' }, { name: 'session.css', action: 'add' }, { name: 'sessionStore.ts', action: 'add' }] },

        // Phase B2 (Opus)
        { hash: 'e4f5a6b', author: 'Opus', agent: 'opus', message: 'feat(joc): Electron shell, ChatGPT + Gemini AI drivers, IPC bridge', timestamp: '2026-03-02T11:30:00', branch: 'opus/M-42/joc-build', state: 'building', impact: 0.95, size: 'milestone', isMerge: false, mission: 'M-42', files: [{ name: 'electron/main.cjs', action: 'add' }, { name: 'aiDrivers.ts', action: 'add' }, { name: 'preload.js', action: 'add' }] },

        // Phase B3 — Comms (Opus)
        { hash: 'a1b2c3d', author: 'Opus', agent: 'opus', message: 'feat(joc): Agent comms drawer — Discord-like with real MCP messages', timestamp: '2026-03-02T12:04:00', branch: 'opus/M-42/joc-build', state: 'building', impact: 0.7, size: 'normal', isMerge: false, mission: 'M-42', files: [{ name: 'AgentCommsDrawer.tsx', action: 'add' }, { name: 'comms.css', action: 'add' }] },

        // Connectivity test (Opus)
        { hash: 'cc33dd4', author: 'Opus', agent: 'opus', message: 'test: AI connectivity harness — Gemini CLI + API + MCP bridge test', timestamp: '2026-03-02T11:10:00', branch: 'opus/M-42/joc-build', state: 'testing', impact: 0.3, size: 'small', isMerge: false, mission: 'M-42', files: [{ name: 'test-connectivity.mjs', action: 'add' }] },

        // Phase C — Git Timeline (Opus)
        { hash: 'dd44ee5', author: 'Opus', agent: 'opus', message: 'feat(joc): Git Subway Map V2 — multi-layer narrative timeline', timestamp: '2026-03-02T12:23:00', branch: 'opus/M-42/joc-build', state: 'building', impact: 0.9, size: 'milestone', isMerge: false, mission: 'M-42', files: [{ name: 'GitTimelineV2.tsx', action: 'add' }, { name: 'timeline-v2.css', action: 'add' }] },
    ] as CommitV2[]).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
}

// ─── Component ───

type LayerKey = 'heat' | 'flow' | 'missions' | 'impact' | 'zones';

export function GitTimelineV2() {
    const [commits] = useState<CommitV2[]>(generateAdvancedCommits);
    const [hovered, setHovered] = useState<string | null>(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const [playing, setPlaying] = useState(false);
    const [playHead, setPlayHead] = useState(commits.length - 1);
    const [layers, setLayers] = useState<Record<LayerKey, boolean>>({
        heat: true, flow: true, missions: true, impact: true, zones: true,
    });
    const viewportRef = useRef<HTMLDivElement>(null);
    const animRef = useRef<ReturnType<typeof setTimeout>>();

    const toggleLayer = (key: LayerKey) =>
        setLayers(prev => ({ ...prev, [key]: !prev[key] }));

    // Playback
    useEffect(() => {
        if (!playing) return;
        const advance = () => {
            setPlayHead(prev => {
                if (prev >= commits.length - 1) { setPlaying(false); return commits.length - 1; }
                return prev + 1;
            });
            animRef.current = setTimeout(advance, 600);
        };
        animRef.current = setTimeout(advance, 600);
        return () => clearTimeout(animRef.current);
    }, [playing, commits.length]);

    // Layout params
    const nodeSpacing = 90;
    const canvasWidth = commits.length * nodeSpacing + 120;
    const agentHeatHeight = AGENTS.length * 14;
    const mainHeight = 200;
    const totalHeight = agentHeatHeight + mainHeight + 20;
    const flowTop = agentHeatHeight;
    const flowHeight = mainHeight;

    // Mouse tracking for tooltip
    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        setMousePos({ x: e.clientX, y: e.clientY });
    }, []);

    // Derive agent heat data (per time slot, per agent)
    const agentHeat = useMemo(() => {
        const heat: Record<AgentId, number[]> = {} as any;
        AGENTS.forEach(a => { heat[a.id] = new Array(commits.length).fill(0); });

        commits.forEach((c, idx) => {
            if (heat[c.agent]) heat[c.agent][idx] = c.impact;
            // Spread heat to neighboring slots for continuity
            if (idx > 0 && heat[c.agent]) heat[c.agent][idx - 1] = Math.max(heat[c.agent][idx - 1], c.impact * 0.3);
            if (idx < commits.length - 1 && heat[c.agent]) heat[c.agent][idx + 1] = Math.max(heat[c.agent][idx + 1], c.impact * 0.3);
        });

        return heat;
    }, [commits]);

    // Mission arcs
    const missionArcs = useMemo(() => {
        const arcs: MissionArc[] = [];
        const missionMap = new Map<string, { start: number; end: number }>();

        commits.forEach((c, idx) => {
            if (c.mission) {
                if (!missionMap.has(c.mission)) {
                    missionMap.set(c.mission, { start: idx, end: idx });
                } else {
                    missionMap.get(c.mission)!.end = idx;
                }
            }
        });

        missionMap.forEach((range, id) => {
            arcs.push({
                id,
                title: id,
                color: id === 'M-42' ? '#7C4DFF' : '#888',
                startIdx: range.start,
                endIdx: range.end,
            });
        });

        return arcs;
    }, [commits]);

    // Build SVG flow paths — organic curves between commits
    const flowPaths = useMemo(() => {
        const paths: { d: string; color: string; width: number }[] = [];

        for (let i = 0; i < commits.length - 1; i++) {
            const from = commits[i];
            const to = commits[i + 1];

            // Only connect commits on the same branch
            if (from.branch !== to.branch) continue;

            const x1 = i * nodeSpacing + nodeSpacing / 2;
            const x2 = (i + 1) * nodeSpacing + nodeSpacing / 2;
            const y1 = STATE_CONFIG[from.state].y * flowHeight;
            const y2 = STATE_CONFIG[to.state].y * flowHeight;

            // Organic bezier — the curve shape tells the story
            const dx = (x2 - x1) * 0.4;
            const width = 2 + from.impact * 2; // thicker for higher impact

            paths.push({
                d: `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`,
                color: AGENT_MAP[from.agent],
                width,
            });
        }

        // Cross-agent dependency links (dashed)
        commits.forEach((c, idx) => {
            if (c.dependsOn) {
                const depIdx = commits.findIndex(cc => cc.hash === c.dependsOn);
                if (depIdx >= 0) {
                    const from = commits[depIdx];
                    const x1 = depIdx * nodeSpacing + nodeSpacing / 2;
                    const x2 = idx * nodeSpacing + nodeSpacing / 2;
                    const y1 = STATE_CONFIG[from.state].y * flowHeight;
                    const y2 = STATE_CONFIG[c.state].y * flowHeight;
                    const dx = (x2 - x1) * 0.3;

                    paths.push({
                        d: `M ${x1} ${y1} C ${x1 + dx} ${y1 - 20}, ${x2 - dx} ${y2 - 20}, ${x2} ${y2}`,
                        color: '#ffffff30',
                        width: 1.5,
                    });
                }
            }
        });

        return paths;
    }, [commits, nodeSpacing, flowHeight]);

    const hoveredCommit = commits.find(c => c.hash === hovered);

    return (
        <div className="timeline-v2" onMouseMove={handleMouseMove}>
            {/* Header */}
            <div className="timeline-v2-header">
                <LayersIcon />
                <span className="timeline-v2-title">Narrative Timeline</span>
                <span className="timeline-v2-subtitle">
                    {commits.length} events • {new Set(commits.map(c => c.branch)).size} branches • {new Set(commits.map(c => c.agent)).size} agents
                </span>

                <div className="layer-toggles">
                    {([
                        { key: 'heat' as LayerKey, label: 'Heat', color: '#CC7722' },
                        { key: 'zones' as LayerKey, label: 'Zones', color: '#7C4DFF' },
                        { key: 'flow' as LayerKey, label: 'Flow', color: '#00D4FF' },
                        { key: 'missions' as LayerKey, label: 'Missions', color: '#FFB74D' },
                        { key: 'impact' as LayerKey, label: 'Impact', color: '#4CAF50' },
                    ]).map(l => (
                        <button
                            key={l.key}
                            className={`layer-toggle ${layers[l.key] ? 'active' : ''}`}
                            onClick={() => toggleLayer(l.key)}
                        >
                            <span className="layer-toggle-dot" style={{ background: layers[l.key] ? l.color : '#444' }} />
                            {l.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Canvas */}
            <div className="timeline-v2-viewport" ref={viewportRef}>
                <div className="timeline-v2-canvas" style={{ width: `${canvasWidth}px`, height: `${totalHeight}px` }}>

                    {/* Layer 1: Agent Activity Heat */}
                    {layers.heat && (
                        <div className="layer-agent-heat">
                            {AGENTS.map(agent => (
                                <div key={agent.id} className="agent-heat-row">
                                    <span className="agent-heat-label" style={{ color: agent.color }}>{agent.label}</span>
                                    <div className="agent-heat-strip">
                                        {agentHeat[agent.id]?.map((intensity, idx) => (
                                            <div
                                                key={idx}
                                                className="heat-block"
                                                style={{
                                                    width: `${nodeSpacing}px`,
                                                    background: agent.color,
                                                    opacity: idx <= playHead ? intensity * 0.6 : 0,
                                                }}
                                            />
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Layer 2: Semantic State Zones */}
                    {layers.zones && (
                        <div className="layer-state-zones" style={{ top: `${flowTop}px`, height: `${flowHeight}px` }}>
                            {Object.entries(STATE_CONFIG).map(([state, cfg]) => (
                                <div
                                    key={state}
                                    className={`state-zone ${state}`}
                                    style={{ top: `${cfg.y * 100}%` }}
                                >
                                    <span className="state-zone-label" style={{ color: cfg.color }}>
                                        {cfg.label}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Layer 3: Flow Paths (SVG) */}
                    {layers.flow && (
                        <svg
                            className="commit-flow-svg"
                            style={{ top: `${flowTop}px`, height: `${flowHeight}px`, position: 'absolute', left: '60px' }}
                            width={canvasWidth - 60}
                            height={flowHeight}
                        >
                            {flowPaths.map((p, i) => (
                                <path
                                    key={i}
                                    className="flow-path"
                                    d={p.d}
                                    stroke={p.color}
                                    strokeWidth={p.width}
                                    strokeDasharray={p.width < 2 ? '6,4' : 'none'}
                                />
                            ))}
                        </svg>
                    )}

                    {/* Layer 4: Mission Arcs */}
                    {layers.missions && missionArcs.map(arc => {
                        const x1 = arc.startIdx * nodeSpacing + nodeSpacing / 2;
                        const x2 = arc.endIdx * nodeSpacing + nodeSpacing / 2;
                        const width = x2 - x1;
                        if (width <= 0) return null;
                        return (
                            <div
                                key={arc.id}
                                className="mission-arc"
                                style={{
                                    left: `${60 + x1}px`,
                                    width: `${width}px`,
                                    top: `${flowTop - 8}px`,
                                    height: '16px',
                                    borderColor: arc.color,
                                }}
                            >
                                <span className="mission-arc-label" style={{ color: arc.color }}>
                                    {arc.title}
                                </span>
                            </div>
                        );
                    })}

                    {/* Commit Nodes */}
                    {commits.map((commit, idx) => {
                        const x = 60 + idx * nodeSpacing + nodeSpacing / 2;
                        const y = flowTop + STATE_CONFIG[commit.state].y * flowHeight;
                        const isActive = idx <= playHead;
                        const dotSize = commit.size === 'milestone' ? 18 : commit.size === 'large' ? 14 : commit.size === 'small' ? 8 : 10;

                        return (
                            <div
                                key={commit.hash}
                                className="commit-v2"
                                style={{
                                    left: `${x - dotSize / 2}px`,
                                    top: `${y - dotSize / 2}px`,
                                    opacity: isActive ? 1 : 0.2,
                                    transition: 'opacity 0.4s ease',
                                }}
                                onMouseEnter={() => setHovered(commit.hash)}
                                onMouseLeave={() => setHovered(null)}
                            >
                                <div
                                    className={`commit-v2-dot ${commit.size} ${commit.isMerge ? 'merge' : ''} ${commit.impact > 0.8 ? 'high-impact' : ''}`}
                                    style={{
                                        width: `${dotSize}px`,
                                        height: `${dotSize}px`,
                                        borderColor: AGENT_MAP[commit.agent],
                                        ['--agent-color' as any]: AGENT_MAP[commit.agent],
                                        background: hovered === commit.hash ? AGENT_MAP[commit.agent] : 'var(--bg-deep)',
                                    }}
                                />
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Layer 5: Impact Heatmap Strip */}
            {layers.impact && (
                <div className="layer-impact">
                    <span className="impact-label">Impact</span>
                    <div className="impact-strip">
                        {commits.map((c, idx) => (
                            <div
                                key={c.hash}
                                className="impact-cell"
                                data-files={c.files?.length ? `${c.files.length} files` : '–'}
                                style={{
                                    width: `${nodeSpacing}px`,
                                    background: `linear-gradient(to top, ${AGENT_MAP[c.agent]}${Math.round(c.impact * 180).toString(16).padStart(2, '0')}, transparent)`,
                                    opacity: idx <= playHead ? 1 : 0.1,
                                }}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Playback Controls */}
            <div className="timeline-v2-controls">
                <button className="timeline-ctrl-btn" onClick={() => { setPlayHead(0); setPlaying(false); }}>
                    <svg width={12} height={12} viewBox="0 0 24 24" fill="currentColor"><polygon points="19,20 9,12 19,4" /><line x1="5" y1="19" x2="5" y2="5" stroke="currentColor" strokeWidth="2" /></svg>
                </button>
                <button className={`timeline-ctrl-btn ${playing ? 'active' : ''}`} onClick={() => setPlaying(!playing)}>
                    {playing
                        ? <svg width={12} height={12} viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></svg>
                        : <svg width={12} height={12} viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21" /></svg>
                    }
                </button>
                <button className="timeline-ctrl-btn" onClick={() => { setPlayHead(commits.length - 1); setPlaying(false); }}>
                    <svg width={12} height={12} viewBox="0 0 24 24" fill="currentColor"><polygon points="5,4 15,12 5,20" /><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" strokeWidth="2" /></svg>
                </button>

                <div className="timeline-scrubber" onClick={e => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const pct = (e.clientX - rect.left) / rect.width;
                    setPlayHead(Math.round(pct * (commits.length - 1)));
                    setPlaying(false);
                }}>
                    <div className="timeline-scrubber-fill" style={{ width: `${(playHead / Math.max(commits.length - 1, 1)) * 100}%` }} />
                    <div className="timeline-scrubber-head" style={{ left: `${(playHead / Math.max(commits.length - 1, 1)) * 100}%` }} />
                </div>

                <span className="timeline-range-label">
                    {commits[playHead]?.hash.slice(0, 7)} • {commits[playHead]?.state}
                </span>
            </div>

            {/* Floating Tooltip */}
            {hoveredCommit && (
                <div
                    className="tooltip-v2"
                    style={{ left: mousePos.x + 16, top: mousePos.y - 80 }}
                >
                    <div className="tooltip-v2-header">
                        <span className="tooltip-v2-agent-dot" style={{ background: AGENT_MAP[hoveredCommit.agent] }} />
                        <span className="tooltip-v2-hash">{hoveredCommit.hash}</span>
                        <span className={`tooltip-v2-state ${hoveredCommit.state}`}>{hoveredCommit.state}</span>
                    </div>
                    <div className="tooltip-v2-msg">{hoveredCommit.message}</div>
                    <div className="tooltip-v2-meta">
                        <span className="tooltip-v2-meta-key">Author</span>
                        <span className="tooltip-v2-meta-val" style={{ color: AGENT_MAP[hoveredCommit.agent] }}>{hoveredCommit.author}</span>
                        <span className="tooltip-v2-meta-key">Branch</span>
                        <span className="tooltip-v2-meta-val">{hoveredCommit.branch}</span>
                        <span className="tooltip-v2-meta-key">Impact</span>
                        <span className="tooltip-v2-meta-val">{Math.round(hoveredCommit.impact * 100)}%</span>
                        {hoveredCommit.mission && (<>
                            <span className="tooltip-v2-meta-key">Mission</span>
                            <span className="tooltip-v2-meta-val">{hoveredCommit.mission}</span>
                        </>)}
                    </div>
                    {hoveredCommit.files && (
                        <div className="tooltip-v2-files">
                            {hoveredCommit.files.map(f => (
                                <div key={f.name} className={`tooltip-v2-file tooltip-v2-file-${f.action === 'add' ? 'add' : f.action === 'delete' ? 'del' : 'mod'}`}>
                                    {f.action === 'add' ? '+' : f.action === 'delete' ? '−' : '~'} {f.name}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
