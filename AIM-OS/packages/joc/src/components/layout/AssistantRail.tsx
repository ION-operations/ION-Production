import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useAIMOS } from '../../hooks/useAIMOS';
import type { AssistantRailMode, DataStatus } from '../../store/panelRegistry';
import { DATA_STATUS_CONFIG } from '../../store/panelRegistry';
import { CloseIcon, ChevronLeftIcon, ChevronRightIcon } from '../icons';

// ═══════════════════════════════════════════════════════════════════
// AssistantRail — The persistent AIMOS intelligence companion.
// Canon Law 4: Present on EVERY workspace. Never hidden.
// Four modes: Chat, Context, Actions, Memory/Evidence.
// ═══════════════════════════════════════════════════════════════════

// ─── Mode Definitions ────────────────────────────────────────────

const RAIL_MODES: Array<{
    mode: AssistantRailMode;
    label: string;
    shortcut: string;
    icon: string;
    description: string;
}> = [
        { mode: 'chat', label: 'Chat', shortcut: '1', icon: '💬', description: 'Direct conversation with AIMOS' },
        { mode: 'context', label: 'Context', shortcut: '2', icon: '🔍', description: 'What AIMOS knows about your current focus' },
        { mode: 'actions', label: 'Actions', shortcut: '3', icon: '⚡', description: 'Proposed operations and approvals' },
        { mode: 'memory', label: 'Memory', shortcut: '4', icon: '🧠', description: 'Evidence, atoms, and reasoning chains' },
    ];

// ─── Chat Message Types ──────────────────────────────────────────

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    confidence?: number;
    evidenceCount?: number;
}

// ─── Chat Mode ───────────────────────────────────────────────────

function ChatMode() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: 'welcome',
            role: 'system',
            content: 'AIMOS Assistant ready. I have access to all system context — memory, goals, evidence, and agent state.',
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { connected } = useAIMOS({ pollDomains: [], pollInterval: 60000 });

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    const handleSend = useCallback(() => {
        if (!input.trim()) return;

        const userMsg: ChatMessage = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');

        // Simulated assistant response — will be replaced with real MCP integration
        setTimeout(() => {
            const assistantMsg: ChatMessage = {
                id: `asst-${Date.now()}`,
                role: 'assistant',
                content: `Processing: "${userMsg.content}"\n\nMCP integration pending — this will connect to the Oracle system for real responses.`,
                timestamp: new Date(),
                confidence: 0.0,
            };
            setMessages(prev => [...prev, assistantMsg]);
        }, 800);
    }, [input]);

    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }, [handleSend]);

    return (
        <div className="rail-chat">
            <div className="rail-chat-messages">
                {messages.map(msg => (
                    <div key={msg.id} className={`rail-chat-msg rail-chat-msg--${msg.role}`}>
                        <div className="rail-chat-msg-content">{msg.content}</div>
                        <div className="rail-chat-msg-meta">
                            <span className="rail-chat-msg-time">
                                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                            {msg.confidence !== undefined && msg.confidence > 0 && (
                                <span className="rail-chat-msg-confidence" title="VIF Confidence">
                                    κ {msg.confidence.toFixed(2)}
                                </span>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            <div className="rail-chat-input-area">
                <div className={`rail-chat-connection ${connected ? 'connected' : 'disconnected'}`}>
                    <span className="rail-chat-connection-dot" />
                    {connected ? 'AIMOS' : 'Offline'}
                </div>
                <div className="rail-chat-input-row">
                    <textarea
                        className="rail-chat-input"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Message AIMOS..."
                        rows={1}
                        aria-label="Message AIMOS assistant"
                    />
                    <button
                        className="rail-chat-send"
                        onClick={handleSend}
                        disabled={!input.trim()}
                        aria-label="Send message"
                        title="Send (Enter)"
                    >
                        ↑
                    </button>
                </div>
            </div>
        </div>
    );
}

// ─── Context Mode ────────────────────────────────────────────────

function ContextMode() {
    const { connected, memory, consciousness, goals, latency } = useAIMOS({
        pollDomains: ['memory', 'consciousness', 'goals'],
        pollInterval: 8000,
    });

    const dataStatus: DataStatus = connected ? 'live' : 'offline';
    const statusConfig = DATA_STATUS_CONFIG[dataStatus];

    return (
        <div className="rail-context">
            {dataStatus !== 'live' && (
                <div className={`rail-data-status ${statusConfig.cssClass}`}>
                    <span>{statusConfig.icon}</span>
                    <span>{statusConfig.label}</span>
                </div>
            )}

            <div className="rail-context-section">
                <div className="rail-section-header">Workspace Context</div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Active Workspace</span>
                    <span className="rail-context-value">—</span>
                </div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Selected Item</span>
                    <span className="rail-context-value">None</span>
                </div>
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">System State</div>
                <div className="rail-context-item">
                    <span className="rail-context-label">MCP Latency</span>
                    <span className="rail-context-value">{connected ? `${latency}ms` : '—'}</span>
                </div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Memory Atoms</span>
                    <span className="rail-context-value">{memory?.total_atoms ?? '—'}</span>
                </div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Cognitive Drift</span>
                    <span className="rail-context-value">
                        {consciousness?.cognitive_drift != null
                            ? (consciousness.cognitive_drift as number).toFixed(3)
                            : '—'}
                    </span>
                </div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Active Goals</span>
                    <span className="rail-context-value">{goals.length}</span>
                </div>
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">Related Context</div>
                <div className="rail-context-hint">
                    Select an item in the workspace to see related memory atoms, evidence chains, and temporal context.
                </div>
            </div>
        </div>
    );
}

// ─── Actions Mode ────────────────────────────────────────────────

function ActionsMode() {
    const { connected } = useAIMOS({ pollDomains: [], pollInterval: 60000 });

    return (
        <div className="rail-actions">
            <div className="rail-context-section">
                <div className="rail-section-header">
                    Oracle Status
                    <span className="rail-oracle-badge">SUPERVISED</span>
                </div>
                <div className="rail-context-hint">
                    Autonomy level: Supervised. Actions require human approval.
                </div>
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">Pending Approvals</div>
                {connected ? (
                    <div className="rail-actions-empty">
                        <div className="rail-actions-empty-icon">✓</div>
                        <div>No pending approvals</div>
                    </div>
                ) : (
                    <div className="rail-actions-empty">
                        <div className="rail-actions-empty-icon">⊘</div>
                        <div>MCP offline — cannot fetch approvals</div>
                    </div>
                )}
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">Recent Actions</div>
                <div className="rail-context-hint">
                    Completed and reversed actions will appear here with full audit trail.
                </div>
            </div>
        </div>
    );
}

// ─── Memory Mode ─────────────────────────────────────────────────

function MemoryMode() {
    const [searchQuery, setSearchQuery] = useState('');
    const { connected, memory } = useAIMOS({
        pollDomains: ['memory'],
        pollInterval: 30000,
    });

    const dataStatus: DataStatus = connected ? 'live' : 'offline';
    const statusConfig = DATA_STATUS_CONFIG[dataStatus];

    return (
        <div className="rail-memory">
            {dataStatus !== 'live' && (
                <div className={`rail-data-status ${statusConfig.cssClass}`}>
                    <span>{statusConfig.icon}</span>
                    <span>{statusConfig.label}</span>
                </div>
            )}

            <div className="rail-memory-search">
                <input
                    type="text"
                    className="rail-memory-search-input"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search memory atoms..."
                    aria-label="Search AIMOS memory"
                />
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">Memory Overview</div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Total Atoms</span>
                    <span className="rail-context-value">{memory?.total_atoms ?? '—'}</span>
                </div>
                <div className="rail-context-item">
                    <span className="rail-context-label">Tags</span>
                    <span className="rail-context-value">{memory?.total_tags ?? '—'}</span>
                </div>
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">Evidence Chains</div>
                <div className="rail-context-hint">
                    Select a data point in any workspace to see its evidence chain from the Shared Evidence Graph (SEG).
                </div>
            </div>

            <div className="rail-context-section">
                <div className="rail-section-header">Related Sessions</div>
                <div className="rail-context-hint">
                    Temporal context from TCS will show related sessions and their outcomes here.
                </div>
            </div>
        </div>
    );
}

// ─── Mode Content Resolver ───────────────────────────────────────

function RailContent({ mode }: { mode: AssistantRailMode }) {
    switch (mode) {
        case 'chat': return <ChatMode />;
        case 'context': return <ContextMode />;
        case 'actions': return <ActionsMode />;
        case 'memory': return <MemoryMode />;
    }
}

// ─── Shared state for external triggers (RightIconBar) ──────────
let _setExpanded: React.Dispatch<React.SetStateAction<boolean>> | null = null;
let _setMode: ((m: AssistantRailMode) => void) | null = null;

export function openAssistantRail(mode?: AssistantRailMode) {
    if (mode && _setMode) _setMode(mode);
    if (_setExpanded) _setExpanded(true);
}

export function toggleAssistantRail() {
    if (_setExpanded) _setExpanded(prev => !prev);
}

// ─── Assistant Rail Component ────────────────────────────────

export function AssistantRail() {
    const [activeMode, setActiveMode] = useState<AssistantRailMode>('chat');
    const [expanded, setExpanded] = useState(false);

    // Register setters for external access
    useEffect(() => {
        _setExpanded = setExpanded;
        _setMode = setActiveMode;
        return () => { _setExpanded = null; _setMode = null; };
    }, []);

    // Keyboard shortcuts: Ctrl+1/2/3/4 switch modes, Ctrl+\ toggles
    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (!e.ctrlKey && !e.metaKey) return;

            const tag = (e.target as HTMLElement).tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA') return;

            switch (e.key) {
                case '1': e.preventDefault(); setActiveMode('chat'); setExpanded(true); break;
                case '2': e.preventDefault(); setActiveMode('context'); setExpanded(true); break;
                case '3': e.preventDefault(); setActiveMode('actions'); setExpanded(true); break;
                case '4': e.preventDefault(); setActiveMode('memory'); setExpanded(true); break;
                case '\\': e.preventDefault(); setExpanded(prev => !prev); break;
            }
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, []);

    // When not expanded, render NOTHING — no collapsed bar, no icons, nothing.
    if (!expanded) return null;

    return (
        <div className="assistant-rail assistant-rail--expanded" role="complementary" aria-label="J.A.R.V.I.S. Assistant">
            {/* Mode Tabs */}
            <div className="rail-mode-tabs" role="tablist">
                {RAIL_MODES.map(m => (
                    <button
                        key={m.mode}
                        className={`rail-mode-tab ${activeMode === m.mode ? 'active' : ''}`}
                        onClick={() => setActiveMode(m.mode)}
                        title={`${m.label} (Ctrl+${m.shortcut})`}
                        role="tab"
                        aria-selected={activeMode === m.mode}
                        aria-label={m.description}
                    >
                        <span className="rail-mode-icon">{m.icon}</span>
                        <span className="rail-mode-label">{m.label}</span>
                    </button>
                ))}
                <button
                    className="rail-collapse-btn"
                    onClick={() => setExpanded(false)}
                    title="Close (Ctrl+\)"
                    aria-label="Close assistant rail"
                >
                    <ChevronRightIcon size={12} />
                </button>
            </div>

            {/* Mode Content */}
            <div className="rail-content" role="tabpanel">
                <RailContent mode={activeMode} />
            </div>
        </div>
    );
}
