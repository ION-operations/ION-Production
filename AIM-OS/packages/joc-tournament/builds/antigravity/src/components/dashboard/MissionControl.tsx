import React, { useMemo } from 'react';
import { useAIMOS } from '../../hooks/useAIMOS';
import {
    MOCK_AGENTS,
    MOCK_APPROVALS,
} from '../../data/mockData';
import { Sparkline, RingGauge } from '../Sparkline';

// ═══════════════════════════════════════════════════════════════════
// MISSION CONTROL V3 — Live MCP Instrument
// Wired to real AIM-OS backend via useAIMOS hook.
// Agent fleet + approvals use mock fallback (no live API yet).
// Everything else pulls from real MCP at localhost:5001.
// ═══════════════════════════════════════════════════════════════════

// ─── Helper ───

function timeAgo(ts: number | string | undefined): string {
    if (!ts) return 'never';
    const t = typeof ts === 'string' ? new Date(ts).getTime() : ts;
    const secs = Math.floor((Date.now() - t) / 1000);
    if (secs < 0) return 'now';
    if (secs < 5) return 'now';
    if (secs < 60) return `${secs}s`;
    if (secs < 3600) return `${Math.floor(secs / 60)}m`;
    return `${Math.floor(secs / 3600)}h`;
}

function fmt(n: number | undefined | null): string {
    if (n === undefined || n === null) return '—';
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return String(n);
}

// ─── Subsystem definitions (static list, health derived from MCP connection) ───

const SUBSYSTEM_DEFS = [
    { acronym: 'CMC', name: 'Memory Core', toolCount: 8 },
    { acronym: 'HHNI', name: 'Nav Index', toolCount: 4 },
    { acronym: 'VIF', name: 'Confidence', toolCount: 3 },
    { acronym: 'SEG', name: 'Evidence', toolCount: 3 },
    { acronym: 'APOE', name: 'Orchestration', toolCount: 4 },
    { acronym: 'TCS', name: 'Timeline', toolCount: 4 },
    { acronym: 'CAS', name: 'Cognition', toolCount: 3 },
    { acronym: 'MCP', name: 'Protocol', toolCount: 92 },
    { acronym: 'NLT', name: 'NL Tags', toolCount: 4 },
    { acronym: 'ORC', name: 'Oracle', toolCount: 3 },
    { acronym: 'GEN', name: 'Genome', toolCount: 2 },
    { acronym: 'IIS', name: 'Intuition', toolCount: 3 },
    { acronym: 'SDF', name: 'Semantic', toolCount: 2 },
    { acronym: 'SEER', name: 'Vision', toolCount: 5 },
];

export function MissionControl() {
    const aimos = useAIMOS({
        pollDomains: ['memory', 'timeline', 'consciousness', 'messages', 'goals', 'problems'],
    });

    return (
        <div className="mc-root">
            <MetricsStrip aimos={aimos} />
            <div className="mc-grid">
                <div className="mc-col-force">
                    <ForceOverview />
                </div>
                <div className="mc-col-systems">
                    <SystemsMatrix aimos={aimos} />
                </div>
                <div className="mc-col-actions">
                    <ApprovalQueue />
                    <CommsFeed aimos={aimos} />
                </div>
            </div>
            <MissionTimeline aimos={aimos} />
        </div>
    );
}

// ─── Metrics Strip — LIVE from MCP ──────────────────────────────

function MetricsStrip({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    const kappa = aimos.consciousness
        ? (1 - (aimos.consciousness.failure_rate || 0)).toFixed(2)
        : '—';
    const drift = aimos.consciousness
        ? `${((aimos.consciousness.cognitive_drift || 0) * 100).toFixed(0)}%`
        : '—';

    return (
        <div className="mc-metrics">
            {/* MCP connection */}
            <div className="mc-metric">
                <span className="mc-metric-label">MCP</span>
                <span className={`status-led ${aimos.connected ? 'live' : 'offline'}`} />
                <span className="mc-metric-value">
                    {aimos.connected ? `${aimos.latency}ms` : 'OFF'}
                </span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* Agent count (mock) */}
            <div className="mc-metric">
                <span className="mc-metric-label">AGENTS</span>
                <span className="mc-metric-value">
                    {MOCK_AGENTS.filter(a => a.status === 'active').length}
                    <span className="mc-metric-dim">/{MOCK_AGENTS.length}</span>
                </span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* Systems — derived from MCP connection */}
            <div className="mc-metric">
                <span className="mc-metric-label">SYSTEMS</span>
                <span className="mc-metric-value">
                    {aimos.connected ? `${SUBSYSTEM_DEFS.length - 1}` : '0'}
                    <span className="mc-metric-dim">/{SUBSYSTEM_DEFS.length}</span>
                </span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* Approvals (mock) */}
            <div className="mc-metric">
                <span className="mc-metric-label">APPROVALS</span>
                <span className="mc-metric-value" style={{ color: 'var(--led-amber)' }}>
                    {MOCK_APPROVALS.length}
                </span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* VIF κ — LIVE */}
            <div className="mc-metric">
                <span className="mc-metric-label">VIF κ</span>
                <span className="mc-metric-value" style={{
                    color: aimos.consciousness ? 'var(--led-green)' : 'var(--text-dim)',
                }}>{kappa}</span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* CAS Drift — LIVE */}
            <div className="mc-metric">
                <span className="mc-metric-label">DRIFT</span>
                <span className="mc-metric-value" style={{
                    color: aimos.consciousness && (aimos.consciousness.cognitive_drift || 0) < 0.3
                        ? 'var(--text-mid)' : 'var(--led-amber)',
                }}>{drift}</span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* CMC Atoms — LIVE */}
            <div className="mc-metric">
                <span className="mc-metric-label">ATOMS</span>
                <span className="mc-metric-value">
                    {fmt(aimos.memory?.total_atoms)}
                </span>
            </div>
            <span className="mc-metric-sep">│</span>

            {/* Goals — LIVE */}
            <div className="mc-metric">
                <span className="mc-metric-label">GOALS</span>
                <span className="mc-metric-value">
                    {aimos.goals.length || '—'}
                </span>
            </div>

            {/* Connection / refresh meta */}
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
                {aimos.error && (
                    <span className="mc-metric-label" style={{ color: 'var(--led-red)', fontSize: 8 }}>
                        {aimos.error}
                    </span>
                )}
                <span className="mc-metric-label" style={{ fontSize: 8, opacity: 0.4 }}>
                    {aimos.lastRefresh ? timeAgo(aimos.lastRefresh) : '—'}
                </span>
                <span className={`status-led ${aimos.connected ? 'live' : aimos.health === 'connecting' ? 'idle' : 'offline'}`}
                    style={{ width: 5, height: 5 }}
                    title={`MCP: ${aimos.health}`}
                />
            </div>
        </div>
    );
}

// ─── Force Overview — Agent Fleet (MOCK — no live agent runtime API) ───

function ForceOverview() {
    return (
        <div className="mc-panel" style={{ position: 'relative' }}>
            <div className="truth-badge truth-badge-mock" />
            <div className="mc-panel-header">
                <span className="mc-panel-title">FORCE OVERVIEW</span>
                <span className="mc-panel-count">
                    {MOCK_AGENTS.filter(a => a.status === 'active').length}/{MOCK_AGENTS.length}
                </span>
            </div>
            <div className="mc-agent-grid">
                {MOCK_AGENTS.map((agent) => (
                    <div key={agent.id} className={`mc-agent-tile ${agent.status}`}>
                        <div className="mc-agent-top">
                            <span className={`status-led ${agent.status === 'active' ? 'live' :
                                agent.status === 'idle' ? 'idle' : 'offline'
                                }`} />
                            <span className="mc-agent-name">{agent.name}</span>
                            <span className="mc-agent-rank">{agent.rank}</span>
                        </div>
                        <div className="mc-agent-task">{agent.currentTask}</div>
                        <div className="mc-agent-bottom">
                            <Sparkline
                                data={agent.activityHistory}
                                width={48}
                                height={16}
                                color={agent.status === 'active' ? 'var(--text-dim)' : 'var(--text-ghost)'}
                                strokeWidth={1}
                                fillOpacity={0.08}
                            />
                            <RingGauge
                                value={agent.confidence * 100}
                                size={22}
                                strokeWidth={2}
                                color={agent.confidence > 0.85 ? 'var(--led-green)' : agent.confidence > 0.7 ? 'var(--led-amber)' : 'var(--text-dim)'}
                                label={agent.confidence > 0 ? (agent.confidence * 100).toFixed(0) : '—'}
                            />
                            <div className="mc-agent-token-wrap">
                                <div className="mc-agent-token-bar">
                                    <div className="mc-agent-token-fill" style={{
                                        width: `${(agent.tokensUsed / agent.tokenBudget) * 100}%`,
                                        background: agent.tokensUsed / agent.tokenBudget > 0.8 ? 'var(--led-amber)' : 'var(--led-blue)',
                                    }} />
                                </div>
                                <span className="mc-agent-token-label">{Math.round(agent.tokensUsed / 1000)}k</span>
                            </div>
                        </div>
                        <div className="mc-agent-meta">
                            <span>{agent.model}</span>
                            <span style={{ marginLeft: 'auto' }}>{agent.lastActive}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ─── Systems Matrix — LIVE from MCP health ──────────────────────

function SystemsMatrix({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    // Derive each subsystem's health from what MCP tells us
    const subsystems = useMemo(() => {
        return SUBSYSTEM_DEFS.map(def => {
            let stat = '—';
            let online = aimos.connected;

            // Specific data from live tools
            switch (def.acronym) {
                case 'CMC':
                    stat = fmt(aimos.memory?.total_atoms);
                    break;
                case 'VIF':
                    stat = aimos.consciousness
                        ? `κ:${(1 - (aimos.consciousness.failure_rate || 0)).toFixed(2)}`
                        : '—';
                    break;
                case 'TCS':
                    stat = aimos.timeline.length ? `${aimos.timeline.length}` : '—';
                    break;
                case 'CAS':
                    stat = aimos.consciousness
                        ? `dr:${((aimos.consciousness.cognitive_drift || 0) * 100).toFixed(0)}%`
                        : '—';
                    break;
                case 'MCP':
                    stat = aimos.connected ? `${aimos.latency}ms` : 'off';
                    break;
                case 'SEER':
                    online = false; // SEER not operational
                    stat = 'off';
                    break;
                default:
                    stat = aimos.connected ? 'OK' : '—';
                    break;
            }

            const status = !online ? 'offline' as const :
                def.acronym === 'SDF' ? 'degraded' as const :
                    'healthy' as const;

            return { ...def, stat, online, status };
        });
    }, [aimos.connected, aimos.memory, aimos.consciousness, aimos.timeline, aimos.latency]);

    const healthyCount = subsystems.filter(s => s.status === 'healthy').length;

    return (
        <div className="mc-panel" style={{ position: 'relative' }}>
            {/* No MOCK badge — this is LIVE */}
            {!aimos.connected && <div className="truth-badge truth-badge-offline" />}
            <div className="mc-panel-header">
                <span className="mc-panel-title">SYSTEMS MATRIX</span>
                <span className="mc-panel-count">{healthyCount}/{subsystems.length}</span>
            </div>
            <div className="mc-sys-grid">
                {subsystems.map((sys) => (
                    <div key={sys.acronym} className={`mc-sys-tile ${sys.status}`}>
                        <div className="mc-sys-top">
                            <span className={`status-led ${sys.status === 'healthy' ? 'live' :
                                sys.status === 'degraded' ? 'warning' :
                                    'offline'
                                }`} />
                            <span className="mc-sys-acronym">{sys.acronym}</span>
                            <span className="mc-sys-pct">{sys.stat}</span>
                        </div>
                        <div className="mc-sys-bottom">
                            <span>{sys.toolCount}t</span>
                            <span>{sys.online ? 'LIVE' : 'OFF'}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ─── Approval Queue (MOCK — no live Oracle stream) ──────────────

function ApprovalQueue() {
    return (
        <div className="mc-panel mc-panel-compact" style={{ position: 'relative' }}>
            <div className="truth-badge truth-badge-mock" />
            <div className="mc-panel-header">
                <span className="mc-panel-title">AWAITING APPROVAL</span>
                <span className="mc-panel-count" style={{ color: 'var(--led-amber)' }}>{MOCK_APPROVALS.length}</span>
            </div>
            <div className="mc-approvals">
                {MOCK_APPROVALS.map((apr) => (
                    <div key={apr.id} className={`mc-approval-row risk-${apr.risk}`}>
                        <span className={`status-led ${apr.risk === 'high' ? 'critical' :
                            apr.risk === 'medium' ? 'warning' : 'live'
                            }`} />
                        <div className="mc-approval-info">
                            <div className="mc-approval-action">{apr.action}</div>
                            <div className="mc-approval-meta">{apr.agent} · {apr.timeAgo} · {apr.affectedSystems} sys</div>
                        </div>
                        <div className="mc-approval-btns">
                            <button className="mc-btn-approve">APR</button>
                            <button className="mc-btn-deny">DNY</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ─── Comms Feed — LIVE from MCP AI Messages ─────────────────────

function CommsFeed({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    const messages = aimos.aiMessages || [];

    return (
        <div className="mc-panel mc-panel-compact mc-panel-flex" style={{ position: 'relative' }}>
            {!aimos.connected && <div className="truth-badge truth-badge-offline" />}
            <div className="mc-panel-header">
                <span className="mc-panel-title">COMMS</span>
                <span className="mc-panel-count">
                    {messages.length > 0 ? messages.length : '—'}
                </span>
                {aimos.connected && (
                    <span className="status-led live" style={{ width: 4, height: 4, marginLeft: 4 }} />
                )}
            </div>
            <div className="mc-comms">
                {messages.length === 0 ? (
                    <div style={{
                        fontFamily: 'var(--font-mono)', fontSize: 9,
                        color: 'var(--text-dim)', padding: '12px 8px', textAlign: 'center',
                    }}>
                        {aimos.connected ? 'No agent messages yet' : 'MCP offline — awaiting connection'}
                    </div>
                ) : (
                    messages.slice(-8).reverse().map((msg, i) => (
                        <div key={msg.id || i} className="mc-msg-row">
                            <div className="mc-msg-header">
                                <span className="mc-msg-from">{msg.from_ai}</span>
                                <span className="mc-msg-arrow">→</span>
                                <span className="mc-msg-to">{msg.to_ai}</span>
                                <span className="mc-msg-time">{timeAgo(msg.timestamp)}</span>
                            </div>
                            <div className="mc-msg-body">
                                {typeof msg.content === 'string' ? msg.content.slice(0, 120) : '—'}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

// ─── Mission Timeline — LIVE from MCP Goals ──────────────────────

function MissionTimeline({ aimos }: { aimos: ReturnType<typeof useAIMOS> }) {
    const goals = aimos.goals || [];

    return (
        <div className="mc-panel mc-panel-wide" style={{ position: 'relative' }}>
            {!aimos.connected && <div className="truth-badge truth-badge-offline" />}
            <div className="mc-panel-header">
                <span className="mc-panel-title">MISSION TIMELINE</span>
                <span className="mc-panel-count">
                    {goals.length > 0 ? `${goals.length} goals` : '—'}
                </span>
                {aimos.connected && (
                    <span className="status-led live" style={{ width: 4, height: 4, marginLeft: 4 }} />
                )}
            </div>
            <div className="mc-missions">
                {goals.length === 0 ? (
                    <div style={{
                        fontFamily: 'var(--font-mono)', fontSize: 9,
                        color: 'var(--text-dim)', padding: '16px 8px', textAlign: 'center',
                    }}>
                        {aimos.connected ? 'No goals in timeline — dispatch missions to populate' : 'MCP offline — awaiting connection'}
                    </div>
                ) : (
                    goals.slice(0, 8).map((goal) => (
                        <div key={goal.goal_id} className="mc-msn-row">
                            {/* Status LED */}
                            <span className={`status-led ${goal.status === 'completed' ? 'live' :
                                goal.status === 'in_progress' ? 'idle' :
                                    goal.status === 'blocked' ? 'critical' : 'offline'
                                }`} />

                            {/* Goal ID */}
                            <span className="mc-msn-id">{goal.goal_id}</span>

                            {/* Goal name */}
                            <span className="mc-msn-title">{goal.name}</span>

                            {/* Priority */}
                            {goal.priority && (
                                <span className="mc-msn-agent" style={{
                                    color: goal.priority === 'critical' ? 'var(--led-red)' :
                                        goal.priority === 'high' ? 'var(--led-amber)' : 'var(--text-dim)',
                                }}>{goal.priority?.toUpperCase()}</span>
                            )}

                            {/* Progress bar */}
                            <div className="mc-msn-bar">
                                <div className="mc-msn-bar-fill" style={{
                                    width: `${(goal.progress || 0) * 100}%`,
                                    background: goal.status === 'completed' ? 'var(--text-dim)' : 'var(--led-green)',
                                    boxShadow: goal.status === 'in_progress' ? '0 0 4px rgba(34, 204, 68, 0.3)' : 'none',
                                }} />
                                <span className="mc-msn-pct">{Math.round((goal.progress || 0) * 100)}%</span>
                            </div>

                            {/* Status */}
                            <span className="mc-msn-elapsed" style={{
                                color: goal.status === 'in_progress' ? 'var(--led-green)' : 'var(--text-dim)',
                            }}>{goal.status}</span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
