import { useState, useMemo } from 'react';

// ─── Types ───

type ActivityCategory = 'dispatch' | 'session' | 'system' | 'mcp' | 'agent';

interface ActivityEvent {
    id: string;
    category: ActivityCategory;
    icon: string;
    title: string;
    detail: string;
    timestamp: string;
    time: number;
    status?: 'success' | 'warning' | 'error' | 'info';
}

// ─── Mock ───

const ACTIVITIES: ActivityEvent[] = [
    { id: '1', category: 'dispatch', icon: '🚀', title: 'Parallel dispatch launched', detail: 'ChatGPT + Gemini · "Summarize JOC architecture"', timestamp: '20:45:12', time: Date.now() - 120000, status: 'success' },
    { id: '2', category: 'session', icon: '🔄', title: 'Session refreshed', detail: 'ChatGPT session cookies auto-refreshed', timestamp: '20:43:55', time: Date.now() - 195000, status: 'info' },
    { id: '3', category: 'agent', icon: '💬', title: 'Agent message sent', detail: 'Claude → Gemini: "Review my analysis approach"', timestamp: '20:42:30', time: Date.now() - 280000, status: 'info' },
    { id: '4', category: 'mcp', icon: '💾', title: 'Memory stored', detail: 'Synthesis result saved to CMC (atom_id: syn_0923)', timestamp: '20:41:15', time: Date.now() - 355000, status: 'success' },
    { id: '5', category: 'system', icon: '⚠', title: 'Token budget exceeded', detail: 'Context attachment 12.4K tokens > Ollama limit 8K', timestamp: '20:40:00', time: Date.now() - 430000, status: 'warning' },
    { id: '6', category: 'dispatch', icon: '✓', title: 'Dispatch completed', detail: 'Sequential dispatch (GPT→Gemini) · 4 responses · 8.2K tokens', timestamp: '20:38:22', time: Date.now() - 528000, status: 'success' },
    { id: '7', category: 'session', icon: '❌', title: 'Session expired', detail: 'Claude session cookies expired — reconnect needed', timestamp: '20:35:10', time: Date.now() - 720000, status: 'error' },
    { id: '8', category: 'mcp', icon: '🔍', title: 'HHNI search completed', detail: 'Semantic search "architecture patterns" → 14 results', timestamp: '20:33:45', time: Date.now() - 805000, status: 'info' },
    { id: '9', category: 'agent', icon: '🤝', title: 'Task handoff', detail: 'ChatGPT → Claude: "Please review and provide feedback"', timestamp: '20:30:00', time: Date.now() - 1030000, status: 'info' },
    { id: '10', category: 'system', icon: '🟢', title: 'System startup', detail: 'JOC initialized · MCP Core connected · BAS connected', timestamp: '20:25:00', time: Date.now() - 1330000, status: 'success' },
    { id: '11', category: 'dispatch', icon: '⚔', title: 'Debate dispatch started', detail: 'ChatGPT vs Gemini · "Best approach for state management"', timestamp: '20:22:14', time: Date.now() - 1500000, status: 'info' },
    { id: '12', category: 'mcp', icon: '📊', title: 'Statistics computed', detail: 'Token usage analysis: 42.3K today, avg 2.1K/dispatch', timestamp: '20:18:30', time: Date.now() - 1720000, status: 'info' },
];

// ─── Component ───

export function ActivityLogPage() {
    const [categoryFilter, setCategoryFilter] = useState<string>('all');
    const [search, setSearch] = useState('');

    const categories: { id: string; label: string; icon: string; color: string }[] = [
        { id: 'all', label: 'All', icon: '📋', color: '#e0e0e0' },
        { id: 'dispatch', label: 'Dispatch', icon: '🚀', color: '#4ecdc4' },
        { id: 'session', label: 'Session', icon: '🌐', color: '#00d4ff' },
        { id: 'agent', label: 'Agent', icon: '💬', color: '#a882ff' },
        { id: 'mcp', label: 'MCP', icon: '🔌', color: '#ffd93d' },
        { id: 'system', label: 'System', icon: '⚙', color: '#888' },
    ];

    const statusColors: Record<string, string> = {
        success: '#4ecdc4', warning: '#ffd93d', error: '#ff6b6b', info: '#00d4ff',
    };

    const filtered = useMemo(() => {
        return ACTIVITIES.filter(e => {
            if (categoryFilter !== 'all' && e.category !== categoryFilter) return false;
            if (search && !e.title.toLowerCase().includes(search.toLowerCase()) &&
                !e.detail.toLowerCase().includes(search.toLowerCase())) return false;
            return true;
        });
    }, [categoryFilter, search]);

    return (
        <div className="actlog-page">
            <div className="actlog-header">
                <div className="actlog-header-left">
                    <span className="actlog-title">📋 Activity Log</span>
                    <span className="actlog-subtitle">{ACTIVITIES.length} events today</span>
                </div>
                <div className="actlog-header-right">
                    <input className="actlog-search" placeholder="Search events..." value={search}
                        onChange={e => setSearch(e.target.value)} />
                    <button className="actlog-export-btn">📤 Export CSV</button>
                    <button className="actlog-export-btn">📤 Export JSON</button>
                </div>
            </div>

            <div className="actlog-body">
                {/* Category Filter */}
                <div className="actlog-filter-bar">
                    {categories.map(cat => (
                        <button key={cat.id}
                            className={`actlog-filter-btn ${categoryFilter === cat.id ? 'active' : ''}`}
                            onClick={() => setCategoryFilter(cat.id)}
                            style={categoryFilter === cat.id ? { borderBottomColor: cat.color } : {}}>
                            {cat.icon} {cat.label}
                        </button>
                    ))}
                </div>

                {/* Timeline */}
                <div className="actlog-timeline">
                    {filtered.map(event => (
                        <div key={event.id} className="actlog-event">
                            <div className="actlog-event-line">
                                <div className="actlog-event-dot" style={{ background: statusColors[event.status || 'info'] }} />
                            </div>
                            <div className="actlog-event-content">
                                <div className="actlog-event-header">
                                    <span className="actlog-event-icon">{event.icon}</span>
                                    <span className="actlog-event-title">{event.title}</span>
                                    <span className="actlog-event-badge"
                                        style={{ color: categories.find(c => c.id === event.category)?.color }}>
                                        {event.category}
                                    </span>
                                    <span className="actlog-event-time">{event.timestamp}</span>
                                </div>
                                <div className="actlog-event-detail">{event.detail}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
