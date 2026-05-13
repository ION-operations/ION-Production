import { useJOCStore } from '../store/jocStore';

// ─── Data ───

interface SystemStatus {
    name: string;
    icon: string;
    status: 'online' | 'offline' | 'degraded';
    detail: string;
}

const SYSTEMS: SystemStatus[] = [
    { name: 'MCP Core', icon: '🔌', status: 'online', detail: 'Port 5001 · 23ms latency' },
    { name: 'BAS Server', icon: '🌐', status: 'online', detail: 'Port 5002 · 2 active sessions' },
    { name: 'Ollama', icon: '🖥', status: 'online', detail: 'llama3.2 loaded · 2.8 GB VRAM' },
    { name: 'ChatGPT', icon: '⚡', status: 'online', detail: 'Session active · 2h 14m remaining' },
    { name: 'Gemini', icon: '✦', status: 'online', detail: 'Session active · 6h 02m remaining' },
    { name: 'Claude', icon: '◈', status: 'offline', detail: 'Session expired — reconnect needed' },
    { name: 'Google Drive', icon: '☁️', status: 'online', detail: '4.2 GB / 15 GB used' },
    { name: 'Git', icon: '📦', status: 'online', detail: 'main branch · 0 uncommitted changes' },
];

interface QuickAction {
    id: string;
    label: string;
    icon: string;
    page: string;
    color: string;
}

const QUICK_ACTIONS: QuickAction[] = [
    { id: 'dispatch', label: 'Launch Mission', icon: '🚀', page: 'mission-builder', color: '#4ecdc4' },
    { id: 'chatgpt', label: 'Open ChatGPT', icon: '⚡', page: 'session', color: '#00d4ff' },
    { id: 'gemini', label: 'Open Gemini', icon: '✦', page: 'session', color: '#a882ff' },
    { id: 'atlas', label: 'System Atlas', icon: '🗺', page: 'atlas', color: '#ffd93d' },
    { id: 'comms', label: 'Agent Comms', icon: '💬', page: 'comms', color: '#ff85a2' },
    { id: 'gpu', label: 'GPU Monitor', icon: '🖥', page: 'gpu', color: '#ff6b6b' },
];

interface RecentActivity {
    icon: string;
    title: string;
    time: string;
}

const RECENT: RecentActivity[] = [
    { icon: '✓', title: 'Parallel dispatch completed (ChatGPT + Gemini)', time: '2 min ago' },
    { icon: '💾', title: 'Memory stored: JOC architecture synthesis', time: '5 min ago' },
    { icon: '🔄', title: 'ChatGPT session auto-refreshed', time: '8 min ago' },
    { icon: '🚀', title: 'Debate dispatch started: State management approach', time: '15 min ago' },
    { icon: '📊', title: 'Token usage analyzed: 42.3K tokens today', time: '22 min ago' },
];

// ─── Component ───

export function WelcomePage() {
    const { addTab, setActiveTab } = useJOCStore();

    const navigate = (page: string) => {
        addTab({ id: page, type: page as any, label: page, closable: true });
        setActiveTab(page);
    };

    const statusColors: Record<string, { color: string; bg: string; label: string }> = {
        online: { color: '#4ecdc4', bg: 'rgba(78,205,196,0.08)', label: '● ONLINE' },
        offline: { color: '#ff6b6b', bg: 'rgba(255,107,107,0.08)', label: '○ OFFLINE' },
        degraded: { color: '#ffd93d', bg: 'rgba(255,217,61,0.08)', label: '◐ DEGRADED' },
    };

    const onlineCount = SYSTEMS.filter(s => s.status === 'online').length;

    return (
        <div className="welc-page">
            <div className="welc-hero">
                <div className="welc-logo">◎</div>
                <h1 className="welc-title">Joint Operations Center</h1>
                <p className="welc-subtitle">
                    {onlineCount}/{SYSTEMS.length} systems online · Ready for operations
                </p>
            </div>

            <div className="welc-content">
                {/* Quick Actions */}
                <div className="welc-section">
                    <div className="welc-section-title">Quick Start</div>
                    <div className="welc-actions-grid">
                        {QUICK_ACTIONS.map(action => (
                            <button key={action.id} className="welc-action-card"
                                onClick={() => navigate(action.page)}
                                style={{ borderColor: `${action.color}33` }}>
                                <span className="welc-action-icon">{action.icon}</span>
                                <span className="welc-action-label">{action.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="welc-columns">
                    {/* System Status */}
                    <div className="welc-section">
                        <div className="welc-section-title">System Status</div>
                        <div className="welc-status-grid">
                            {SYSTEMS.map(sys => {
                                const st = statusColors[sys.status];
                                return (
                                    <div key={sys.name} className="welc-status-card" style={{ background: st.bg }}>
                                        <div className="welc-status-header">
                                            <span className="welc-status-icon">{sys.icon}</span>
                                            <span className="welc-status-name">{sys.name}</span>
                                            <span className="welc-status-badge" style={{ color: st.color }}>{st.label}</span>
                                        </div>
                                        <div className="welc-status-detail">{sys.detail}</div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Recent Activity */}
                    <div className="welc-section">
                        <div className="welc-section-title">Recent Activity</div>
                        <div className="welc-recent-list">
                            {RECENT.map((item, i) => (
                                <div key={i} className="welc-recent-item">
                                    <span className="welc-recent-icon">{item.icon}</span>
                                    <span className="welc-recent-title">{item.title}</span>
                                    <span className="welc-recent-time">{item.time}</span>
                                </div>
                            ))}
                        </div>

                        {/* Stats */}
                        <div className="welc-section-title" style={{ marginTop: 16 }}>Today's Stats</div>
                        <div className="welc-stats-grid">
                            <div className="welc-stat">
                                <div className="welc-stat-value">24</div>
                                <div className="welc-stat-label">Dispatches</div>
                            </div>
                            <div className="welc-stat">
                                <div className="welc-stat-value">42.3K</div>
                                <div className="welc-stat-label">Tokens</div>
                            </div>
                            <div className="welc-stat">
                                <div className="welc-stat-value">3.2h</div>
                                <div className="welc-stat-label">AI Hours</div>
                            </div>
                            <div className="welc-stat">
                                <div className="welc-stat-value">97%</div>
                                <div className="welc-stat-label">Success Rate</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
