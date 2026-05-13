import { useJOCStore } from '../../store/jocStore';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ChevronUpIcon, ChevronDownIcon } from '../icons';
import { GitTimelineV2 } from '../GitTimelineV2';

// ─── Mini Subway Map for Collapsed Bar ───

function MiniSubwayMap() {
    // Purely visual — tiny branch lines with dots, no text
    const commits = [
        // Lane 0: main/clean-master (white)
        { x: 5, y: 8, lane: 0, color: '#888' },
        { x: 18, y: 8, lane: 0, color: '#888' },
        { x: 31, y: 8, lane: 0, color: '#888' },
        { x: 44, y: 8, lane: 0, color: '#7C4DFF' }, // aether
        // Lane 1: opus/joc-build (amber)
        { x: 37, y: 18, lane: 1, color: '#CC7722' },
        { x: 50, y: 18, lane: 1, color: '#CC7722' },
        { x: 63, y: 18, lane: 1, color: '#CC7722' },
        { x: 76, y: 18, lane: 1, color: '#CC7722' },
        { x: 89, y: 18, lane: 1, color: '#CC7722' },
        { x: 102, y: 18, lane: 1, color: '#CC7722', active: true },
        // Lane 2: orbital (cyan-faded)
        { x: 5, y: 28, lane: 2, color: '#FFB74D55' },
        { x: 18, y: 28, lane: 2, color: '#FFB74D55' },
        { x: 31, y: 28, lane: 2, color: '#FFB74D55' },
    ];

    return (
        <svg width={120} height={36} viewBox="0 0 120 36" style={{ opacity: 0.8 }}>
            {/* Route lines */}
            <path d="M 5 8 L 44 8" stroke="#555" strokeWidth="1.5" fill="none" strokeLinecap="round" />
            <path d="M 44 8 C 50 8, 37 18, 37 18" stroke="#7C4DFF" strokeWidth="1" fill="none" strokeDasharray="2,2" opacity="0.4" />
            <path d="M 37 18 L 102 18" stroke="#CC7722" strokeWidth="1.5" fill="none" strokeLinecap="round" />
            <path d="M 5 28 L 31 28" stroke="#FFB74D" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.3" />

            {/* Commit dots */}
            {commits.map((c, i) => (
                <circle
                    key={i}
                    cx={c.x}
                    cy={c.y}
                    r={(c as any).active ? 3 : 2}
                    fill={(c as any).active ? c.color : 'transparent'}
                    stroke={c.color}
                    strokeWidth={1}
                />
            ))}

            {/* Active glow on last dot */}
            <circle cx={102} cy={18} r={5} fill="none" stroke="#CC7722" strokeWidth={0.5} opacity={0.3}>
                <animate attributeName="r" from="4" to="8" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" from="0.3" to="0" dur="2s" repeatCount="indefinite" />
            </circle>
        </svg>
    );
}

// ─── Size Icons ───

function ExpandMidIcon() {
    return (
        <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <polyline points="17,11 12,6 7,11" />
            <line x1="12" y1="18" x2="12" y2="6" />
        </svg>
    );
}

function ExpandFullIcon() {
    return (
        <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <polyline points="17,6 12,1 7,6" />
            <polyline points="17,14 12,9 7,14" />
            <line x1="12" y1="22" x2="12" y2="1" />
        </svg>
    );
}

function CollapseIcon() {
    return (
        <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <polyline points="7,13 12,18 17,13" />
            <line x1="12" y1="6" x2="12" y2="18" />
        </svg>
    );
}

// ─── Tabs ───

const BOTTOM_TABS = [
    { id: 'timeline' as const, label: 'Git Timeline', icon: '⎇' },
    { id: 'comms' as const, label: 'Agent Comms', icon: '📡' },
    { id: 'output' as const, label: 'Output', icon: '▸' },
    { id: 'terminal' as const, label: 'Terminal', icon: '⌘' },
    { id: 'diagnostics' as const, label: 'Diagnostics', icon: '⚡' },
    { id: 'missions' as const, label: 'Missions', icon: '▲' },
    { id: 'resources' as const, label: 'Resources', icon: '◆' },
];

// ─── Component ───

export function BottomBar() {
    const {
        bottomPanelSize, toggleBottomPanel, setBottomPanelSize,
        bottomActiveTab, setBottomTab,
        sessions, missions, activity,
    } = useJOCStore();
    const aimos = useAIMOS({ pollDomains: ['memory', 'messages'], pollInterval: 15000 });

    const activeSessions = sessions.filter(s => s.status === 'active').length;
    const runningMissions = missions.filter(m => m.status === 'running').length;

    const isExpanded = bottomPanelSize !== 'collapsed';
    const panelHeight = bottomPanelSize === 'full'
        ? 'var(--bottombar-full)'
        : bottomPanelSize === 'mid'
            ? 'var(--bottombar-mid)'
            : 'var(--bottombar-height)';

    return (
        <div
            className="bottombar"
            style={{ height: panelHeight, transition: 'height 0.25s ease' }}
        >
            {/* Header strip — always visible */}
            <div className="bottombar-header">
                <div className="bottombar-left">
                    {/* Size controls — collapse/mid/full */}
                    <div style={{ display: 'flex', gap: '1px' }}>
                        <button
                            className="bottombar-expand-btn"
                            onClick={() => setBottomPanelSize('collapsed')}
                            title="Collapse"
                            style={{ opacity: bottomPanelSize === 'collapsed' ? 1 : 0.5 }}
                        >
                            <ChevronDownIcon />
                        </button>
                        <button
                            className="bottombar-expand-btn"
                            onClick={() => setBottomPanelSize('mid')}
                            title="Mid size (25%)"
                            style={{ opacity: bottomPanelSize === 'mid' ? 1 : 0.5 }}
                        >
                            <ExpandMidIcon />
                        </button>
                        <button
                            className="bottombar-expand-btn"
                            onClick={() => setBottomPanelSize('full')}
                            title="Full size (50%)"
                            style={{ opacity: bottomPanelSize === 'full' ? 1 : 0.5 }}
                        >
                            <ExpandFullIcon />
                        </button>
                    </div>

                    {/* Mini subway map — only in collapsed mode */}
                    {bottomPanelSize === 'collapsed' && <MiniSubwayMap />}
                </div>

                <div className="bottombar-center">
                    {/* Mission timeline mini */}
                    {missions.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', maxWidth: '400px', width: '100%' }}>
                            <span style={{ fontSize: '10px', color: 'var(--text-hint)' }}>Missions:</span>
                            <div style={{
                                flex: 1,
                                height: '6px',
                                background: 'var(--bg-input)',
                                borderRadius: '3px',
                                overflow: 'hidden',
                                position: 'relative',
                            }}>
                                {missions.map((m, i) => (
                                    <div
                                        key={m.id}
                                        style={{
                                            position: 'absolute',
                                            left: `${(i / missions.length) * 100}%`,
                                            width: `${100 / missions.length}%`,
                                            height: '100%',
                                            background: m.status === 'complete' ? 'var(--success)' : 'var(--purple)',
                                            opacity: m.status === 'complete' ? 0.5 : 1,
                                            borderRight: '1px solid var(--bg-deep)',
                                        }}
                                        title={`${m.id}: ${m.title}`}
                                    />
                                ))}
                            </div>
                            <span style={{ fontSize: '10px', color: 'var(--text-hint)' }}>
                                {missions[0]?.id}
                            </span>
                        </div>
                    )}
                </div>

                <div className="bottombar-right">
                    <span>
                        <span className="status-dot active" />
                        {activeSessions} AIs
                    </span>
                    <span>
                        ▲ {runningMissions} mission{runningMissions !== 1 ? 's' : ''}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span className={`status-dot ${aimos.connected ? 'active' : 'sleeping'}`} />
                        MCP: {aimos.connected ? '✓' : '✗'}
                        {aimos.connected && aimos.latency > 0 && (
                            <span style={{ fontSize: '9px', color: 'var(--text-hint)' }}>{aimos.latency}ms</span>
                        )}
                    </span>
                    {aimos.memory?.total_atoms !== undefined && (
                        <span style={{ color: 'var(--accent)', fontSize: '10px' }}>
                            {aimos.memory.total_atoms} atoms
                        </span>
                    )}
                </div>
            </div>

            {/* Expanded panel */}
            {isExpanded && (
                <div className="bottombar-panel animate-fadeIn">
                    <div className="bottombar-panel-tabs">
                        {BOTTOM_TABS.map(tab => (
                            <button
                                key={tab.id}
                                className={`bottombar-panel-tab ${bottomActiveTab === tab.id ? 'active' : ''}`}
                                onClick={() => setBottomTab(tab.id)}
                            >
                                <span style={{ marginRight: '3px', fontSize: '10px' }}>{tab.icon}</span>
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    <div className="bottombar-panel-content">
                        {bottomActiveTab === 'timeline' && (
                            <GitTimelineV2 />
                        )}

                        {bottomActiveTab === 'comms' && (
                            <div>
                                {activity.map(a => (
                                    <div key={a.id} className="activity-item">
                                        <span className="activity-time">{a.time}</span>
                                        <span className="activity-text">{a.text}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        {bottomActiveTab === 'output' && (
                            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', padding: '8px' }}>
                                <div>[12:23:42] JOC initialized — all systems nominal</div>
                                <div>[12:23:43] MCP connection established</div>
                                <div>[12:23:44] 4 AI sessions loaded from cache</div>
                                <div>[12:23:45] Git Timeline V2 loaded — 16 commits, 4 branches</div>
                                <div style={{ color: 'var(--success)' }}>[12:23:46] Ready.</div>
                            </div>
                        )}

                        {bottomActiveTab === 'terminal' && (
                            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', padding: '8px', background: '#0a0a0a', height: '100%' }}>
                                <div style={{ color: '#4CAF50' }}>$ npm run dev</div>
                                <div style={{ color: 'var(--text-hint)' }}>  VITE v5.4.x  ready in 340ms</div>
                                <div style={{ color: 'var(--text-hint)' }}>  ➜  Local:   http://localhost:5011/</div>
                                <div style={{ color: 'var(--text-hint)' }}>  ➜  press h + enter to show help</div>
                                <div style={{ marginTop: '8px', color: '#CC7722' }}>■ opus/M-42/joc-build</div>
                                <div style={{ color: 'var(--text-hint)' }}>  16 files changed, +5841 insertions</div>
                            </div>
                        )}

                        {bottomActiveTab === 'diagnostics' && (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px', fontSize: '10px', padding: '8px' }}>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>BUILD</div>
                                    <div style={{ color: 'var(--success)' }}>✓ No errors</div>
                                    <div style={{ color: 'var(--text-hint)' }}>3 warnings (unused vars)</div>
                                    <div style={{ color: 'var(--text-secondary)' }}>HMR: 40ms avg</div>
                                </div>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>MCP</div>
                                    <div style={{ color: 'var(--success)' }}>● Connected</div>
                                    <div style={{ color: 'var(--text-hint)' }}>5 messages sent</div>
                                    <div style={{ color: 'var(--text-hint)' }}>2 received</div>
                                </div>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>AGENTS</div>
                                    <div><span style={{ color: '#CC7722' }}>● Opus</span> active</div>
                                    <div><span style={{ color: '#7C4DFF' }}>● Aether</span> standby</div>
                                    <div><span style={{ color: '#4285F4' }}>● Gemini</span> offline</div>
                                </div>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>GIT</div>
                                    <div style={{ color: '#CC7722' }}>⎇ opus/M-42/joc-build</div>
                                    <div style={{ color: 'var(--text-hint)' }}>16 commits today</div>
                                    <div style={{ color: 'var(--text-hint)' }}>0 conflicts</div>
                                </div>
                            </div>
                        )}

                        {bottomActiveTab === 'missions' && (
                            <div className="mission-queue">
                                <div className="mission-queue-header">
                                    <span className="mission-queue-title">Mission Queue</span>
                                    <span className="mission-queue-count">{missions.length} missions</span>
                                    <button className="mission-queue-btn" onClick={() => {
                                        const { addTab, setActiveTab } = useJOCStore.getState();
                                        addTab({ id: `dispatch-${Date.now()}`, type: 'dispatch', label: 'New Mission', closable: true });
                                        setActiveTab(`dispatch-${Date.now()}`);
                                    }}>+ New</button>
                                </div>
                                {missions.map(m => {
                                    const statusColor = m.status === 'complete' ? '#4ecdc4'
                                        : m.status === 'running' ? '#00d4ff'
                                            : m.status === 'failed' ? '#ff6b6b'
                                                : m.status === 'dispatched' ? '#ffd93d'
                                                    : '#555';
                                    return (
                                        <div key={m.id} className="mission-card">
                                            <div className="mission-card-header">
                                                <span className="mission-card-dot" style={{ background: statusColor, boxShadow: `0 0 6px ${statusColor}` }} />
                                                <span className="mission-card-id">{m.id}</span>
                                                <span className="mission-card-title">{m.title}</span>
                                                <span className="mission-card-status" style={{ color: statusColor }}>{m.status.toUpperCase()}</span>
                                                <span className="mission-card-time">{m.createdAt}</span>
                                            </div>
                                            <div className="mission-card-body">
                                                <div className="mission-card-targets">
                                                    {m.targets.map(t => (
                                                        <span key={t} className="mission-target-tag">{t}</span>
                                                    ))}
                                                </div>
                                                <div className="mission-card-progress-row">
                                                    <div className="mission-progress-track">
                                                        <div className="mission-progress-fill" style={{ width: `${m.progress}%`, background: statusColor }} />
                                                    </div>
                                                    <span className="mission-progress-pct">{m.progress}%</span>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}

                        {bottomActiveTab === 'resources' && (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', fontSize: '11px', padding: '8px' }}>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px' }}>LOCAL GPU</div>
                                    <div style={{ color: 'var(--text-primary)' }}>3050 Ti — 38% util</div>
                                    <div style={{ color: 'var(--text-hint)' }}>4GB / 4GB VRAM</div>
                                </div>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px' }}>STORAGE</div>
                                    <div style={{ color: 'var(--text-primary)' }}>Google Drive: 4.2 / 30 TB</div>
                                    <div style={{ color: 'var(--text-hint)' }}>Local: 210 GB free</div>
                                </div>
                                <div>
                                    <div style={{ color: 'var(--text-hint)', marginBottom: '4px' }}>API USAGE</div>
                                    <div style={{ color: 'var(--text-primary)' }}>Gemini: 842 / ∞ calls</div>
                                    <div style={{ color: 'var(--text-hint)' }}>OpenAI: $2.40 today</div>
                                </div>
                            </div>
                        )}

                        {bottomActiveTab === 'console' && (
                            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', padding: '8px' }}>
                                <div style={{ color: '#4285F4' }}>ℹ [React] StrictMode double-render detected</div>
                                <div style={{ color: 'var(--text-hint)' }}>ℹ [Vite] HMR update: /src/components/GitTimelineV2.tsx</div>
                                <div style={{ color: '#FFB74D' }}>⚠ [TS] 'CommitIcon' is declared but never used</div>
                                <div style={{ color: 'var(--text-hint)' }}>ℹ [Zustand] Store 'jocStore' initialized</div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
