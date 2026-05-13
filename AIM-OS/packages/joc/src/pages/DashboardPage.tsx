// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD — AIM-OS Mission Control Overview
// The face of a 13-subsystem AI operating system.
//
// Zones:
//   1. System Bar — Oracle mode, MCP/BAS/CMC/CAS vitals, cost, alerts
//   2. Left Column — Agent genome fleet, AIM-OS subsystem status, Oracle action log, upcoming
//   3. Right Column — Dispatch composer, active missions, unified results feed
// ═══════════════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useJOCStore, type AISession } from '../store/jocStore';
import { useAIMOS } from '../hooks/useAIMOS';
import { usePageOracle, type OraclePageAction } from '../hooks/usePageOracle';
import { useOracleStore } from '../store/oracleStore';
import { useAgentGenomeStore } from '../store/agentGenomeStore';
import { useSessionStore } from '../store/sessionStore';
import { useVaultStore } from '../store/vaultStore';
import { useCalendarStore } from '../store/calendarStore';
import { useNotificationStore } from '../store/notificationStore';
import * as basClient from '../services/basClient';
import {
    RadarIcon, ConstellationIcon, LaunchVectorIcon, DispatchIcon,
    StatusDotIcon, SatelliteIcon, AutomationIcon, BoltIcon,
    RobotHeadIcon, ClipboardListIcon, BellAlertIcon, RefreshCycleIcon,
    ShieldKeyIcon, CalendarMarkIcon,
} from '../components/icons';
import '../styles/dashboard.css';

// ─── Types ───

interface LiveProvider {
    name: string;
    icon: string;
    available: boolean;
    selectors: number;
}

const PROVIDER_ICONS: Record<string, string> = {
    chatgpt: 'GPT', gemini: 'GEM', claude: 'CLD', perplexity: 'PPX', ollama: 'OLL', deepseek: 'DSK',
};

// ─── Helpers ───

function fmt(n: number | undefined | null): string {
    if (n === undefined || n === null) return '—';
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return String(n);
}

function fmtCost(n: number | undefined | null): string {
    if (n === undefined || n === null) return '$—';
    return `$${n.toFixed(2)}`;
}

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

function clockTime(ts: number | string | undefined): string {
    if (!ts) return '—';
    const d = typeof ts === 'string' ? new Date(ts) : new Date(ts);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });
}

function confidenceColor(v: number): string {
    if (v >= 0.9) return '#4CAF50';
    if (v >= 0.7) return '#FF9800';
    return '#f44336';
}

// ─── Component ───

export function DashboardPage() {
    // ─── Store connections ───
    const { sessions, missions, activity, addTab } = useJOCStore();
    const aimos = useAIMOS({ pollDomains: ['memory', 'timeline', 'consciousness', 'messages', 'goals', 'problems'] });
    const oracle = useOracleStore();
    const genomes = useAgentGenomeStore();
    const sessionStore = useSessionStore();
    const vault = useVaultStore();
    const calendar = useCalendarStore();
    const notifications = useNotificationStore();

    // ─── Oracle API Registration ───
    const oracleActions: OraclePageAction[] = useMemo(() => [
        {
            id: 'dashboard.refreshAll',
            label: 'Refresh All Data',
            system: 'sessions' as const,
            description: 'Refresh MCP data and BAS provider status',
            minPermission: 'supervised' as const,
            execute: async () => {
                await aimos.refreshAll();
                await refreshBAS();
                return { success: true, message: 'Dashboard data refreshed' };
            },
        },
        {
            id: 'dashboard.cycleOracleMode',
            label: 'Cycle Oracle Mode',
            system: 'dispatch' as const,
            description: 'Cycle through Oracle autonomy modes',
            minPermission: 'manual' as const,
            execute: async () => {
                cycleOracleMode();
                return { success: true, message: `Oracle mode: ${oracle.mode}` };
            },
        },
    ], [aimos, oracle.mode]);

    usePageOracle('dashboard', {
        actions: oracleActions,
        getState: () => ({
            mcpConnected: aimos.connected,
            basOnline,
            sessionCount: sessions.length,
            activeSessions: sessions.filter(s => s.status === 'active').length,
            oracleMode: oracle.mode,
            agentCount: genomes.agents.length,
            totalAtoms: aimos.memory?.total_atoms ?? 0,
        }),
    });

    // ─── BAS State ───
    const [basOnline, setBASOnline] = useState(false);
    const [liveProviders, setLiveProviders] = useState<LiveProvider[]>([]);
    const [basLatency, setBASLatency] = useState<number | null>(null);
    const pollRef = useRef<ReturnType<typeof setInterval>>();

    const refreshBAS = useCallback(async () => {
        try {
            const start = performance.now();
            const online = await basClient.isBASOnline();
            setBASLatency(Math.round(performance.now() - start));
            setBASOnline(online);
            if (online) {
                const providers = await basClient.getProviders();
                setLiveProviders(providers.map(p => ({
                    name: p.name,
                    icon: PROVIDER_ICONS[p.name.toLowerCase()] || '◆',
                    available: true,
                    selectors: p.inputSelectors + p.responseSelectors,
                })));
            } else {
                setLiveProviders([]);
            }
        } catch {
            setBASOnline(false);
            setLiveProviders([]);
        }
    }, []);

    useEffect(() => {
        refreshBAS();
        pollRef.current = setInterval(refreshBAS, 30000);
        return () => { if (pollRef.current) clearInterval(pollRef.current); };
    }, [refreshBAS]);

    // ─── Quick Dispatch State ───
    const [dispatchText, setDispatchText] = useState('');
    const [selectedTargets, setSelectedTargets] = useState<Set<string>>(new Set(['all']));
    const [strategy, setStrategy] = useState<'parallel' | 'consensus' | 'sequential'>('parallel');

    const toggleTarget = (target: string) => {
        setSelectedTargets(prev => {
            const next = new Set(prev);
            if (target === 'all') return new Set(['all']);
            next.delete('all');
            if (next.has(target)) next.delete(target);
            else next.add(target);
            return next.size === 0 ? new Set(['all']) : next;
        });
    };

    // ─── Oracle mode cycling ───
    const cycleOracleMode = () => {
        const modes = ['auto', 'supervised', 'manual', 'offline'] as const;
        const idx = modes.indexOf(oracle.mode as any);
        oracle.setMode(modes[(idx + 1) % modes.length]);
    };

    // ─── Derived data ───
    const activeGenomes = genomes.agents.filter(a => a.status === 'active' || a.status === 'executing');
    const pendingApprovals = oracle.actionLog.filter(a => a.status === 'pending');
    const recentActions = oracle.actionLog.slice(-6).reverse();
    const vaultEntries = Object.values(vault.entries || {});
    const totalCostToday = vaultEntries.reduce((sum: number, e: any) => sum + (e.usageStats?.costToday || 0), 0);
    const unreadCount = notifications.notifications.filter(n => !n.read).length;
    // calendarStore.events is a Record<string, ScheduledEvent>, not an array
    const calendarEventsArray = Object.values(calendar.events || {});
    const upcomingEvents = calendarEventsArray
        .filter((e: any) => e.status === 'scheduled' || e.status === 'active')
        .sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime())
        .slice(0, 3);

    // Session pipeline awareness
    const sessionStates = Object.entries(sessionStore.sessions || {});
    const activeSessions = sessionStates.filter(([, s]) => s.status !== 'disconnected');

    // Unified feed: combine notifications, oracle actions, AI messages, activity
    const feedItems = useMemo(() => {
        const items: { time: number; type: string; icon: string; text: string; source: string }[] = [];

        // Notifications (field is `type` not `severity`)
        notifications.notifications.slice(-8).forEach(n => {
            items.push({ time: n.timestamp || Date.now(), type: 'notification', icon: n.type === 'error' ? '🔴' : n.type === 'warning' ? '🟡' : '💬', text: n.message || n.title, source: 'System' });
        });

        // AI messages
        (aimos.aiMessages || []).slice(-5).forEach((m: any) => {
            items.push({ time: new Date(m.timestamp || Date.now()).getTime(), type: 'ai_message', icon: '🤖', text: typeof m.content === 'string' ? m.content.slice(0, 100) : String(m.content || '').slice(0, 100), source: m.from_ai || 'AI' });
        });

        // Oracle action log (timestamps are ISO strings)
        oracle.actionLog.slice(-5).forEach(a => {
            const ts = typeof a.timestamp === 'string' ? new Date(a.timestamp).getTime() : Date.now();
            items.push({ time: ts, type: 'oracle', icon: '⚡', text: a.detail || a.action || 'Oracle action', source: 'Oracle' });
        });

        // Activity log (ActivityItem has: id, time, text, type)
        (activity || []).slice(-5).forEach(a => {
            items.push({ time: Date.now(), type: 'activity', icon: '📋', text: a.text || 'Activity', source: a.type || 'JOC' });
        });

        return items.sort((a, b) => b.time - a.time).slice(0, 15);
    }, [notifications.notifications, aimos.aiMessages, oracle.actionLog, activity]);

    // AIM-OS subsystem status grid
    const subsystems = [
        { name: 'CMC', stat: fmt(aimos.memory?.total_atoms), online: aimos.connected },
        { name: 'HHNI', stat: aimos.connected ? '✓' : '—', online: aimos.connected },
        { name: 'VIF', stat: aimos.consciousness ? `κ:${(1 - (aimos.consciousness.failure_rate || 0)).toFixed(2)}` : '—', online: aimos.connected },
        { name: 'SEG', stat: aimos.connected ? '✓' : '—', online: aimos.connected },
        { name: 'APOE', stat: aimos.connected ? '✓' : '—', online: aimos.connected },
        { name: 'SDF', stat: aimos.connected ? '✓' : '—', online: aimos.connected },
        { name: 'TCS', stat: aimos.timeline.length ? `${aimos.timeline.length}` : '—', online: aimos.connected },
        { name: 'CAS', stat: aimos.consciousness ? `drift:${((aimos.consciousness.cognitive_drift || 0) * 100).toFixed(0)}%` : '—', online: aimos.connected },
        { name: 'SCOR', stat: aimos.connected ? '✓' : '—', online: aimos.connected },
        { name: 'IIS', stat: aimos.connected ? '✓' : '—', online: aimos.connected },
        { name: 'BAS', stat: basOnline ? `${basLatency}ms` : 'off', online: basOnline },
        { name: 'MCP', stat: aimos.connected ? `${aimos.latency}ms` : 'off', online: aimos.connected },
    ];

    // ─── Render ───
    return (
        <div className="dash">
            {/* ═══════════════════════════════════════
                ZONE 1: System Status Bar
                ═══════════════════════════════════════ */}
            <div className="dash__sysbar">
                {/* Oracle Mode */}
                <div className="dash__sysbar-item dash__sysbar-item--oracle" onClick={cycleOracleMode} title={`Mode: ${oracle.mode} — click to cycle`}>
                    <span style={{ fontSize: '9px', color: '#555' }}>ORACLE</span>
                    <span className={`dash__mode-badge dash__mode-badge--${oracle.mode}`}>
                        {oracle.mode}
                    </span>
                    {oracle.actionsPerMinute > 0 && (
                        <span style={{ fontSize: '8px', color: '#444' }}>
                            {oracle.actionsPerMinute.toFixed(1)}/m
                        </span>
                    )}
                </div>

                <div className="dash__sysbar-sep" />

                {/* MCP */}
                <div className="dash__sysbar-item">
                    <span className={`dash__led ${aimos.connected ? 'dash__led--on' : 'dash__led--off'}`} />
                    <SatelliteIcon size={11} style={{ opacity: 0.4 }} />
                    <span style={{ color: '#555' }}>MCP</span>
                    <span style={{ color: aimos.connected ? '#888' : '#444' }}>{aimos.connected ? `${aimos.latency}ms` : 'off'}</span>
                </div>

                {/* BAS */}
                <div className="dash__sysbar-item">
                    <span className={`dash__led ${basOnline ? 'dash__led--on' : 'dash__led--off'}`} />
                    <AutomationIcon size={11} style={{ opacity: 0.4 }} />
                    <span style={{ color: '#555' }}>BAS</span>
                    <span style={{ color: basOnline ? '#888' : '#444' }}>{basOnline ? `${basLatency}ms` : 'off'}</span>
                </div>

                <div className="dash__sysbar-sep" />

                {/* CMC Atoms */}
                <div className="dash__sysbar-item">
                    <span className="dash__sysbar-label">Atoms</span>
                    <span className="dash__sysbar-value">{fmt(aimos.memory?.total_atoms)}</span>
                </div>

                {/* Consciousness */}
                {aimos.consciousness && (
                    <div className="dash__sysbar-item">
                        <span style={{ color: '#555' }}>DRIFT</span>
                        <span style={{
                            color: (aimos.consciousness.cognitive_drift || 0) < 0.3 ? 'var(--dxl-led-green)' : 'var(--dxl-led-amber)'
                        }}>
                            {((aimos.consciousness.cognitive_drift || 0) * 100).toFixed(0)}%
                        </span>
                    </div>
                )}

                <div className="dash__sysbar-sep" />

                {/* Cost */}
                <div className="dash__sysbar-item">
                    <span className="dash__sysbar-label">Cost</span>
                    <span className="dash__sysbar-value">{fmtCost(totalCostToday)}</span>
                </div>

                {/* Goals */}
                <div className="dash__sysbar-item">
                    <span className="dash__sysbar-label">Goals</span>
                    <span className="dash__sysbar-value">{aimos.goals.length || '—'}</span>
                </div>

                {/* Alerts / Pending */}
                {(unreadCount > 0 || pendingApprovals.length > 0) && (
                    <>
                        <div className="dash__sysbar-sep" />
                        <div className="dash__sysbar-item">
                            {pendingApprovals.length > 0 && (
                                <span style={{ color: 'var(--dxl-led-amber)', fontSize: '9px' }}>
                                    <span className="dash__led dash__led--warn" style={{ marginRight: 3 }} />
                                    {pendingApprovals.length} PEND
                                </span>
                            )}
                            {unreadCount > 0 && (
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3 }}>
                                    <BellAlertIcon size={12} style={{ color: '#666' }} />
                                    <span style={{ color: '#888' }}>{unreadCount}</span>
                                </span>
                            )}
                        </div>
                    </>
                )}

                <div className="dash__sysbar-spacer" />

                {/* Refresh timestamp */}
                <div className="dash__sysbar-item">
                    <RefreshCycleIcon size={10} style={{ color: '#444' }} />
                    <span style={{ color: '#555' }}>{timeAgo(aimos.lastRefresh)}</span>
                </div>
            </div>

            {/* ═══════════════════════════════════════
                ZONE 2: Two-Column Workspace
                ═══════════════════════════════════════ */}
            <div className="dash__workspace">

                {/* ─── Left Column: System Status + Operations ─── */}
                <div className="dash__col dash__col--left">

                    {/* Agent Genome Fleet */}
                    <div className="dash__section">
                        <div className="dash__section-hdr">
                            <ConstellationIcon size={12} />
                            AGENT FLEET
                            <span className="dash__section-badge">{activeGenomes.length} active</span>
                        </div>
                        <div className="dash__section-body">
                            <div className="dash__fleet-grid">
                                {genomes.agents.filter(a => a.status !== 'retired').map(agent => (
                                    <div
                                        key={agent.id}
                                        className="dash__agent"
                                        title={`${agent.displayName}\nDomains: ${agent.behavioralDNA?.domains?.join(', ') || '—'}\nConfidence: ${(agent.metrics?.confidence || 0).toFixed(2)}`}
                                    >
                                        <span className="dash__agent-avatar">{agent.avatar?.charAt?.(0) || '◆'}</span>
                                        <div className="dash__agent-info">
                                            <div className="dash__agent-name">{agent.displayName || agent.name}</div>
                                            <div className="dash__agent-domain">
                                                {agent.behavioralDNA?.domains?.[0] || agent.category || '—'}
                                            </div>
                                        </div>
                                        <span className="dash__agent-score" style={{ color: confidenceColor(agent.metrics?.confidence || 0) }}>
                                            {((agent.metrics?.confidence || 0) * 100).toFixed(0)}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* AIM-OS Subsystem Status */}
                    <div className="dash__section">
                        <div className="dash__section-hdr">
                            <RadarIcon size={12} />
                            AIM-OS SUBSYSTEMS
                            <span className="dash__section-badge">{subsystems.filter(s => s.online).length}/{subsystems.length}</span>
                        </div>
                        <div className="dash__section-body">
                            <div className="dash__subsys-grid">
                                {subsystems.map(sys => (
                                    <div key={sys.name} className={`dash__subsys-cell ${sys.online ? 'dash__subsys-cell--active' : ''}`}>
                                        <span className={`dash__subsys-led ${sys.online ? 'dash__subsys-led--on' : 'dash__subsys-led--off'}`} />
                                        <span>{sys.name}</span>
                                        <span style={{ marginLeft: 'auto', fontSize: '8px' }}>{sys.stat}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Oracle Action Log */}
                    <div className="dash__section">
                        <div className="dash__section-hdr">
                            <BoltIcon size={12} />
                            ORACLE LOG
                            <span className="dash__section-badge">{oracle.actionLog.length} total</span>
                        </div>
                        <div className="dash__section-body">
                            {recentActions.length === 0 ? (
                                <div className="dash__empty">No oracle actions yet</div>
                            ) : (
                                recentActions.map((action, i) => (
                                    <div key={i} className="dash__oracle-entry">
                                        <span className="dash__oracle-time">{clockTime(action.timestamp)}</span>
                                        <span className="dash__oracle-text">{action.detail || action.action || '—'}</span>
                                        <span className={`dash__oracle-status dash__oracle-status--${action.status}`}>
                                            {action.status}
                                        </span>
                                        {action.status === 'pending' && (
                                            <>
                                                <button className="dash__oracle-approve dash__oracle-approve--yes" onClick={() => oracle.approveAction(action.id)}>✓</button>
                                                <button className="dash__oracle-approve dash__oracle-approve--no" onClick={() => oracle.denyAction(action.id)}>✗</button>
                                            </>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Upcoming Scheduled */}
                    {upcomingEvents.length > 0 && (
                        <div className="dash__section">
                            <div className="dash__section-hdr">
                                <CalendarMarkIcon size={12} />
                                UPCOMING
                                {calendar.runningMacro && (
                                    <span className="dash__section-badge" style={{ color: 'var(--dxl-led-amber)' }}>
                                        <RefreshCycleIcon size={10} style={{ verticalAlign: 'middle' }} /> macro
                                    </span>
                                )}
                            </div>
                            <div className="dash__section-body">
                                {upcomingEvents.map(evt => (
                                    <div key={evt.id} className="dash__oracle-entry">
                                        <span className="dash__oracle-time">{clockTime(evt.startTime)}</span>
                                        <span className="dash__oracle-text">{evt.title}</span>
                                        <span className="dash__section-badge">{String(evt.recurrence) !== 'none' ? String(evt.recurrence) : ''}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* ─── Right Column: Dispatch + Missions + Feed ─── */}
                <div className="dash__col dash__col--right">

                    {/* Dispatch Composer */}
                    <div className="dash__section">
                        <div className="dash__section-hdr">
                            <DispatchIcon size={12} />
                            DISPATCH
                            <span className="dash__section-badge">
                                <select
                                    className="dash__dispatch-select"
                                    value={strategy}
                                    onChange={(e) => setStrategy(e.target.value as any)}
                                >
                                    <option value="parallel">Parallel</option>
                                    <option value="consensus">Consensus</option>
                                    <option value="sequential">Sequential</option>
                                </select>
                            </span>
                        </div>
                        <div className="dash__dispatch">
                            <div className="dash__dispatch-input">
                                <textarea
                                    className="dash__dispatch-textarea"
                                    placeholder="Enter prompt to dispatch across AI providers..."
                                    value={dispatchText}
                                    onChange={(e) => setDispatchText(e.target.value)}
                                    rows={3}
                                />
                            </div>
                            <div className="dash__dispatch-controls">
                                <div className="dash__dispatch-targets">
                                    <button
                                        className={`dash__target-btn ${selectedTargets.has('all') ? 'dash__target-btn--active' : ''}`}
                                        onClick={() => toggleTarget('all')}
                                    >
                                        All
                                    </button>
                                    {liveProviders.map(p => (
                                        <button
                                            key={p.name}
                                            className={`dash__target-btn dash__target-btn--connected ${selectedTargets.has(p.name) ? 'dash__target-btn--active' : ''}`}
                                            onClick={() => toggleTarget(p.name)}
                                        >
                                            {p.icon} {p.name}
                                            {/* Show pipeline stage if a session exists */}
                                            {sessionStates.find(([, s]) => s.provider === p.name)?.[1]?.status !== 'disconnected' && (
                                                <span className="dash__target-pipeline">
                                                    {sessionStates.find(([, s]) => s.provider === p.name)?.[1]?.status}
                                                </span>
                                            )}
                                        </button>
                                    ))}
                                </div>
                                <button
                                    className="dash__dispatch-btn"
                                    onClick={() => { /* dispatch logic */ }}
                                    disabled={!dispatchText.trim()}
                                >
                                    <DispatchIcon size={12} />
                                    DISPATCH
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Active Missions — Per-target pipeline visualization */}
                    <div className="dash__section">
                        <div className="dash__section-hdr">
                            <LaunchVectorIcon size={12} />
                            MISSIONS
                            <span className="dash__section-badge">{missions.filter(m => m.status === 'running').length} active</span>
                        </div>
                        <div className="dash__section-body">
                            {missions.length === 0 ? (
                                <div className="dash__empty">No missions dispatched yet</div>
                            ) : (
                                missions.slice(-5).reverse().map(mission => {
                                    // Mission.targets is string[] (provider names), not objects
                                    const pct = mission.progress ?? 0;

                                    return (
                                        <div key={mission.id} className="dash__mission">
                                            <div className="dash__mission-hdr">
                                                <span className="dash__mission-id">{mission.id?.slice(0, 8)}</span>
                                                <span className="dash__mission-title">
                                                    {mission.prompt?.slice(0, 80) || mission.title || 'Mission'}
                                                </span>
                                                <span className={`dash__mission-status dash__mission-status--${mission.status}`}>
                                                    {mission.status}
                                                </span>
                                            </div>

                                            {/* Target providers as chips */}
                                            {(mission.targets || []).length > 0 && (
                                                <div className="dash__mission-targets">
                                                    {mission.targets.map((provider: string, i: number) => (
                                                        <span key={i} className="dash__mission-target">
                                                            {PROVIDER_ICONS[provider.toLowerCase()] || '◆'}
                                                            {provider}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}

                                            <div className="dash__mission-progress">
                                                <div
                                                    className={`dash__mission-fill ${pct >= 100 ? 'dash__mission-fill--done' : ''}`}
                                                    style={{ width: `${Math.min(100, pct)}%` }}
                                                />
                                            </div>

                                            {mission.status === 'complete' && (
                                                <div className="dash__mission-actions">
                                                    <button className="dash__btn-sm dash__btn-sm--primary" onClick={() => addTab({ id: `mission-${mission.id}`, type: 'mission', label: mission.title, closable: true })}>
                                                        View Results
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>

                    {/* Unified Results Feed */}
                    <div className="dash__section">
                        <div className="dash__section-hdr">
                            <ClipboardListIcon size={12} />
                            FEED
                            <span className="dash__section-badge">{feedItems.length} items</span>
                        </div>
                        <div className="dash__section-body">
                            {feedItems.length === 0 ? (
                                <div className="dash__empty">No activity yet — dispatch a mission or wait for system events</div>
                            ) : (
                                feedItems.map((item, i) => (
                                    <div key={i} className="dash__feed-item">
                                        <span className="dash__feed-time">{clockTime(item.time)}</span>
                                        <span className={`dash__feed-icon dash__feed-icon--${item.type}`}>
                                            {item.type === 'notification' && <BellAlertIcon size={12} />}
                                            {item.type === 'ai_message' && <RobotHeadIcon size={12} />}
                                            {item.type === 'oracle' && <BoltIcon size={12} />}
                                            {item.type === 'activity' && <ClipboardListIcon size={12} />}
                                        </span>
                                        <span className="dash__feed-text">
                                            <span className="dash__feed-source">{item.source}</span>{' '}
                                            {item.text}
                                        </span>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
