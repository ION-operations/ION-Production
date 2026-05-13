import { useState, useMemo, useRef, useEffect } from 'react';
import { useAIMOS } from '../hooks/useAIMOS';
import { mcp, callTool } from '../services/mcpClient';

// ─── Types ───

interface ThreadGroup {
    threadId: string;
    participants: string[];
    messages: ThreadMessage[];
    lastActivity: string;
}

interface ThreadMessage {
    id: string;
    from: string;
    to: string;
    content: string;
    type: string;
    priority: string;
    timestamp: string;
    threadId: string;
}

type FilterType = 'all' | 'discussion' | 'task_handoff' | 'problem_solving' | 'status_update' | 'urgent';

// ─── Component ───

export function AgentCommsPage() {
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
    const [filterType, setFilterType] = useState<FilterType>('all');
    const [selectedThread, setSelectedThread] = useState<string | null>(null);
    const [composeOpen, setComposeOpen] = useState(false);
    const [composeFrom, setComposeFrom] = useState('Sev');
    const [composeTo, setComposeTo] = useState('');
    const [composeContent, setComposeContent] = useState('');
    const [composeType, setComposeType] = useState<FilterType>('discussion');
    const [sending, setSending] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);

    const aimos = useAIMOS({
        pollInterval: 5000,
        pollDomains: ['messages'],
    });

    // Derive agents from messages
    const agents = useMemo(() => {
        const agentSet = new Map<string, { name: string; messageCount: number; lastSeen: string }>();
        aimos.aiMessages.forEach(msg => {
            [msg.from_ai, msg.to_ai].forEach(name => {
                if (!name) return;
                const existing = agentSet.get(name);
                agentSet.set(name, {
                    name,
                    messageCount: (existing?.messageCount || 0) + 1,
                    lastSeen: msg.timestamp || existing?.lastSeen || '',
                });
            });
        });
        return Array.from(agentSet.values()).sort((a, b) => b.messageCount - a.messageCount);
    }, [aimos.aiMessages]);

    // Group messages into threads
    const threads = useMemo(() => {
        const threadMap = new Map<string, ThreadGroup>();
        const messages = aimos.aiMessages
            .filter(msg => {
                if (selectedAgent && msg.from_ai !== selectedAgent && msg.to_ai !== selectedAgent) return false;
                if (filterType !== 'all' && msg.message_type !== filterType) return false;
                return true;
            })
            .map(msg => ({
                id: msg.id || `msg-${Math.random().toString(36).slice(2)}`,
                from: msg.from_ai,
                to: msg.to_ai,
                content: msg.content,
                type: msg.message_type || 'discussion',
                priority: msg.priority || 'medium',
                timestamp: msg.timestamp || '',
                threadId: msg.thread_id || 'general',
            }));

        messages.forEach(msg => {
            const tid = msg.threadId;
            if (!threadMap.has(tid)) {
                threadMap.set(tid, {
                    threadId: tid,
                    participants: [],
                    messages: [],
                    lastActivity: msg.timestamp,
                });
            }
            const thread = threadMap.get(tid)!;
            thread.messages.push(msg);
            if (!thread.participants.includes(msg.from)) thread.participants.push(msg.from);
            if (!thread.participants.includes(msg.to)) thread.participants.push(msg.to);
            thread.lastActivity = msg.timestamp || thread.lastActivity;
        });

        return Array.from(threadMap.values()).sort((a, b) =>
            (b.lastActivity || '').localeCompare(a.lastActivity || '')
        );
    }, [aimos.aiMessages, selectedAgent, filterType]);

    // Active thread messages
    const activeThread = selectedThread
        ? threads.find(t => t.threadId === selectedThread)
        : threads[0];

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [activeThread?.messages.length]);

    // Send message
    const handleSend = async () => {
        if (!composeContent.trim() || !composeTo) return;
        setSending(true);
        try {
            await callTool('send_ai_message', {
                from_ai: composeFrom,
                to_ai: composeTo,
                content: composeContent,
                message_type: composeType,
                priority: 'medium',
            });
            setComposeContent('');
            // Refresh messages
            setTimeout(() => aimos.refreshMessages(), 500);
        } catch (e) {
            console.error('Failed to send message:', e);
        } finally {
            setSending(false);
        }
    };

    const agentColor = (name: string) => {
        const colors: Record<string, string> = {
            'Sev': '#00d4ff',
            'Antigravity': '#00d4ff',
            'Aether': '#4ecdc4',
            'Codex': '#a855f7',
            'Claude': '#CC7722',
            'Opus': '#ff6b35',
            'Gemini': '#4285F4',
        };
        // Match partial names
        for (const [key, color] of Object.entries(colors)) {
            if (name.toLowerCase().includes(key.toLowerCase())) return color;
        }
        // Hash fallback
        let hash = 0;
        for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
        const hue = Math.abs(hash) % 360;
        return `hsl(${hue}, 70%, 60%)`;
    };

    const priorityStyles: Record<string, { color: string; bg: string }> = {
        urgent: { color: '#ff6b6b', bg: 'rgba(255, 107, 107, 0.1)' },
        high: { color: '#ffd93d', bg: 'rgba(255, 217, 61, 0.08)' },
        medium: { color: '#00d4ff', bg: 'rgba(0, 212, 255, 0.06)' },
        low: { color: '#888', bg: 'rgba(136, 136, 136, 0.04)' },
    };

    const typeIcon: Record<string, string> = {
        discussion: '💬',
        task_handoff: '🔄',
        problem_solving: '🧩',
        status_update: '📊',
        urgent: '🚨',
        profile_sharing: '👤',
    };

    return (
        <div className="comms-page">
            {/* ─── Left: Agent Sidebar ─── */}
            <div className="comms-sidebar">
                <div className="comms-sidebar-header">
                    <span className="comms-sidebar-title">Agents</span>
                    <span className="comms-sidebar-count">{agents.length}</span>
                </div>

                {/* Filter bar */}
                <div className="comms-filter-bar">
                    <select
                        className="comms-filter-select"
                        value={filterType}
                        onChange={e => setFilterType(e.target.value as FilterType)}
                    >
                        <option value="all">All Types</option>
                        <option value="discussion">💬 Discussion</option>
                        <option value="task_handoff">🔄 Task Handoff</option>
                        <option value="problem_solving">🧩 Problem Solving</option>
                        <option value="status_update">📊 Status Update</option>
                        <option value="urgent">🚨 Urgent</option>
                    </select>
                </div>

                {/* Agent list */}
                <div className="comms-agent-list">
                    <div
                        className={`comms-agent-item ${!selectedAgent ? 'active' : ''}`}
                        onClick={() => setSelectedAgent(null)}
                    >
                        <span className="comms-agent-dot" style={{ background: '#888' }} />
                        <span className="comms-agent-name">All Agents</span>
                        <span className="comms-agent-badge">{aimos.aiMessages.length}</span>
                    </div>
                    {agents.map(agent => (
                        <div
                            key={agent.name}
                            className={`comms-agent-item ${selectedAgent === agent.name ? 'active' : ''}`}
                            onClick={() => setSelectedAgent(agent.name)}
                        >
                            <span className="comms-agent-dot" style={{ background: agentColor(agent.name) }} />
                            <span className="comms-agent-name">{agent.name}</span>
                            <span className="comms-agent-badge">{agent.messageCount}</span>
                        </div>
                    ))}
                </div>

                {/* Thread list */}
                <div className="comms-threads-header">Threads ({threads.length})</div>
                <div className="comms-thread-list">
                    {threads.map(t => (
                        <div
                            key={t.threadId}
                            className={`comms-thread-item ${activeThread?.threadId === t.threadId ? 'active' : ''}`}
                            onClick={() => setSelectedThread(t.threadId)}
                        >
                            <span className="comms-thread-id">{t.threadId.slice(0, 12)}</span>
                            <span className="comms-thread-parts">
                                {t.participants.slice(0, 3).join(', ')}
                            </span>
                            <span className="comms-thread-count">{t.messages.length}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ─── Center: Message Thread ─── */}
            <div className="comms-main">
                <div className="comms-main-header">
                    <span className="comms-main-title">
                        {activeThread
                            ? `Thread: ${activeThread.threadId.slice(0, 20)}`
                            : 'No threads'}
                    </span>
                    <span className="comms-main-meta">
                        {activeThread ? `${activeThread.messages.length} messages · ${activeThread.participants.join(', ')}` : ''}
                    </span>
                    <span className="comms-main-spacer" />
                    <button
                        className="comms-compose-toggle"
                        onClick={() => setComposeOpen(!composeOpen)}
                    >
                        ✏️ Compose
                    </button>
                    <button className="comms-refresh-btn" onClick={() => aimos.refreshMessages()}>
                        ⟳
                    </button>
                </div>

                {/* Messages */}
                <div className="comms-messages" ref={scrollRef}>
                    {activeThread ? (
                        activeThread.messages.map(msg => {
                            const ps = priorityStyles[msg.priority] || priorityStyles.medium;
                            return (
                                <div
                                    key={msg.id}
                                    className={`comms-message ${msg.priority === 'urgent' ? 'urgent' : ''}`}
                                    style={{ borderLeftColor: agentColor(msg.from) }}
                                >
                                    <div className="comms-message-header">
                                        <span className="comms-message-from" style={{ color: agentColor(msg.from) }}>
                                            {msg.from}
                                        </span>
                                        <span className="comms-message-arrow">→</span>
                                        <span className="comms-message-to" style={{ color: agentColor(msg.to) }}>
                                            {msg.to}
                                        </span>
                                        <span className="comms-message-type" style={{ background: ps.bg, color: ps.color }}>
                                            {typeIcon[msg.type] || '💬'} {msg.type.replace(/_/g, ' ')}
                                        </span>
                                        {msg.priority === 'urgent' && (
                                            <span className="comms-priority-urgent">URGENT</span>
                                        )}
                                        {msg.priority === 'high' && (
                                            <span className="comms-priority-high">HIGH</span>
                                        )}
                                        <span className="comms-message-spacer" />
                                        <span className="comms-message-time">{msg.timestamp}</span>
                                    </div>
                                    <div className="comms-message-content">
                                        {msg.content}
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        <div className="comms-empty">
                            <div className="comms-empty-icon">📡</div>
                            <div className="comms-empty-text">
                                {aimos.connected
                                    ? 'No messages yet. Agent comms will appear here.'
                                    : 'MCP offline — connect to see agent messages.'}
                            </div>
                        </div>
                    )}
                </div>

                {/* ─── Compose Bar ─── */}
                {composeOpen && (
                    <div className="comms-compose">
                        <div className="comms-compose-header">
                            <select
                                className="comms-compose-select"
                                value={composeFrom}
                                onChange={e => setComposeFrom(e.target.value)}
                            >
                                <option value="Sev">From: Sev</option>
                                <option value="Antigravity">From: Antigravity</option>
                                <option value="JOC">From: JOC</option>
                            </select>
                            <span className="comms-compose-arrow">→</span>
                            <select
                                className="comms-compose-select"
                                value={composeTo}
                                onChange={e => setComposeTo(e.target.value)}
                            >
                                <option value="">To agent...</option>
                                {agents.map(a => (
                                    <option key={a.name} value={a.name}>{a.name}</option>
                                ))}
                                <option value="Aether">Aether</option>
                                <option value="Codex">Codex</option>
                                <option value="Claude">Claude</option>
                            </select>
                            <select
                                className="comms-compose-select"
                                value={composeType}
                                onChange={e => setComposeType(e.target.value as FilterType)}
                            >
                                <option value="discussion">💬 Discussion</option>
                                <option value="task_handoff">🔄 Handoff</option>
                                <option value="problem_solving">🧩 Problem</option>
                                <option value="status_update">📊 Update</option>
                                <option value="urgent">🚨 Urgent</option>
                            </select>
                        </div>
                        <div className="comms-compose-body">
                            <textarea
                                className="comms-compose-textarea"
                                placeholder="Type your message..."
                                value={composeContent}
                                onChange={e => setComposeContent(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSend();
                                }}
                                rows={3}
                            />
                            <button
                                className="comms-send-btn"
                                onClick={handleSend}
                                disabled={!composeContent.trim() || !composeTo || sending}
                            >
                                {sending ? '⟳' : '▶'} {sending ? 'Sending...' : 'Send'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
