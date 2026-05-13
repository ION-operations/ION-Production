import { useState, useEffect, useCallback, useRef } from 'react';
import { checkHealth, callTool, getConnectionState, getLastLatency, onConnectionChange, mcp } from '../services/mcpClient';
import type { ConnectionState, AIMessage } from '../services/mcpClient';

interface ToolInfo {
    name: string;
    description?: string;
}

interface HealthData {
    status: string;
    mode?: string;
    ready?: boolean;
    tools_count?: number;
    [key: string]: unknown;
}

export function MCPDiagnosticsPage() {
    const [connectionState, setConnectionState] = useState<ConnectionState>(getConnectionState());
    const [latency, setLatency] = useState(getLastLatency());
    const [healthData, setHealthData] = useState<HealthData | null>(null);
    const [tools, setTools] = useState<ToolInfo[]>([]);
    const [messages, setMessages] = useState<AIMessage[]>([]);
    const [lastCheck, setLastCheck] = useState<string>('Never');
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [isLoadingTools, setIsLoadingTools] = useState(false);
    const [isLoadingHealth, setIsLoadingHealth] = useState(false);
    const [isLoadingMessages, setIsLoadingMessages] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [toolFilter, setToolFilter] = useState('');
    const intervalRef = useRef<number | null>(null);

    // Connection state listener
    useEffect(() => {
        const unsub = onConnectionChange((state) => {
            setConnectionState(state);
            setLatency(getLastLatency());
        });
        return () => { unsub(); };
    }, []);

    // Health check
    const runHealthCheck = useCallback(async () => {
        setIsLoadingHealth(true);
        setError(null);
        try {
            const healthy = await checkHealth();
            if (healthy) {
                // Try to get detailed health from the bridge
                try {
                    const resp = await fetch('http://127.0.0.1:5001/health', {
                        signal: AbortSignal.timeout(5000),
                    });
                    if (resp.ok) {
                        const data = await resp.json();
                        setHealthData(data);
                    }
                } catch {
                    setHealthData({ status: 'up', mode: 'connected' });
                }
            } else {
                setHealthData(null);
            }
            setLastCheck(new Date().toLocaleTimeString());
            setLatency(getLastLatency());
        } catch (err) {
            setError(`Health check failed: ${err}`);
            setHealthData(null);
        } finally {
            setIsLoadingHealth(false);
        }
    }, []);

    // Load tools list
    const loadTools = useCallback(async () => {
        setIsLoadingTools(true);
        try {
            const result = await callTool<{ tools?: ToolInfo[] }>('list_tools', {});
            if (result?.tools) {
                setTools(result.tools);
            } else {
                // Try tools/list RPC
                try {
                    const resp = await fetch('http://127.0.0.1:5001/mcp', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/list' }),
                        signal: AbortSignal.timeout(30000),
                    });
                    if (resp.ok) {
                        const data = await resp.json();
                        if (data.result?.tools) {
                            setTools(data.result.tools);
                        }
                    }
                } catch {
                    // Fallback: try MCP execute endpoint
                    const memStats = await mcp.getMemoryStats();
                    if (memStats) {
                        setTools([{ name: 'get_memory_stats', description: 'Working ✓' }]);
                    }
                }
            }
        } catch (err) {
            setError(`Failed to load tools: ${err}`);
        } finally {
            setIsLoadingTools(false);
        }
    }, []);

    // Load messages
    const loadMessages = useCallback(async () => {
        setIsLoadingMessages(true);
        try {
            const result = await mcp.getAIMessages(50);
            if (result?.messages) {
                setMessages(result.messages);
            }
        } catch (err) {
            setError(`Failed to load messages: ${err}`);
        } finally {
            setIsLoadingMessages(false);
        }
    }, []);

    // Auto-refresh polling
    useEffect(() => {
        if (autoRefresh) {
            runHealthCheck();
            intervalRef.current = window.setInterval(() => {
                runHealthCheck();
            }, 5000);
        }
        return () => {
            if (intervalRef.current) {
                window.clearInterval(intervalRef.current);
            }
        };
    }, [autoRefresh, runHealthCheck]);

    // Initial load
    useEffect(() => {
        loadTools();
        loadMessages();
    }, [loadTools, loadMessages]);

    const statusColor = connectionState === 'connected' ? 'var(--color-success, #22c55e)' :
        connectionState === 'connecting' ? 'var(--color-warning, #eab308)' :
            'var(--color-error, #ef4444)';

    const filteredTools = tools.filter(t =>
        !toolFilter || t.name.toLowerCase().includes(toolFilter.toLowerCase())
    );

    return (
        <div className="mcp-diagnostics" id="mcp-diagnostics-page">
            {/* Header */}
            <div className="mcp-diag-header">
                <div className="mcp-diag-title">
                    <span className="mcp-diag-dot" style={{ background: statusColor }} />
                    <h1>MCP Server Diagnostics</h1>
                    <span className="mcp-diag-status-badge" style={{ color: statusColor }}>
                        {connectionState.toUpperCase()}
                    </span>
                </div>
                <div className="mcp-diag-controls">
                    <label className="mcp-diag-toggle">
                        <input
                            type="checkbox"
                            checked={autoRefresh}
                            onChange={(e) => setAutoRefresh(e.target.checked)}
                        />
                        Auto-refresh (5s)
                    </label>
                    <button className="mcp-diag-btn" onClick={runHealthCheck} disabled={isLoadingHealth}>
                        {isLoadingHealth ? '⟳ Checking...' : '🔍 Check Health'}
                    </button>
                    <button className="mcp-diag-btn" onClick={loadTools} disabled={isLoadingTools}>
                        {isLoadingTools ? '⟳ Loading...' : '📋 Refresh Tools'}
                    </button>
                    <button className="mcp-diag-btn" onClick={loadMessages} disabled={isLoadingMessages}>
                        {isLoadingMessages ? '⟳ Loading...' : '💬 Refresh Messages'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="mcp-diag-error">
                    ⚠️ {error}
                    <button onClick={() => setError(null)}>✕</button>
                </div>
            )}

            {/* Status Cards */}
            <div className="mcp-diag-cards">
                <div className="mcp-diag-card">
                    <div className="mcp-diag-card-label">Connection</div>
                    <div className="mcp-diag-card-value" style={{ color: statusColor }}>
                        {connectionState === 'connected' ? '● ONLINE' : connectionState === 'connecting' ? '◐ CONNECTING' : '○ OFFLINE'}
                    </div>
                </div>
                <div className="mcp-diag-card">
                    <div className="mcp-diag-card-label">Latency</div>
                    <div className="mcp-diag-card-value">{latency}ms</div>
                </div>
                <div className="mcp-diag-card">
                    <div className="mcp-diag-card-label">Tools Loaded</div>
                    <div className="mcp-diag-card-value">{tools.length}</div>
                </div>
                <div className="mcp-diag-card">
                    <div className="mcp-diag-card-label">Messages</div>
                    <div className="mcp-diag-card-value">{messages.length}</div>
                </div>
                <div className="mcp-diag-card">
                    <div className="mcp-diag-card-label">Last Check</div>
                    <div className="mcp-diag-card-value mcp-diag-card-small">{lastCheck}</div>
                </div>
                <div className="mcp-diag-card">
                    <div className="mcp-diag-card-label">Mode</div>
                    <div className="mcp-diag-card-value mcp-diag-card-small">
                        {healthData?.mode || 'unknown'}
                    </div>
                </div>
            </div>

            {/* Health Detail */}
            {healthData && (
                <div className="mcp-diag-section">
                    <h2>Health Response</h2>
                    <pre className="mcp-diag-pre">{JSON.stringify(healthData, null, 2)}</pre>
                </div>
            )}

            {/* Two-column layout: Tools + Messages */}
            <div className="mcp-diag-columns">
                {/* Tools List */}
                <div className="mcp-diag-section">
                    <div className="mcp-diag-section-header">
                        <h2>Tools ({filteredTools.length}{toolFilter ? ` / ${tools.length}` : ''})</h2>
                        <input
                            className="mcp-diag-search"
                            type="text"
                            placeholder="Filter tools..."
                            value={toolFilter}
                            onChange={(e) => setToolFilter(e.target.value)}
                        />
                    </div>
                    <div className="mcp-diag-tool-list">
                        {filteredTools.length === 0 && !isLoadingTools && (
                            <div className="mcp-diag-empty">No tools loaded. Click "Refresh Tools".</div>
                        )}
                        {isLoadingTools && <div className="mcp-diag-empty">Loading tools...</div>}
                        {filteredTools.map((tool, i) => (
                            <div key={i} className="mcp-diag-tool-item">
                                <span className="mcp-diag-tool-name">{tool.name}</span>
                                {tool.description && (
                                    <span className="mcp-diag-tool-desc">{tool.description}</span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Messages */}
                <div className="mcp-diag-section">
                    <h2>Agent Messages ({messages.length})</h2>
                    <div className="mcp-diag-message-list">
                        {messages.length === 0 && !isLoadingMessages && (
                            <div className="mcp-diag-empty">No messages found.</div>
                        )}
                        {isLoadingMessages && <div className="mcp-diag-empty">Loading messages...</div>}
                        {messages.slice().reverse().map((msg, i) => (
                            <div key={i} className="mcp-diag-message-item">
                                <div className="mcp-diag-msg-header">
                                    <span className="mcp-diag-msg-from">{msg.from_ai}</span>
                                    <span className="mcp-diag-msg-arrow">→</span>
                                    <span className="mcp-diag-msg-to">{msg.to_ai}</span>
                                    {msg.priority && (
                                        <span className={`mcp-diag-msg-priority mcp-diag-priority-${msg.priority}`}>
                                            {msg.priority}
                                        </span>
                                    )}
                                    {msg.timestamp && (
                                        <span className="mcp-diag-msg-time">
                                            {new Date(msg.timestamp).toLocaleTimeString()}
                                        </span>
                                    )}
                                </div>
                                {msg.thread_id && (
                                    <div className="mcp-diag-msg-thread">Thread: {msg.thread_id}</div>
                                )}
                                <div className="mcp-diag-msg-content">
                                    {msg.content.length > 300 ? msg.content.substring(0, 300) + '...' : msg.content}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
