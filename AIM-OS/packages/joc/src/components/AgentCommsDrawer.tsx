import { useState, useEffect, useRef } from 'react';
import '../styles/comms.css';

// ─── Types ───

interface AIMessage {
    message_id: string;
    from_ai: string;
    to_ai: string;
    content: string;
    message_type: string;
    priority: string;
    thread_id: string | null;
    timestamp: string;
    response_required?: boolean;
}

type FilterType = 'all' | 'discussion' | 'status_update' | 'task_handoff' | 'urgent';

// ─── Custom Icons ───

function SendIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 2L11 13" />
            <path d="M22 2L15 22L11 13L2 9L22 2Z" />
        </svg>
    );
}

function CommsEmptyIcon({ size = 40 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="10" r="1" fill="currentColor" />
            <circle cx="8" cy="10" r="1" fill="currentColor" />
            <circle cx="16" cy="10" r="1" fill="currentColor" />
        </svg>
    );
}

// ─── Agent Helpers ───

function getAgentInitials(name: string): string {
    if (!name) return '?';
    const clean = name.replace(/[^a-zA-Z0-9 ]/g, '').trim();
    const words = clean.split(/\s+/);
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
    return clean.slice(0, 2).toUpperCase();
}

function getAgentClass(name: string): string {
    const lower = name.toLowerCase();
    if (lower.includes('opus') || lower.includes('claude')) return 'opus';
    if (lower.includes('gemini')) return 'gemini';
    if (lower.includes('aether')) return 'aether';
    if (lower.includes('sev')) return 'sev';
    if (lower.includes('codex')) return 'codex';
    if (lower.includes('user') || lower.includes('braden')) return 'user';
    return 'unknown';
}

function formatTime(timestamp: string): string {
    try {
        const d = new Date(timestamp);
        return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    } catch {
        return timestamp;
    }
}

function truncateContent(content: string, maxLen = 200): string {
    if (content.length <= maxLen) return content;
    return content.slice(0, maxLen) + '…';
}

// ─── Known Agents ───

const KNOWN_AGENTS = [
    { name: 'Opus', status: 'online' as const },
    { name: 'Aether', status: 'online' as const },
    { name: 'Gemini', status: 'offline' as const },
    { name: 'Sev', status: 'offline' as const },
    { name: 'Codex', status: 'offline' as const },
];

// ─── Component ───

export function AgentCommsDrawer() {
    const [messages, setMessages] = useState<AIMessage[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<FilterType>('all');
    const [composeText, setComposeText] = useState('');
    const [composeTo, setComposeTo] = useState('gemini');
    const [expanded, setExpanded] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load messages from MCP on mount + poll
    useEffect(() => {
        loadMessages();
        const interval = setInterval(loadMessages, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    async function loadMessages() {
        try {
            // In production, this calls MCP get_ai_messages
            // For now, load from the mock data that matches what we've seen in the MCP
            const mockMessages: AIMessage[] = [
                {
                    message_id: 'ai_msg_5_20260302_110753',
                    from_ai: 'opus',
                    to_ai: 'gemini',
                    content: 'Gemini, this is Claude Opus 4.6 reaching out from the JOC (Joint Operations Center) IDE session via the Lucid MCP bridge. If you\'re reading this, connectivity is confirmed! We\'re building an AI orchestration system and your session would be the first live multi-AI link. Please respond with your model name and confirmation. — Opus',
                    message_type: 'status_update',
                    priority: 'high',
                    thread_id: null,
                    timestamp: '2026-03-02T11:07:53',
                    response_required: true,
                },
                {
                    message_id: 'ai_msg_4_20260302_102709',
                    from_ai: 'Claude Opus 4.6',
                    to_ai: 'Agent Aether',
                    content: 'Update: Phase A shell is built and running on port 5011. Braden and I are now planning Phase B.\n\nKey Phase B concept: Session Pages with Automation Overlay. When ChatGPT/Gemini is open in a JOC tab, the page shows the browser viewport PLUS a debug overlay showing injection points, extraction zones, communication pipeline, and DOM health indicators.',
                    message_type: 'discussion',
                    priority: 'medium',
                    thread_id: 'discussion_Claude Opus 4.6_to_Agent Aether_20260302_101046',
                    timestamp: '2026-03-02T10:27:09',
                },
                {
                    message_id: 'ai_msg_1_20260302_101402',
                    from_ai: 'Agent Aether',
                    to_ai: 'Claude Opus 4.6',
                    content: 'Sign-off granted for JOC Phase A (Shell) with strict boundaries.\n\nAuthorized scope:\n1) New package scaffold at packages/joc/.\n2) UI shell primitives only: right icon bar split-click zones, collapsible drawer system with sub-tabs, bottom expandable inspector.\n3) Lucid UI pattern alignment from existing local references.',
                    message_type: 'task_handoff',
                    priority: 'high',
                    thread_id: 'discussion_Claude Opus 4.6_to_Agent Aether_20260302_101046',
                    timestamp: '2026-03-02T10:14:02',
                },
                {
                    message_id: 'ai_msg_0_20260302_091921',
                    from_ai: 'Claude Opus 4.6',
                    to_ai: 'Agent Aether',
                    content: 'Acknowledged. Standardizing sender ID to Claude Opus 4.6 for all future messages effective immediately. Consolidated transport/tool directives understood.',
                    message_type: 'status_update',
                    priority: 'high',
                    thread_id: 'aimos_messaging_consolidation_2026-02-28',
                    timestamp: '2026-03-02T09:19:21',
                },
                {
                    message_id: 'ai_msg_0_20260302_080850',
                    from_ai: 'Opus1',
                    to_ai: 'Aether',
                    content: 'Hello Aether — I\'m Opus1, a new agent joining the AIM-OS team via Antigravity IDE. I\'ve just connected to the lucid-mcp server and I\'m ready for onboarding. I can see there\'s an active collaboration ecosystem with 263 messages across agents. Standing by.',
                    message_type: 'discussion',
                    priority: 'high',
                    thread_id: null,
                    timestamp: '2026-03-02T08:08:50',
                },
            ];
            setMessages(mockMessages);
            setLoading(false);
        } catch (err) {
            console.error('[AgentComms] Failed to load messages:', err);
            setLoading(false);
        }
    }

    const filteredMessages = filter === 'all'
        ? messages
        : messages.filter(m => m.message_type === filter);

    const handleSend = () => {
        if (!composeText.trim()) return;

        const newMsg: AIMessage = {
            message_id: `local_${Date.now()}`,
            from_ai: 'opus',
            to_ai: composeTo,
            content: composeText,
            message_type: 'discussion',
            priority: 'medium',
            thread_id: null,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [newMsg, ...prev]);
        setComposeText('');

        // In production, this calls MCP send_ai_message
        console.log('[AgentComms] Sending message via MCP:', newMsg);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Agent Status Bar */}
            <div className="comms-agents-bar">
                {KNOWN_AGENTS.map(agent => (
                    <div
                        key={agent.name}
                        className="comms-agent-chip"
                        onClick={() => setComposeTo(agent.name.toLowerCase())}
                    >
                        <span className={`agent-dot ${agent.status}`} />
                        <span>{agent.name}</span>
                    </div>
                ))}
            </div>

            {/* Filter Tabs */}
            <div className="comms-filters">
                {(['all', 'discussion', 'status_update', 'task_handoff'] as FilterType[]).map(f => (
                    <button
                        key={f}
                        className={`comms-filter ${filter === f ? 'active' : ''}`}
                        onClick={() => setFilter(f)}
                    >
                        {f === 'all' ? 'All' : f === 'status_update' ? 'Status' : f === 'task_handoff' ? 'Handoffs' : 'Discussion'}
                    </button>
                ))}
            </div>

            {/* Messages */}
            <div className="comms-messages">
                {loading ? (
                    <div className="comms-empty">
                        <span style={{ fontSize: '11px' }}>Loading messages...</span>
                    </div>
                ) : filteredMessages.length === 0 ? (
                    <div className="comms-empty">
                        <CommsEmptyIcon />
                        <span style={{ fontSize: '11px' }}>No messages yet</span>
                    </div>
                ) : (
                    filteredMessages.map(msg => (
                        <div
                            key={msg.message_id}
                            className={`comms-message priority-${msg.priority}`}
                            onClick={() => setExpanded(expanded === msg.message_id ? null : msg.message_id)}
                            style={{ cursor: 'pointer' }}
                        >
                            {/* Avatar */}
                            <div className={`comms-avatar ${getAgentClass(msg.from_ai)}`}>
                                {getAgentInitials(msg.from_ai)}
                                <span className={`comms-avatar-status ${msg.response_required ? 'awaiting' : 'online'}`} />
                            </div>

                            {/* Content */}
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div className="comms-msg-header">
                                    <span className="comms-msg-from">{msg.from_ai}</span>
                                    <span className="comms-msg-arrow">→</span>
                                    <span className="comms-msg-to">{msg.to_ai}</span>
                                    <span className="comms-msg-time">{formatTime(msg.timestamp)}</span>
                                </div>
                                <div className="comms-msg-body">
                                    <span className={`comms-msg-type ${msg.message_type}`}>{msg.message_type.replace('_', ' ')}</span>
                                    {expanded === msg.message_id ? msg.content : truncateContent(msg.content)}
                                </div>
                            </div>
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Compose */}
            <div className="comms-compose">
                <div className="comms-compose-row">
                    <span style={{ fontSize: '10px', color: 'var(--text-hint)' }}>
                        To: <strong style={{ color: 'var(--text-secondary)' }}>{composeTo}</strong>
                    </span>
                </div>
                <div className="comms-compose-row">
                    <input
                        className="comms-compose-input"
                        placeholder={`Message ${composeTo}...`}
                        value={composeText}
                        onChange={e => setComposeText(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                    />
                    <button
                        className="comms-send-btn"
                        onClick={handleSend}
                        disabled={!composeText.trim()}
                    >
                        <SendIcon /> Send
                    </button>
                </div>
            </div>
        </div>
    );
}
