import { useState, useRef, useEffect, useCallback } from 'react';
import * as basClient from '../services/basClient';

// ─── Types ───

interface CliCommand {
    id: string;
    input: string;
    output: string;
    status: 'running' | 'success' | 'error';
    timestamp: string;
    duration?: string;
    provider?: string;
}

interface QuickAction {
    id: string;
    label: string;
    command: string;
    icon: string;
    provider: string;
}

// ─── Quick Actions ───

const QUICK_ACTIONS: QuickAction[] = [
    { id: 'bas-health', label: 'BAS Health', command: 'bas:health', icon: '💚', provider: 'bas' },
    { id: 'bas-metrics', label: 'BAS Metrics', command: 'bas:metrics', icon: '📊', provider: 'bas' },
    { id: 'bas-providers', label: 'BAS Providers', command: 'bas:providers', icon: '🌐', provider: 'bas' },
    { id: 'bas-status', label: 'BAS Status', command: 'bas:status', icon: '📡', provider: 'bas' },
    { id: 'gem-chat', label: 'Gemini Chat', command: 'gemini chat "', icon: '✦', provider: 'gemini-cli' },
    { id: 'gem-models', label: 'List Models', command: 'gemini models list', icon: '📋', provider: 'gemini-cli' },
    { id: 'ollama-run', label: 'Ollama Run', command: 'ollama run llama3.2 "', icon: '🖥', provider: 'ollama' },
    { id: 'ollama-list', label: 'Ollama List', command: 'ollama list', icon: '📋', provider: 'ollama' },
    { id: 'mcp-health', label: 'MCP Health', command: 'curl http://localhost:5001/health', icon: '💜', provider: 'system' },
];

// ─── Component ───

export function CliTerminalPage() {
    const [history, setHistory] = useState<CliCommand[]>([]);
    const [input, setInput] = useState('');
    const [isRunning, setIsRunning] = useState(false);
    const outputRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (outputRef.current) {
            outputRef.current.scrollTop = outputRef.current.scrollHeight;
        }
    }, [history]);

    // ─── BAS command router ───
    const executeBASCommand = useCallback(async (command: string): Promise<{ output: string; status: 'success' | 'error' }> => {
        try {
            if (command === 'bas:health') {
                const health = await basClient.checkBASHealth();
                return {
                    output: JSON.stringify(health, null, 2),
                    status: 'success',
                };
            }
            if (command === 'bas:metrics') {
                const metrics = await basClient.getMetrics();
                return {
                    output: JSON.stringify(metrics, null, 2),
                    status: 'success',
                };
            }
            if (command === 'bas:providers') {
                const providers = await basClient.getProviders();
                const lines = providers.map(p =>
                    `  ${p.name.padEnd(12)} ${p.inputSelectors} input · ${p.submitSelectors} submit · ${p.responseSelectors} response   → ${p.url}`
                );
                return {
                    output: `Providers (${providers.length}):\n${lines.join('\n')}`,
                    status: 'success',
                };
            }
            if (command === 'bas:status') {
                const online = await basClient.isBASOnline();
                return {
                    output: `BAS Status: ${online ? '🟢 ONLINE (port 5002)' : '🔴 OFFLINE'}`,
                    status: 'success',
                };
            }
            // curl commands targeting BAS
            if (command.startsWith('curl ') && command.includes('localhost:5002')) {
                const urlMatch = command.match(/https?:\/\/[^\s"']+/);
                if (urlMatch) {
                    const res = await fetch(urlMatch[0]);
                    const data = await res.json();
                    return { output: JSON.stringify(data, null, 2), status: 'success' };
                }
            }
            // curl commands targeting MCP
            if (command.startsWith('curl ') && command.includes('localhost:5001')) {
                const urlMatch = command.match(/https?:\/\/[^\s"']+/);
                if (urlMatch) {
                    const res = await fetch(urlMatch[0]);
                    const data = await res.json();
                    return { output: JSON.stringify(data, null, 2), status: 'success' };
                }
            }
            return {
                output: `Command not routed to BAS. Available BAS commands:\n  bas:health    — Check BAS service health\n  bas:metrics   — Automation execution metrics\n  bas:providers — List supported AI providers\n  bas:status    — Quick online check`,
                status: 'success',
            };
        } catch (err: any) {
            return {
                output: `Error: ${err.message || 'Command failed'}`,
                status: 'error',
            };
        }
    }, []);

    const executeCommand = useCallback(async () => {
        if (!input.trim() || isRunning) return;

        const provider = input.startsWith('bas:') ? 'bas' :
            input.startsWith('gemini') ? 'gemini-cli' :
                input.startsWith('ollama') ? 'ollama' :
                    input.startsWith('curl') ? 'system' : 'system';

        const cmd: CliCommand = {
            id: String(Date.now()),
            input: input.trim(),
            output: '',
            status: 'running',
            timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
            provider,
        };
        setHistory(prev => [...prev, cmd]);
        setInput('');
        setIsRunning(true);

        const start = performance.now();
        const result = await executeBASCommand(cmd.input);
        const duration = `${((performance.now() - start) / 1000).toFixed(1)}s`;

        setHistory(prev => prev.map(c => c.id === cmd.id ? {
            ...c,
            output: result.output,
            status: result.status,
            duration,
        } : c));
        setIsRunning(false);
    }, [input, isRunning, executeBASCommand]);

    const loadQuickAction = (action: QuickAction) => {
        setInput(action.command);
        inputRef.current?.focus();
    };

    const clearHistory = () => setHistory([]);

    const providerColor: Record<string, string> = {
        'bas': '#61dafb',
        'gemini-cli': '#8b5cf6',
        'ollama': '#4ecdc4',
        'system': '#888',
    };

    return (
        <div className="cli-page">
            {/* ─── Header ─── */}
            <div className="cli-header">
                <div className="cli-header-left">
                    <span className="cli-title">⌨ CLI Terminal</span>
                    <span className="cli-subtitle">{history.length} commands · Gemini CLI + Ollama + System</span>
                </div>
                <div className="cli-header-right">
                    <button className="cli-clear-btn" onClick={clearHistory}>🗑 Clear</button>
                </div>
            </div>

            <div className="cli-body">
                {/* ─── Quick Actions ─── */}
                <div className="cli-sidebar">
                    <div className="cli-sidebar-title">Quick Commands</div>
                    {QUICK_ACTIONS.map(action => (
                        <button key={action.id} className="cli-quick-btn" onClick={() => loadQuickAction(action)}>
                            <span className="cli-quick-icon">{action.icon}</span>
                            <span className="cli-quick-label">{action.label}</span>
                            <span className="cli-quick-provider" style={{ color: providerColor[action.provider] || '#888' }}>
                                {action.provider}
                            </span>
                        </button>
                    ))}

                    <div className="cli-sidebar-title" style={{ marginTop: 16 }}>History ({history.length})</div>
                    <div className="cli-history-list">
                        {history.slice().reverse().map(cmd => (
                            <div key={cmd.id} className="cli-history-item" onClick={() => setInput(cmd.input)}>
                                <span className={`cli-history-dot ${cmd.status}`} />
                                <span className="cli-history-cmd">{cmd.input}</span>
                                <span className="cli-history-time">{cmd.timestamp}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* ─── Terminal Output ─── */}
                <div className="cli-terminal">
                    <div className="cli-output" ref={outputRef}>
                        <div className="cli-welcome">
                            <span style={{ color: '#4ecdc4' }}>AIM-OS CLI Terminal v1.0</span><br />
                            <span style={{ color: '#888' }}>Connected to Gemini CLI, Ollama, and system shell.</span><br />
                            <span style={{ color: '#888' }}>Type a command or use Quick Commands →</span><br />
                            <br />
                        </div>
                        {history.map(cmd => (
                            <div key={cmd.id} className="cli-entry">
                                <div className="cli-prompt-line">
                                    <span className="cli-prompt-user" style={{ color: providerColor[cmd.provider || 'system'] }}>
                                        {cmd.provider || 'system'}
                                    </span>
                                    <span className="cli-prompt-arrow">❯</span>
                                    <span className="cli-prompt-cmd">{cmd.input}</span>
                                    {cmd.duration && <span className="cli-prompt-duration">{cmd.duration}</span>}
                                </div>
                                {cmd.output && (
                                    <pre className="cli-output-text">{cmd.output}</pre>
                                )}
                            </div>
                        ))}
                        {isRunning && (
                            <div className="cli-running">
                                <span className="cli-spinner">⠋</span> Running...
                            </div>
                        )}
                    </div>

                    {/* ─── Input ─── */}
                    <div className="cli-input-bar">
                        <span className="cli-input-prompt">❯</span>
                        <input
                            ref={inputRef}
                            className="cli-input"
                            placeholder="Enter command..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') executeCommand(); }}
                            disabled={isRunning}
                        />
                        <button className="cli-run-btn" onClick={executeCommand} disabled={isRunning || !input.trim()}>
                            ▶ Run
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
