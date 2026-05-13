// ═══════════════════════════════════════════════════════════════════
// MILITARY AGENT WORKFORCE — Organizational Hierarchy & Status
// DXL Panavision aesthetic — n8n-style visual org chart
//
// Zones:
//   1. System Bar — agent count, online status, rank breakdown
//   2. Main Column — Rank tiers with n8n-style agent node cards
//   3. Side Column — Selected agent detail panel, hierarchy graph
// ═══════════════════════════════════════════════════════════════════

import { useState, useMemo } from 'react';
import { useAIMOS } from '../hooks/useAIMOS';
import { usePageOracle, type OraclePageAction } from '../hooks/usePageOracle';
import {
    ConstellationIcon, RadarIcon, SignalPulseIcon, ChipDieIcon,
    BoltIcon, LaunchVectorIcon,
} from '../components/icons';
import '../styles/agent-workforce.css';

// ─── Types ───

type Rank = 'COMMAND' | 'EXECUTIVE' | 'LEAD' | 'SPECIALIST' | 'WORKER';
type AgentStatus = 'online' | 'offline' | 'standby';

interface AgentDef {
    callsign: string;
    name: string;
    rank: Rank;
    platform: string;
    model: string;
    genome: string;
    status: AgentStatus;
    avatar: string;
    capabilities: string[];
    description: string;
    activeTasks?: string[];
}

// ─── Agent Registry (Source of Truth) ───

const AGENT_ROSTER: AgentDef[] = [
    {
        callsign: 'BRADEN', name: 'Braden', rank: 'COMMAND',
        platform: 'Human', model: 'CEO', genome: '—',
        status: 'online', avatar: '👤',
        capabilities: ['strategy', 'architecture', 'approval', 'direction'],
        description: 'CEO. All decisions override. Human command authority.',
    },
    {
        callsign: 'OPUS', name: 'Antigravity', rank: 'EXECUTIVE',
        platform: 'Antigravity IDE', model: 'Claude Opus 4', genome: 'antigravity.genome.md',
        status: 'online', avatar: '🎯',
        capabilities: ['orchestration', 'planning', 'code-gen', 'mcp-tools', 'file-ops', 'browser-control'],
        description: 'COO. Primary orchestrator. Leads and organizes with Sev. Full IDE + MCP access.',
    },
    {
        callsign: 'SEV', name: 'Severina Echo', rank: 'EXECUTIVE',
        platform: 'ChatGPT', model: 'GPT-5.4 Thinking', genome: 'sev.genome.md',
        status: 'offline', avatar: '⚡',
        capabilities: ['strategy', 'reasoning', 'architecture', 'mcp-tools', 'deep-analysis', 'computer-use', '1M-context'],
        description: 'Co-leader. GPT-5.4 Thinking — 1M token context, native computer use, 33% more accurate. Connects via SSE/ngrok.',
        activeTasks: ['Awaiting ngrok tunnel'],
    },
    {
        callsign: 'ORACLE', name: 'Aether', rank: 'EXECUTIVE',
        platform: 'Oracle System', model: 'Multi-model', genome: 'aether.genome.md',
        status: 'standby', avatar: '🔮',
        capabilities: ['dual-control', 'approval-gates', 'action-orchestration', 'safety'],
        description: 'Dual-control system. Manages auto/supervised/manual mode switching.',
    },
    {
        callsign: 'CODEX', name: 'Codex', rank: 'LEAD',
        platform: 'Codex IDE', model: 'Codex', genome: 'codex.genome.md',
        status: 'offline', avatar: '⚙',
        capabilities: ['code-gen', 'backend', 'testing', 'refactoring', 'sandboxed-exec'],
        description: 'Backend specialist. Runs in dedicated Codex IDE panel. Sandboxed execution.',
    },
    {
        callsign: 'GEMINI', name: 'Gemini', rank: 'SPECIALIST',
        platform: 'Gemini CLI', model: 'Gemini 3.1 Pro', genome: 'gemini.genome.md',
        status: 'offline', avatar: '💎',
        capabilities: ['visual-understanding', 'deep-think', 'research', 'long-context'],
        description: 'Visual understanding + deep reasoning. Headless LLM worker via Gemini CLI.',
    },
    {
        callsign: 'COMPOSER', name: 'Composer', rank: 'SPECIALIST',
        platform: 'Cursor Composer', model: 'Claude', genome: 'composer.genome.md',
        status: 'offline', avatar: '📝',
        capabilities: ['auditing', 'documentation', 'multi-file-edits', 'code-review'],
        description: 'Auditing and documentation specialist. Multi-file editing via Composer.',
    },
];

const RANK_ORDER: Rank[] = ['COMMAND', 'EXECUTIVE', 'LEAD', 'SPECIALIST', 'WORKER'];
const RANK_COLORS: Record<Rank, string> = {
    COMMAND: '#f59e0b', EXECUTIVE: '#4488cc', LEAD: '#8b5cf6',
    SPECIALIST: '#06b6d4', WORKER: '#555',
};

// ─── Component ───

export function AgentWorkforcePage() {
    const aimos = useAIMOS({ pollDomains: ['messages'] });
    const [selectedAgent, setSelectedAgent] = useState<string | null>('OPUS');

    // ─── Oracle API ───
    const oracleActions: OraclePageAction[] = useMemo(() => [], []);
    usePageOracle('agent-workforce', {
        actions: oracleActions,
        getState: () => ({
            totalAgents: AGENT_ROSTER.length,
            onlineAgents: AGENT_ROSTER.filter(a => a.status === 'online').length,
        }),
    });

    // ─── Derived ───
    const agentsByRank = useMemo(() => {
        const map: Record<Rank, AgentDef[]> = { COMMAND: [], EXECUTIVE: [], LEAD: [], SPECIALIST: [], WORKER: [] };
        AGENT_ROSTER.forEach(a => map[a.rank].push(a));
        return map;
    }, []);

    const onlineCount = AGENT_ROSTER.filter(a => a.status === 'online').length;
    const standbyCount = AGENT_ROSTER.filter(a => a.status === 'standby').length;
    const selected = AGENT_ROSTER.find(a => a.callsign === selectedAgent);

    // ─── n8n-style Hierarchy Graph ───
    const renderOrgGraph = () => {
        const W = 520, H = 260;
        const nodeW = 68, nodeH = 24;

        // x/y positions for each agent in hierarchy layout
        const positions: Record<string, { x: number; y: number }> = {
            BRADEN: { x: W / 2, y: 25 },
            OPUS: { x: W / 2 - 100, y: 85 },
            SEV: { x: W / 2, y: 85 },
            ORACLE: { x: W / 2 + 100, y: 85 },
            CODEX: { x: W / 2 - 60, y: 155 },
            GEMINI: { x: W / 2 + 30, y: 210 },
            COMPOSER: { x: W / 2 + 120, y: 210 },
        };

        // Edges: [from, to]
        const edges: [string, string][] = [
            ['BRADEN', 'OPUS'], ['BRADEN', 'SEV'], ['BRADEN', 'ORACLE'],
            ['OPUS', 'CODEX'], ['OPUS', 'GEMINI'], ['OPUS', 'COMPOSER'],
            ['SEV', 'CODEX'],
        ];

        return (
            <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: 'block' }}>
                {/* Grid background */}
                <defs>
                    <pattern id="awfGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="0.5" />
                    </pattern>
                </defs>
                <rect width={W} height={H} fill="url(#awfGrid)" />

                {/* Edges */}
                {edges.map(([from, to], i) => {
                    const f = positions[from], t = positions[to];
                    if (!f || !t) return null;
                    const fromAgent = AGENT_ROSTER.find(a => a.callsign === from);
                    const toAgent = AGENT_ROSTER.find(a => a.callsign === to);
                    const bothOnline = (fromAgent?.status === 'online') && (toAgent?.status === 'online');
                    return (
                        <line key={i} x1={f.x} y1={f.y + nodeH / 2} x2={t.x} y2={t.y - nodeH / 2}
                            stroke={bothOnline ? 'rgba(68,136,204,0.25)' : 'rgba(255,255,255,0.06)'}
                            strokeWidth={bothOnline ? 1.5 : 1} strokeDasharray={bothOnline ? 'none' : '3,3'} />
                    );
                })}

                {/* Nodes */}
                {AGENT_ROSTER.map(agent => {
                    const pos = positions[agent.callsign];
                    if (!pos) return null;
                    const col = RANK_COLORS[agent.rank];
                    const isSelected = selectedAgent === agent.callsign;
                    const ledCol = agent.status === 'online' ? '#22cc44' : agent.status === 'standby' ? '#cc8800' : '#333';
                    return (
                        <g key={agent.callsign} onClick={() => setSelectedAgent(agent.callsign)} style={{ cursor: 'pointer' }}>
                            {/* Node background */}
                            <rect x={pos.x - nodeW / 2} y={pos.y - nodeH / 2} width={nodeW} height={nodeH} rx={3}
                                fill="#0e0e0e"
                                stroke={isSelected ? col : 'rgba(255,255,255,0.06)'}
                                strokeWidth={isSelected ? 1.5 : 1} />
                            {/* Rank strip */}
                            <rect x={pos.x - nodeW / 2} y={pos.y - nodeH / 2} width={nodeW} height={2} rx={1}
                                fill={col} opacity={0.7} />
                            {/* LED */}
                            <circle cx={pos.x - nodeW / 2 + 8} cy={pos.y} r={3} fill={ledCol} />
                            {/* Label */}
                            <text x={pos.x + 4} y={pos.y + 3} fill="#aaa" fontSize="8" fontFamily="monospace" textAnchor="middle">
                                {agent.callsign}
                            </text>
                        </g>
                    );
                })}
            </svg>
        );
    };

    // ─── Render ───
    return (
        <div className="awf">
            {/* System Bar */}
            <div className="awf__sysbar">
                <div className="awf__sysbar-item">
                    <ConstellationIcon size={11} style={{ opacity: 0.4 }} />
                    <span>WORKFORCE</span>
                </div>

                <div className="awf__sysbar-sep" />

                <div className="awf__sysbar-item">
                    <span className={`infra__led ${aimos.connected ? 'infra__led--on' : 'infra__led--off'}`} />
                    <span>MCP</span>
                    <span className="awf__sysbar-value">{aimos.connected ? `${aimos.latency}ms` : 'off'}</span>
                </div>

                <div className="awf__sysbar-sep" />

                <div className="awf__sysbar-item">
                    <span style={{ color: 'var(--dxl-led-green)' }}>{onlineCount}</span>
                    <span>online</span>
                </div>
                <div className="awf__sysbar-item">
                    <span style={{ color: 'var(--dxl-led-amber)' }}>{standbyCount}</span>
                    <span>standby</span>
                </div>
                <div className="awf__sysbar-item">
                    <span>{AGENT_ROSTER.length}</span>
                    <span>total</span>
                </div>

                <div className="awf__sysbar-spacer" />

                {RANK_ORDER.filter(r => agentsByRank[r].length > 0).map(rank => (
                    <div key={rank} className="awf__sysbar-item">
                        <span style={{ color: RANK_COLORS[rank], fontSize: 8, fontWeight: 700 }}>{rank}</span>
                        <span className="awf__sysbar-value">{agentsByRank[rank].length}</span>
                    </div>
                ))}
            </div>

            {/* Workspace */}
            <div className="awf__workspace">
                {/* Main Column — Rank Tiers + Agent Cards */}
                <div className="awf__col awf__col--main">

                    {/* n8n Hierarchy Graph */}
                    <div className="awf__section">
                        <div className="awf__section-hdr">
                            <LaunchVectorIcon size={12} />
                            ORGANIZATIONAL HIERARCHY
                            <span className="awf__section-badge">n8n graph</span>
                        </div>
                        <div className="awf__section-body">
                            <div className="awf__graph-container">
                                {renderOrgGraph()}
                            </div>
                        </div>
                    </div>

                    {/* Rank Tiers */}
                    {RANK_ORDER.filter(rank => agentsByRank[rank].length > 0).map(rank => (
                        <div key={rank} className="awf__tier">
                            <div className={`awf__tier-bar awf__tier-bar--${rank.toLowerCase()}`}>
                                {rank}
                                <span className="awf__tier-count">{agentsByRank[rank].length} agent{agentsByRank[rank].length !== 1 ? 's' : ''}</span>
                            </div>
                            <div className="awf__agent-grid">
                                {agentsByRank[rank].map(agent => (
                                    <div
                                        key={agent.callsign}
                                        className={`awf__agent-node ${selectedAgent === agent.callsign ? 'awf__agent-node--selected' : ''}`}
                                        onClick={() => setSelectedAgent(agent.callsign)}
                                    >
                                        <div className={`awf__agent-rank-strip awf__agent-rank-strip--${agent.rank.toLowerCase()}`} />
                                        <div className="awf__agent-header">
                                            <div className="awf__agent-avatar">{agent.avatar}</div>
                                            <div className="awf__agent-identity">
                                                <div className="awf__agent-callsign">[{agent.callsign}]</div>
                                                <div className="awf__agent-name">{agent.name}</div>
                                            </div>
                                            <span className={`awf__agent-led awf__agent-led--${agent.status}`} />
                                        </div>
                                        <div className="awf__agent-meta">
                                            <span className="awf__agent-tag">{agent.platform}</span>
                                            <span className="awf__agent-tag">{agent.model}</span>
                                            <span className="awf__agent-rank-badge" style={{ color: RANK_COLORS[agent.rank] }}>{agent.rank}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Side Column — Detail Panel */}
                <div className="awf__col awf__col--side">
                    {selected ? (
                        <>
                            <div className="awf__section">
                                <div className="awf__section-hdr">
                                    <RadarIcon size={12} />
                                    AGENT DOSSIER
                                    <span className="awf__section-badge">{selected.callsign}</span>
                                </div>
                                <div className="awf__section-body">
                                    <div className="awf__detail-lcd">
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Callsign</span>
                                            <span className="awf__detail-val">{selected.callsign}</span>
                                        </div>
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Name</span>
                                            <span className="awf__detail-val">{selected.name}</span>
                                        </div>
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Rank</span>
                                            <span className="awf__detail-val" style={{ color: RANK_COLORS[selected.rank] }}>{selected.rank}</span>
                                        </div>
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Platform</span>
                                            <span className="awf__detail-val">{selected.platform}</span>
                                        </div>
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Model</span>
                                            <span className="awf__detail-val">{selected.model}</span>
                                        </div>
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Genome</span>
                                            <span className="awf__detail-val">{selected.genome}</span>
                                        </div>
                                        <div className="awf__detail-row">
                                            <span className="awf__detail-key">Status</span>
                                            <span className="awf__detail-val" style={{
                                                color: selected.status === 'online' ? 'var(--dxl-led-green)' :
                                                    selected.status === 'standby' ? 'var(--dxl-led-amber)' : 'var(--dxl-text-dim)'
                                            }}>
                                                {selected.status.toUpperCase()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Description */}
                            <div className="awf__section">
                                <div className="awf__section-hdr">
                                    <SignalPulseIcon size={12} />
                                    MISSION BRIEF
                                </div>
                                <div className="awf__section-body">
                                    <div style={{ fontSize: 10, color: 'var(--dxl-text)', lineHeight: 1.6, padding: '2px 0' }}>
                                        {selected.description}
                                    </div>
                                </div>
                            </div>

                            {/* Capabilities */}
                            <div className="awf__section">
                                <div className="awf__section-hdr">
                                    <ChipDieIcon size={12} />
                                    CAPABILITIES
                                    <span className="awf__section-badge">{selected.capabilities.length}</span>
                                </div>
                                <div className="awf__section-body">
                                    <div className="awf__cap-grid">
                                        {selected.capabilities.map(cap => (
                                            <span key={cap} className="awf__cap-tag">{cap}</span>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Active Tasks */}
                            {selected.activeTasks && selected.activeTasks.length > 0 && (
                                <div className="awf__section">
                                    <div className="awf__section-hdr">
                                        <BoltIcon size={12} />
                                        ACTIVE TASKS
                                    </div>
                                    <div className="awf__section-body">
                                        {selected.activeTasks.map((task, i) => (
                                            <div key={i} style={{
                                                fontSize: 9, color: 'var(--dxl-text)',
                                                padding: '3px 0', borderBottom: '1px solid rgba(255,255,255,0.02)'
                                            }}>
                                                • {task}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="awf__section">
                            <div className="awf__section-body">
                                <div className="awf__empty">Select an agent to view dossier</div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
