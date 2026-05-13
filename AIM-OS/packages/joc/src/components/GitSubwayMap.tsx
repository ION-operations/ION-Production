import { useState, useRef, useEffect, useMemo } from 'react';
import '../styles/timeline.css';

// ─── Types ───

interface GitCommit {
    hash: string;
    author: string;
    message: string;
    timestamp: string;
    branch: string;
    isMerge: boolean;
    agent: AgentId;
    lane: number;
    files?: string[];
}

interface GitBranch {
    name: string;
    color: string;
    lane: number;
    commits: GitCommit[];
}

type AgentId = 'opus' | 'aether' | 'gemini' | 'sev' | 'braden' | 'codex' | 'unknown';

// ─── Custom SVG Icons ───

function GitBranchIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="6" y1="3" x2="6" y2="15" />
            <circle cx="18" cy="6" r="3" />
            <circle cx="6" cy="18" r="3" />
            <path d="M18 9a9 9 0 0 1-9 9" />
        </svg>
    );
}

function CommitIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="12" cy="12" r="4" />
            <line x1="1.05" y1="12" x2="7" y2="12" />
            <line x1="17.01" y1="12" x2="22.96" y2="12" />
        </svg>
    );
}

function PlayIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5,3 19,12 5,21" />
        </svg>
    );
}

function PauseIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
        </svg>
    );
}

function SkipBackIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <polygon points="19,20 9,12 19,4" />
            <line x1="5" y1="19" x2="5" y2="5" stroke="currentColor" strokeWidth="2" />
        </svg>
    );
}

function SkipFwdIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5,4 15,12 5,20" />
            <line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" strokeWidth="2" />
        </svg>
    );
}

function ZoomInIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
            <line x1="11" y1="8" x2="11" y2="14" />
            <line x1="8" y1="11" x2="14" y2="11" />
        </svg>
    );
}

function ZoomOutIcon({ size = 12 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
            <line x1="8" y1="11" x2="14" y2="11" />
        </svg>
    );
}

// ─── Helpers ───

const AGENT_COLORS: Record<AgentId, string> = {
    opus: '#CC7722',
    aether: '#7C4DFF',
    gemini: '#4285F4',
    sev: '#00D4FF',
    braden: '#E8E8E8',
    codex: '#4CAF50',
    unknown: '#666',
};

const ROUTE_COLORS: Record<string, string> = {
    main: '#E8E8E8',
    master: '#E8E8E8',
    'clean-master': '#B0B0B0',
    feat: '#7C4DFF',
    fix: '#4CAF50',
    hotfix: '#FF5722',
    session: '#00D4FF',
    orbital: '#FFB74D',
    default: '#888',
};

function detectAgent(author: string, message: string): AgentId {
    const lower = (author + ' ' + message).toLowerCase();
    if (lower.includes('opus') || lower.includes('claude')) return 'opus';
    if (lower.includes('aether')) return 'aether';
    if (lower.includes('gemini')) return 'gemini';
    if (lower.includes('sev')) return 'sev';
    if (lower.includes('codex')) return 'codex';
    if (lower.includes('braden') || lower.includes('bombe')) return 'braden';
    return 'braden'; // Default to user
}

function getBranchColor(branchName: string): string {
    const lower = branchName.toLowerCase();
    for (const [key, color] of Object.entries(ROUTE_COLORS)) {
        if (lower.includes(key)) return color;
    }
    return ROUTE_COLORS.default;
}

function formatTimestamp(ts: string): string {
    try {
        const d = new Date(ts);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
        return ts;
    }
}

function formatTimeRange(ts: string): string {
    try {
        const d = new Date(ts);
        return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    } catch {
        return ts;
    }
}

// ─── Mock Data (with today's real work + historical commits) ───

function generateMockCommits(): GitCommit[] {
    return ([
        // Today's JOC work (from this session!)
        {
            hash: 'a1b2c3d',
            author: 'Opus',
            message: 'feat(joc): Agent comms drawer with MCP messages',
            timestamp: '2026-03-02T12:04:00',
            branch: 'opus/M-42/joc-build',
            isMerge: false,
            agent: 'opus',
            lane: 1,
            files: ['AgentCommsDrawer.tsx', 'comms.css', 'DrawerSystem.tsx'],
        },
        {
            hash: 'e4f5a6b',
            author: 'Opus',
            message: 'feat(joc): Electron shell + AI drivers',
            timestamp: '2026-03-02T11:30:00',
            branch: 'opus/M-42/joc-build',
            isMerge: false,
            agent: 'opus',
            lane: 1,
            files: ['electron/main.cjs', 'preload.js', 'aiDrivers.ts'],
        },
        {
            hash: 'c7d8e9f',
            author: 'Opus',
            message: 'feat(joc): Session page automation overlay',
            timestamp: '2026-03-02T10:45:00',
            branch: 'opus/M-42/joc-build',
            isMerge: false,
            agent: 'opus',
            lane: 1,
            files: ['SessionPage.tsx', 'session.css', 'sessionStore.ts'],
        },
        {
            hash: 'f1a2b3c',
            author: 'Opus',
            message: 'feat(joc): Shell layout, dashboard, custom icons',
            timestamp: '2026-03-02T09:45:00',
            branch: 'opus/M-42/joc-build',
            isMerge: false,
            agent: 'opus',
            lane: 1,
            files: ['App.tsx', 'joc.css', 'icons.tsx', 'DashboardPage.tsx'],
        },
        {
            hash: 'd4e5f6a',
            author: 'Opus',
            message: 'feat(joc): Package scaffold + Vite config',
            timestamp: '2026-03-02T09:15:00',
            branch: 'opus/M-42/joc-build',
            isMerge: false,
            agent: 'opus',
            lane: 1,
        },
        // Aether orchestration
        {
            hash: 'b7c8d9e',
            author: 'Aether',
            message: 'chore: Phase A sign-off, branch permissions updated',
            timestamp: '2026-03-02T10:14:00',
            branch: 'main',
            isMerge: false,
            agent: 'aether',
            lane: 0,
        },
        // Earlier Braden commits (real from git log)
        {
            hash: '5077616',
            author: 'Braden',
            message: 'README source-of-truth, chip diagram, System Atlas',
            timestamp: '2026-02-22T00:36:40',
            branch: 'clean-master',
            isMerge: false,
            agent: 'braden',
            lane: 0,
        },
        {
            hash: 'a57d790',
            author: 'Braden',
            message: 'docs: full system names, gitignore + untrack apps',
            timestamp: '2026-02-21T23:44:00',
            branch: 'clean-master',
            isMerge: false,
            agent: 'braden',
            lane: 0,
        },
        {
            hash: '1661afa',
            author: 'Braden',
            message: 'docs: README clone, systems, MCP tools, setup',
            timestamp: '2026-02-21T22:59:51',
            branch: 'clean-master',
            isMerge: false,
            agent: 'braden',
            lane: 0,
        },
        {
            hash: '6f2dfbc',
            author: 'Braden',
            message: 'Forward+/Clustered light data wiring + depth pyramid',
            timestamp: '2025-12-05T20:37:05',
            branch: 'ionv4x-orbital-weather-mvp',
            isMerge: false,
            agent: 'braden',
            lane: 2,
        },
        {
            hash: '8c97033',
            author: 'Braden',
            message: 'Forward+/Visibility pipeline scaffolding',
            timestamp: '2025-12-05T20:30:17',
            branch: 'ionv4x-orbital-weather-mvp',
            isMerge: false,
            agent: 'braden',
            lane: 2,
        },
        {
            hash: '1a6b2b3',
            author: 'Braden',
            message: 'Depth Pyramid, VB Shading, Forward+ demos',
            timestamp: '2025-12-05T20:20:59',
            branch: 'ionv4x-orbital-weather-mvp',
            isMerge: false,
            agent: 'braden',
            lane: 2,
        },
    ] as GitCommit[]).reverse(); // oldest first
}

// ─── Component ───

export function GitSubwayMap() {
    const [commits] = useState<GitCommit[]>(generateMockCommits);
    const [selected, setSelected] = useState<string | null>(null);
    const [hoveredHash, setHoveredHash] = useState<string | null>(null);
    const [playing, setPlaying] = useState(false);
    const [playHead, setPlayHead] = useState(0);
    const [zoom, setZoom] = useState(1);
    const viewportRef = useRef<HTMLDivElement>(null);
    const animRef = useRef<number>();

    // Playback animation
    useEffect(() => {
        if (!playing) return;
        const advance = () => {
            setPlayHead(prev => {
                if (prev >= commits.length - 1) {
                    setPlaying(false);
                    return commits.length - 1;
                }
                return prev + 1;
            });
            animRef.current = setTimeout(advance, 800) as any;
        };
        animRef.current = setTimeout(advance, 800) as any;
        return () => clearTimeout(animRef.current);
    }, [playing, commits.length]);

    // Derive branches
    const branches = useMemo(() => {
        const branchMap = new Map<string, GitBranch>();
        commits.forEach(c => {
            if (!branchMap.has(c.branch)) {
                branchMap.set(c.branch, {
                    name: c.branch,
                    color: getBranchColor(c.branch),
                    lane: c.lane,
                    commits: [],
                });
            }
            branchMap.get(c.branch)!.commits.push(c);
        });
        return Array.from(branchMap.values());
    }, [commits]);

    // Lane count
    const laneCount = Math.max(...commits.map(c => c.lane)) + 1;
    const nodeWidth = 100 * zoom;
    const laneHeight = 50;
    const topPadding = 30;

    // Selected commit details
    const selectedCommit = commits.find(c => c.hash === selected);
    const hoveredCommit = commits.find(c => c.hash === hoveredHash);

    const getNodeY = (lane: number) => topPadding + lane * laneHeight + laneHeight / 2;

    // Build SVG route paths
    const routePaths = useMemo(() => {
        const paths: { d: string; color: string; isMerge?: boolean }[] = [];

        branches.forEach(branch => {
            const sorted = [...branch.commits].sort(
                (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
            );

            for (let i = 0; i < sorted.length - 1; i++) {
                const fromIdx = commits.indexOf(sorted[i]);
                const toIdx = commits.indexOf(sorted[i + 1]);
                const fromX = fromIdx * nodeWidth + nodeWidth / 2;
                const toX = toIdx * nodeWidth + nodeWidth / 2;
                const fromY = getNodeY(sorted[i].lane);
                const toY = getNodeY(sorted[i + 1].lane);

                if (fromY === toY) {
                    // Same lane: straight line
                    paths.push({ d: `M ${fromX} ${fromY} L ${toX} ${toY}`, color: branch.color });
                } else {
                    // Different lane: bezier curve (subway bend)
                    const midX = (fromX + toX) / 2;
                    paths.push({
                        d: `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`,
                        color: branch.color,
                    });
                }
            }
        });

        return paths;
    }, [branches, commits, nodeWidth, laneCount]);

    return (
        <div className="git-timeline">
            {/* Header */}
            <div className="git-timeline-header">
                <GitBranchIcon size={14} />
                <span className="git-timeline-title">Git Timeline</span>
                <span style={{ fontSize: '9px', color: 'var(--text-hint)' }}>
                    {commits.length} commits • {branches.length} branches
                </span>

                <div className="branch-legend">
                    {branches.map(b => (
                        <div key={b.name} className="branch-legend-item">
                            <div className="branch-legend-line" style={{ background: b.color }} />
                            <span>{b.name.split('/').pop()}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Subway Map */}
            <div className="subway-map-viewport" ref={viewportRef}>
                <div
                    className="subway-map-canvas"
                    style={{ width: `${commits.length * nodeWidth + 40}px`, height: `${laneCount * laneHeight + topPadding + 60}px` }}
                >
                    {/* SVG Connection Lines */}
                    <svg
                        className="subway-connections"
                        width={commits.length * nodeWidth + 40}
                        height={laneCount * laneHeight + topPadding + 60}
                    >
                        {routePaths.map((p, i) => (
                            <path key={i} d={p.d} stroke={p.color} className={p.isMerge ? 'merge-line' : ''} />
                        ))}
                    </svg>

                    {/* Commit Nodes */}
                    {commits.map((commit, idx) => {
                        const x = idx * nodeWidth;
                        const y = getNodeY(commit.lane);
                        const isActive = idx <= playHead;
                        const isSelected = selected === commit.hash;
                        const isHovered = hoveredHash === commit.hash;

                        return (
                            <div
                                key={commit.hash}
                                className={`commit-node ${isSelected ? 'selected' : ''}`}
                                style={{
                                    position: 'absolute',
                                    left: `${x}px`,
                                    top: `${y - 7}px`,
                                    opacity: isActive ? 1 : 0.35,
                                    transition: 'opacity 0.3s ease',
                                }}
                                onClick={() => setSelected(isSelected ? null : commit.hash)}
                                onMouseEnter={() => setHoveredHash(commit.hash)}
                                onMouseLeave={() => setHoveredHash(null)}
                            >
                                {/* Station Dot */}
                                <div
                                    className={`commit-dot ${commit.isMerge ? 'merge' : ''}`}
                                    style={{
                                        borderColor: AGENT_COLORS[commit.agent],
                                        background: isSelected ? AGENT_COLORS[commit.agent] : 'var(--bg-deep)',
                                    }}
                                />

                                {/* Labels below dot */}
                                <span className="commit-hash">{commit.hash.slice(0, 7)}</span>
                                <span className="commit-msg">{commit.message.slice(0, 40)}</span>
                                <span className="commit-author" style={{ color: AGENT_COLORS[commit.agent] }}>
                                    {commit.author}
                                </span>
                                <span className="commit-time">{formatTimestamp(commit.timestamp)}</span>

                                {/* Tooltip */}
                                {isHovered && (
                                    <div className="commit-tooltip">
                                        <div className="commit-tooltip-hash">{commit.hash}</div>
                                        <div className="commit-tooltip-msg">{commit.message}</div>
                                        <div className="commit-tooltip-meta">
                                            <span style={{ color: AGENT_COLORS[commit.agent] }}>● {commit.author}</span>
                                            <span>{commit.branch}</span>
                                            <span>{formatTimeRange(commit.timestamp)}</span>
                                        </div>
                                        {commit.files && (
                                            <div className="commit-tooltip-files">
                                                {commit.files.map(f => (
                                                    <div key={f} className="commit-tooltip-file">📄 {f}</div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Playback Controls */}
            <div className="timeline-controls">
                <button className="timeline-ctrl-btn" onClick={() => { setPlayHead(0); setPlaying(false); }}>
                    <SkipBackIcon />
                </button>
                <button
                    className={`timeline-ctrl-btn ${playing ? 'active' : ''}`}
                    onClick={() => setPlaying(!playing)}
                >
                    {playing ? <PauseIcon /> : <PlayIcon />}
                </button>
                <button className="timeline-ctrl-btn" onClick={() => { setPlayHead(commits.length - 1); setPlaying(false); }}>
                    <SkipFwdIcon />
                </button>

                <div className="timeline-scrubber" onClick={e => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const pct = (e.clientX - rect.left) / rect.width;
                    setPlayHead(Math.round(pct * (commits.length - 1)));
                    setPlaying(false);
                }}>
                    <div className="timeline-scrubber-fill" style={{ width: `${(playHead / (commits.length - 1)) * 100}%` }} />
                    <div className="timeline-scrubber-head" style={{ left: `${(playHead / (commits.length - 1)) * 100}%` }} />
                </div>

                <span className="timeline-range-label">
                    {commits[playHead]?.hash.slice(0, 7)} • {formatTimestamp(commits[playHead]?.timestamp || '')}
                </span>

                <div style={{ marginLeft: 'auto', display: 'flex', gap: '2px' }}>
                    <button className="timeline-ctrl-btn" onClick={() => setZoom(z => Math.max(0.5, z - 0.25))}>
                        <ZoomOutIcon />
                    </button>
                    <button className="timeline-ctrl-btn" onClick={() => setZoom(z => Math.min(2, z + 0.25))}>
                        <ZoomInIcon />
                    </button>
                </div>
            </div>
        </div>
    );
}
