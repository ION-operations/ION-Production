import React, { useState } from 'react';
import { useJOCStore, type OpenLeftDrawer, type PageType } from '../../store/jocStore';
import { ChevronLeftIcon, CloseIcon } from '../icons';
import { useAIMOS } from '../../hooks/useAIMOS';

// ─── Left Drawer Metadata ───

const LEFT_DRAWER_META: Record<string, { title: string; width: number }> = {
    // Dashboard page drawers
    'sys-status': { title: 'SYSTEM STATUS', width: 320 },
    'activity-feed': { title: 'ACTIVITY FEED', width: 320 },
    'quick-launch': { title: 'QUICK LAUNCH', width: 300 },
    // Session page drawers
    'driver-status': { title: 'DRIVER STATUS', width: 340 },
    'dom-inspector': { title: 'DOM INSPECTOR', width: 360 },
    'injection-log': { title: 'INJECTION LOG', width: 340 },
    // Projects page drawers
    'file-tree': { title: 'FILE EXPLORER', width: 300 },
    'git-graph': { title: 'GIT GRAPH', width: 340 },
    'relationships': { title: 'RELATIONSHIPS', width: 320 },
    // Editor page drawers
    'symbols': { title: 'SYMBOLS', width: 280 },
    'search': { title: 'SEARCH', width: 320 },
    // Atlas page drawers
    'system-list': { title: 'SYSTEMS', width: 300 },
    'connections': { title: 'CONNECTIONS', width: 320 },
    // Compute page drawers
    'resources': { title: 'RESOURCES', width: 300 },
    'jobs': { title: 'JOBS', width: 300 },
    // Comms page drawers
    'threads': { title: 'THREADS', width: 300 },
    'agents': { title: 'AGENTS', width: 300 },
    // Dispatch page drawers
    'targets': { title: 'TARGETS', width: 300 },
    'templates': { title: 'TEMPLATES', width: 300 },
    // Synthesizer page drawers
    'responses': { title: 'RESPONSES', width: 320 },
    'evidence': { title: 'EVIDENCE', width: 320 },
    // Context page drawers
    'memory-browser': { title: 'MEMORY BROWSER', width: 340 },
    'retrieval-log': { title: 'RETRIEVAL LOG', width: 320 },
    // Context Graph page drawers
    'timeline-rail': { title: 'TIMELINE', width: 300 },
    'filters': { title: 'FILTERS', width: 280 },
    'systems': { title: 'SYSTEMS', width: 280 },
    // Mission builder drawers
    'agent-pool': { title: 'AGENT POOL', width: 300 },
    // GPU drawers
    'models': { title: 'MODELS', width: 300 },
    'queue': { title: 'QUEUE', width: 300 },
    // Health drawers
    'sessions': { title: 'SESSIONS', width: 300 },
    'dom-health': { title: 'DOM HEALTH', width: 320 },
    // Settings drawers
    'sections': { title: 'SECTIONS', width: 260 },
};

// ─── AIM-OS System Color Map ───

const SYSTEM_COLORS: Record<string, string> = {
    CMC: '#00BCD4',
    HHNI: '#4CAF50',
    VIF: '#FFC107',
    SEG: '#9C27B0',
    TCS: '#2196F3',
    CAS: '#FF5722',
    APOE: '#009688',
    SCOR: '#3F51B5',
    MCP: '#00d4ff',
};

// ─── Placeholder Content ───

function PlaceholderContent({ label, connected }: { label: string; connected?: boolean }) {
    return (
        <div className="drawer-placeholder">
            <div className="drawer-placeholder-icon">{connected === false ? '🔌' : '📂'}</div>
            <div className="drawer-placeholder-text">{label}</div>
            <div className="drawer-placeholder-hint">
                {connected === false
                    ? 'MCP server offline — reconnecting...'
                    : 'Data source not yet wired'}
            </div>
        </div>
    );
}

// ─── Real Data: System Status ───

function SystemStatusContent() {
    const { connected, memory, consciousness, latency, health, problems, goals } = useAIMOS({
        pollDomains: ['memory', 'consciousness', 'goals', 'problems'],
        pollInterval: 12000,
    });

    // Build system status from real MCP data
    const systems = [
        {
            name: 'MCP',
            status: connected ? 'online' : 'offline',
            detail: connected ? `${latency}ms` : 'disconnected',
            color: SYSTEM_COLORS.MCP,
        },
        {
            name: 'CMC',
            status: memory ? 'online' : (connected ? 'idle' : 'offline'),
            detail: memory?.total_atoms != null ? `${memory.total_atoms} atoms` : '—',
            color: SYSTEM_COLORS.CMC,
        },
        {
            name: 'CAS',
            status: consciousness ? 'online' : (connected ? 'idle' : 'offline'),
            detail: consciousness?.cognitive_drift != null
                ? `drift: ${(consciousness.cognitive_drift as number).toFixed(2)}`
                : consciousness?.working_memory_items != null
                    ? `${consciousness.working_memory_items} items`
                    : '—',
            color: SYSTEM_COLORS.CAS,
        },
        {
            name: 'VIF',
            status: connected ? 'online' : 'offline',
            detail: '—',
            color: SYSTEM_COLORS.VIF,
        },
        {
            name: 'HHNI',
            status: connected ? 'online' : 'offline',
            detail: '—',
            color: SYSTEM_COLORS.HHNI,
        },
        {
            name: 'SEG',
            status: connected ? 'online' : 'offline',
            detail: '—',
            color: SYSTEM_COLORS.SEG,
        },
        {
            name: 'TCS',
            status: connected ? 'online' : 'offline',
            detail: '—',
            color: SYSTEM_COLORS.TCS,
        },
        {
            name: 'APOE',
            status: goals.length > 0 ? 'online' : (connected ? 'idle' : 'offline'),
            detail: goals.length > 0 ? `${goals.length} goals` : '—',
            color: SYSTEM_COLORS.APOE,
        },
    ];

    return (
        <div className="left-drawer-sys-status">
            {/* Connection header */}
            <div className="sys-status-header">
                <span className={`sys-dot ${connected ? 'active' : 'error'}`} />
                <span className="sys-status-label">
                    {connected ? 'AIM-OS Connected' : 'Disconnected'}
                </span>
                {connected && (
                    <span className="sys-status-latency">{latency}ms</span>
                )}
            </div>

            {/* Individual systems */}
            {systems.map(s => (
                <div key={s.name} className="sys-status-row">
                    <span
                        className={`sys-dot ${s.status}`}
                        style={{ background: s.status === 'online' ? s.color : undefined }}
                    />
                    <span className="sys-name">{s.name}</span>
                    <span className="sys-detail">{s.detail}</span>
                </div>
            ))}

            {/* IDE problems summary */}
            {problems && (
                <div className="sys-problems-summary">
                    <div className="sys-section-label">IDE Diagnostics</div>
                    <div className="sys-problems-row">
                        {(problems.errors ?? 0) > 0 && (
                            <span className="sys-problem-badge error">
                                {problems.errors} errors
                            </span>
                        )}
                        {(problems.warnings ?? 0) > 0 && (
                            <span className="sys-problem-badge warning">
                                {problems.warnings} warnings
                            </span>
                        )}
                        {(problems.errors ?? 0) === 0 && (problems.warnings ?? 0) === 0 && (
                            <span className="sys-problem-badge clean">Clean</span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

// ─── Real Data: Activity Feed ───

function ActivityFeedContent() {
    const { aiMessages, connected } = useAIMOS({
        pollDomains: ['messages'],
        pollInterval: 12000,
    });

    if (!connected) {
        return <PlaceholderContent label="Activity Feed" connected={false} />;
    }

    if (aiMessages.length === 0) {
        return (
            <div className="drawer-placeholder">
                <div className="drawer-placeholder-icon">💬</div>
                <div className="drawer-placeholder-text">No messages yet</div>
                <div className="drawer-placeholder-hint">AI agent messages will appear here</div>
            </div>
        );
    }

    return (
        <div className="left-drawer-activity-feed">
            {aiMessages.slice(0, 20).map((msg, i) => {
                const time = msg.timestamp
                    ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    : '';
                const typeClass = msg.message_type === 'urgent' ? 'urgent'
                    : msg.message_type === 'task_handoff' ? 'handoff'
                        : msg.message_type === 'status_update' ? 'status'
                            : 'discussion';
                return (
                    <div key={msg.id || `msg-${i}`} className={`activity-item ${typeClass}`}>
                        <div className="activity-item-header">
                            <span className="activity-from">{msg.from_ai}</span>
                            <span className="activity-arrow">→</span>
                            <span className="activity-to">{msg.to_ai}</span>
                            <span className="activity-time">{time}</span>
                        </div>
                        <div className="activity-content">
                            {msg.content.length > 120
                                ? msg.content.substring(0, 120) + '…'
                                : msg.content}
                        </div>
                        {msg.message_type && (
                            <span className={`activity-type-badge ${typeClass}`}>
                                {msg.message_type.replace('_', ' ')}
                            </span>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

// ─── Real Data: Goals ───

function GoalsContent() {
    const { goals, connected } = useAIMOS({
        pollDomains: ['goals'],
        pollInterval: 72000,
    });

    if (!connected) {
        return <PlaceholderContent label="Goals" connected={false} />;
    }

    if (goals.length === 0) {
        return (
            <div className="drawer-placeholder">
                <div className="drawer-placeholder-icon">🎯</div>
                <div className="drawer-placeholder-text">No goals set</div>
                <div className="drawer-placeholder-hint">
                    Goals created via MCP will appear here
                </div>
            </div>
        );
    }

    return (
        <div className="left-drawer-goals">
            {goals.map(goal => {
                const progressPercent = Math.round((goal.progress || 0) * 100);
                const statusClass = goal.status === 'completed' ? 'complete'
                    : goal.status === 'in_progress' ? 'in-progress'
                        : goal.status === 'blocked' ? 'blocked'
                            : 'planned';
                return (
                    <div key={goal.goal_id} className={`goal-item ${statusClass}`}>
                        <div className="goal-header">
                            <span className={`goal-priority ${goal.priority || 'medium'}`}>
                                {goal.priority === 'critical' ? '🔴'
                                    : goal.priority === 'high' ? '🟠'
                                        : goal.priority === 'medium' ? '🟡' : '🟢'}
                            </span>
                            <span className="goal-id">{goal.goal_id}</span>
                            <span className={`goal-status ${statusClass}`}>{goal.status}</span>
                        </div>
                        <div className="goal-name">{goal.name}</div>
                        <div className="goal-progress-bar">
                            <div
                                className="goal-progress-fill"
                                style={{ width: `${progressPercent}%` }}
                            />
                        </div>
                        <div className="goal-progress-label">{progressPercent}%</div>
                    </div>
                );
            })}
        </div>
    );
}

// ─── File Tree (preserved) ───

function FileTreeContent() {
    const mockFiles = [
        { name: 'src/', type: 'dir', children: ['components/', 'pages/', 'store/', 'styles/'] },
        { name: 'package.json', type: 'file' },
        { name: 'tsconfig.json', type: 'file' },
        { name: 'vite.config.ts', type: 'file' },
    ];
    return (
        <div className="left-drawer-file-tree">
            {mockFiles.map(f => (
                <div key={f.name} className={`file-tree-item ${f.type}`}>
                    <span className="file-tree-icon">{f.type === 'dir' ? '📁' : '📄'}</span>
                    <span className="file-tree-name">{f.name}</span>
                    {f.type === 'dir' && f.children && (
                        <div className="file-tree-children">
                            {f.children.map(c => (
                                <div key={c} className="file-tree-item file">
                                    <span className="file-tree-icon">📁</span>
                                    <span className="file-tree-name">{c}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

// ─── Context Filters (preserved + enhanced) ───

function ContextFiltersContent() {
    const systems = ['CMC', 'HHNI', 'SEG', 'VIF', 'APOE', 'CAS', 'TCS'];
    return (
        <div className="left-drawer-filters">
            <div className="filter-section">
                <div className="filter-heading">Systems</div>
                {systems.map(s => (
                    <label key={s} className="filter-checkbox">
                        <input type="checkbox" defaultChecked />
                        <span style={{ color: SYSTEM_COLORS[s] || 'inherit' }}>{s}</span>
                    </label>
                ))}
            </div>
            <div className="filter-section">
                <div className="filter-heading">Confidence</div>
                <input type="range" min="0" max="100" defaultValue="50" className="filter-range" />
                <div className="filter-range-labels">
                    <span>κ ≥ 0.50</span>
                    <span>1.00</span>
                </div>
            </div>
            <div className="filter-section">
                <div className="filter-heading">Time Range</div>
                <select className="filter-select">
                    <option>Last 1 hour</option>
                    <option>Last 6 hours</option>
                    <option>Last 24 hours</option>
                    <option>All time</option>
                </select>
            </div>
        </div>
    );
}

// ─── Content Resolution ───

function getLeftDrawerContent(drawerType: string): React.ReactNode {
    switch (drawerType) {
        case 'sys-status': return <SystemStatusContent />;
        case 'activity-feed': return <ActivityFeedContent />;
        case 'file-tree': return <FileTreeContent />;
        case 'filters': return <ContextFiltersContent />;
        default: {
            const meta = LEFT_DRAWER_META[drawerType];
            return <PlaceholderContent label={meta?.title || drawerType} />;
        }
    }
}

// ─── Single Left Drawer Panel ───

function LeftDrawerPanel({ drawer }: { drawer: OpenLeftDrawer }) {
    const { closeLeftDrawer } = useJOCStore();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const meta = LEFT_DRAWER_META[drawer.type] || { title: drawer.type.toUpperCase(), width: 300 };

    const positionClass =
        drawer.position === 'full' ? 'left-drawer-full' :
            drawer.position === 'top' ? 'left-drawer-top' :
                'left-drawer-bottom';

    return (
        <div
            className={`left-drawer-panel ${positionClass} ${isCollapsed ? 'collapsed' : ''}`}
            style={{ width: isCollapsed ? 36 : meta.width }}
        >
            <div className="drawer-header">
                <button
                    className="drawer-collapse-btn"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    title={isCollapsed ? 'Expand' : 'Collapse'}
                >
                    <ChevronLeftIcon size={14} />
                </button>
                {!isCollapsed && (
                    <>
                        <span className="drawer-title">{meta.title}</span>
                        <button
                            className="drawer-close-btn"
                            onClick={() => closeLeftDrawer(drawer.type)}
                            title="Close"
                        >
                            <CloseIcon size={12} />
                        </button>
                    </>
                )}
            </div>
            {!isCollapsed && (
                <div className="drawer-body">
                    {getLeftDrawerContent(drawer.type)}
                </div>
            )}
        </div>
    );
}

// ─── Left Drawer System Container ───

export function LeftDrawerSystem() {
    const { leftOpenDrawers } = useJOCStore();

    if (leftOpenDrawers.length === 0) return null;

    const topDrawer = leftOpenDrawers.find(d => d.position === 'top');
    const bottomDrawer = leftOpenDrawers.find(d => d.position === 'bottom');
    const fullDrawer = leftOpenDrawers.find(d => d.position === 'full');

    return (
        <div className="left-drawer-system">
            {fullDrawer && <LeftDrawerPanel drawer={fullDrawer} />}
            {!fullDrawer && topDrawer && <LeftDrawerPanel drawer={topDrawer} />}
            {!fullDrawer && bottomDrawer && <LeftDrawerPanel drawer={bottomDrawer} />}
        </div>
    );
}
