import { useState, useEffect, useCallback, useMemo } from 'react';
import { useJOCStore, type AISession } from '../store/jocStore';
import { useSessionStore } from '../store/sessionStore';
import { usePageOracle, type OraclePageAction } from '../hooks/usePageOracle';
import {
    checkBASHealth,
    getProviders,
    getAccounts,
    sendPrompt,
    fullSession,
    getMetrics,
    type BASAccount,
    type ProviderInfo,
    type AutomationMetrics,
    type SendPromptResponse,
    type FullSessionResponse,
} from '../services/basClient';
import {
    DispatchIcon, CrosshairIcon, ParallelLinesIcon, ChainLinkIcon,
    MergePathsIcon, CrossedSwordsIcon, AutomationIcon,
} from '../components/icons';
import { CaptureInspector } from '../components/dispatch/CaptureInspector';
import '../styles/dispatch.css';

// ─── Types ───

type DispatchStrategy = 'single' | 'parallel' | 'sequential' | 'consensus' | 'debate';

interface DispatchTarget {
    id: string;
    session: AISession;
    selected: boolean;
    ring: 1 | 2 | 3;
    account?: BASAccount;
    browserId?: string;
}

interface DispatchResult {
    provider: string;
    targetName: string;
    status: 'pending' | 'running' | 'success' | 'error';
    response?: string;
    duration?: number;
    error?: string;
}

// ─── Strategy Cards ───

const STRATEGIES: { id: DispatchStrategy; label: string; Icon: React.ComponentType<{ size?: number }>; desc: string }[] = [
    { id: 'single', label: 'Single', Icon: CrosshairIcon, desc: 'Send to one AI' },
    { id: 'parallel', label: 'Parallel', Icon: ParallelLinesIcon, desc: 'All AIs simultaneously' },
    { id: 'sequential', label: 'Sequential', Icon: ChainLinkIcon, desc: 'Chain responses' },
    { id: 'consensus', label: 'Consensus', Icon: MergePathsIcon, desc: 'Merge agreements' },
    { id: 'debate', label: 'Debate', Icon: CrossedSwordsIcon, desc: 'Opposing arguments' },
];

// ─── Component ───

export function DispatchPage() {
    const { sessions, missions } = useJOCStore();
    const runtimeSessions = useSessionStore(state => state.sessions);
    const [prompt, setPrompt] = useState('');
    const [strategy, setStrategy] = useState<DispatchStrategy>('single');
    const [selectedTargets, setSelectedTargets] = useState<Set<string>>(new Set());
    const [context, setContext] = useState('');
    const [isDispatching, setIsDispatching] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);

    // Context Capsule state (stub — will be populated by Context Mapper)
    interface ContextCapsule {
        id: string;
        type: 'envelope' | 'knowledge' | 'file' | 'auto';
        label: string;
        source?: string;   // origin system (CMC, HHNI, filesystem, etc.)
        tokens?: number;
    }
    const [contextCapsules, setContextCapsules] = useState<ContextCapsule[]>([]);

    const addCapsule = (capsule: ContextCapsule) => {
        setContextCapsules(prev => [...prev, capsule]);
    };
    const removeCapsule = (id: string) => {
        setContextCapsules(prev => prev.filter(c => c.id !== id));
    };

    // ─── BAS Live State ───
    const [basConnected, setBASConnected] = useState(false);
    const [basProviders, setBASProviders] = useState<ProviderInfo[]>([]);
    const [basAccounts, setBASAccounts] = useState<BASAccount[]>([]);
    const [basMetrics, setBASMetrics] = useState<AutomationMetrics | null>(null);
    const [results, setResults] = useState<DispatchResult[]>([]);
    const [showResults, setShowResults] = useState(false);

    // ─── Oracle API Registration ───
    const oracleActions: OraclePageAction[] = useMemo(() => [
        {
            id: 'dispatch.send',
            label: 'Send Dispatch',
            system: 'dispatch' as const,
            description: 'Send a prompt to selected AI providers',
            minPermission: 'supervised' as const,
            params: [
                { name: 'prompt', type: 'string' as const, required: true, description: 'The prompt to send' },
                { name: 'strategy', type: 'select' as const, required: false, description: 'Dispatch strategy', options: ['single', 'parallel', 'sequential', 'consensus', 'debate'] },
            ],
            execute: async (params) => {
                if (params.prompt) setPrompt(params.prompt as string);
                if (params.strategy) setStrategy(params.strategy as DispatchStrategy);
                return { success: true, message: 'Dispatch parameters set — ready to send' };
            },
        },
        {
            id: 'dispatch.setStrategy',
            label: 'Set Strategy',
            system: 'dispatch' as const,
            description: 'Change the dispatch strategy',
            minPermission: 'supervised' as const,
            params: [
                { name: 'strategy', type: 'select' as const, required: true, description: 'Strategy type', options: ['single', 'parallel', 'sequential', 'consensus', 'debate'] },
            ],
            execute: async (params) => {
                setStrategy(params.strategy as DispatchStrategy);
                return { success: true, message: `Strategy changed to ${params.strategy}` };
            },
        },
    ], []);

    const { emitEvent } = usePageOracle('dispatch', {
        actions: oracleActions,
        getState: () => ({
            prompt,
            strategy,
            selectedTargets: [...selectedTargets],
            basConnected,
            isDispatching,
        }),
    });

    // Check BAS health + load accounts/providers on mount & every 30s
    const loadBASState = useCallback(async () => {
        try {
            await checkBASHealth();
            setBASConnected(true);
            const [providers, accounts, metrics] = await Promise.all([
                getProviders().catch(() => []),
                getAccounts().catch(() => []),
                getMetrics().catch(() => null),
            ]);
            setBASProviders(providers);
            setBASAccounts(accounts);
            setBASMetrics(metrics);
        } catch {
            setBASConnected(false);
        }
    }, []);

    useEffect(() => {
        loadBASState();
        const interval = setInterval(loadBASState, 30000);
        return () => clearInterval(interval);
    }, [loadBASState]);

    const providerToRing = (provider: AISession['provider']): 1 | 2 | 3 =>
        provider === 'chatgpt' || provider === 'gemini' || provider === 'claude' || provider === 'perplexity'
            ? 1
            : provider === 'gemini-cli' || provider === 'local'
                ? 2
                : 3;

    const normalizeRuntimeStatus = (status: string): AISession['status'] => {
        if (status === 'connected' || status === 'connecting' || status === 'injecting' || status === 'extracting') {
            return 'active';
        }
        if (status === 'error') {
            return 'dead';
        }
        return 'sleeping';
    };

    // Prefer live sessionStore entries so Dispatch reuses BAS browser IDs launched in Session page.
    const dispatchBaseTargets = useMemo((): DispatchTarget[] => {
        const targetByProvider = new Map<AISession['provider'], DispatchTarget>();

        Object.entries(runtimeSessions).forEach(([runtimeSessionId, runtimeSession]) => {
            const fleetSession = sessions.find(session => session.provider === runtimeSession.provider);
            targetByProvider.set(runtimeSession.provider, {
                id: runtimeSessionId,
                session: {
                    id: runtimeSessionId,
                    name: fleetSession?.name || `${runtimeSession.provider.toUpperCase()} Session`,
                    provider: runtimeSession.provider,
                    status: normalizeRuntimeStatus(runtimeSession.status),
                    health: runtimeSession.health,
                    uptime: runtimeSession.uptime,
                    lastActivity: fleetSession?.lastActivity || (runtimeSession.lastResponse ? 'Response captured' : 'Ready'),
                },
                selected: false,
                ring: providerToRing(runtimeSession.provider),
                account: basAccounts.find(account => account.provider === runtimeSession.provider),
                browserId: runtimeSession.browserId,
            });
        });

        sessions.forEach((session) => {
            if (!targetByProvider.has(session.provider)) {
                targetByProvider.set(session.provider, {
                    id: session.id,
                    session,
                    selected: false,
                    ring: providerToRing(session.provider),
                    account: basAccounts.find(account => account.provider === session.provider),
                });
            }
        });

        return Array.from(targetByProvider.values());
    }, [runtimeSessions, sessions, basAccounts]);

    const targets = useMemo(
        () => dispatchBaseTargets.map(target => ({ ...target, selected: selectedTargets.has(target.id) })),
        [dispatchBaseTargets, selectedTargets],
    );

    useEffect(() => {
        setSelectedTargets(prev => {
            const validTargetIds = new Set(dispatchBaseTargets.map(target => target.id));
            const kept = [...prev].filter(id => validTargetIds.has(id));
            if (kept.length === 0 && dispatchBaseTargets.length > 0) {
                return new Set([dispatchBaseTargets[0].id]);
            }
            if (kept.length === prev.size) {
                return prev;
            }
            return new Set(kept);
        });
    }, [dispatchBaseTargets]);

    const toggleTarget = (id: string) => {
        setSelectedTargets(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id); else next.add(id);
            return next;
        });
    };

    const selectedCount = targets.filter(target => target.selected).length;

    const dispatchToTarget = async (
        target: DispatchTarget,
        message: string,
        timeout?: number,
    ): Promise<SendPromptResponse | FullSessionResponse> => {
        if (target.browserId) {
            return sendPrompt({
                browserId: target.browserId,
                prompt: message,
                provider: target.session.provider,
                waitForResponse: true,
                responseTimeout: timeout,
            });
        }
        if (target.account) {
            return fullSession({
                accountId: target.account.id,
                prompt: message,
                headless: false,
            });
        }
        throw new Error(`No BAS browser launched for ${target.session.name}. Launch it from Session page first.`);
    };

    // ─── LIVE DISPATCH via BAS ───
    const handleDispatch = async () => {
        const selected = targets.filter(t => t.selected);
        if (!prompt.trim() || selected.length === 0) return;
        setIsDispatching(true);
        setShowResults(true);
        const fullPrompt = context ? `${context}\n\n${prompt}` : prompt;

        // Initialize results
        const initialResults: DispatchResult[] = selected.map(t => ({
            provider: t.session.provider,
            targetName: t.session.name,
            status: 'pending',
        }));
        setResults(initialResults);

        if (basConnected) {
            // ─── REAL BAS DISPATCH ───
            if (strategy === 'parallel' || strategy === 'consensus' || strategy === 'debate') {
                const promises = selected.map(async (t, i) => {
                    setResults(prev => prev.map((r, j) => j === i ? { ...r, status: 'running' } : r));
                    try {
                        const result = await dispatchToTarget(t, fullPrompt, 60000);
                        setResults(prev => prev.map((r, j) => j === i ? {
                            ...r,
                            status: result.success ? 'success' : 'error',
                            response: result.response,
                            duration: result.duration,
                            error: result.error,
                        } : r));
                    } catch (err: any) {
                        setResults(prev => prev.map((r, j) => j === i ? {
                            ...r,
                            status: 'error',
                            error: err.message || 'Dispatch failed',
                        } : r));
                    }
                });
                await Promise.allSettled(promises);
            } else if (strategy === 'sequential') {
                let chainContext = context;
                for (let i = 0; i < selected.length; i++) {
                    const t = selected[i];
                    setResults(prev => prev.map((r, j) => j === i ? { ...r, status: 'running' } : r));
                    try {
                        const fullPrompt = chainContext
                            ? `Previous AI response:\n${chainContext}\n\nNow continue with:\n${prompt}`
                            : prompt;
                        const result = await dispatchToTarget(t, fullPrompt, 60000);
                        if (result.success && result.response) {
                            chainContext = result.response;
                        }
                        setResults(prev => prev.map((r, j) => j === i ? {
                            ...r, status: result.success ? 'success' : 'error',
                            response: result.response, duration: result.duration, error: result.error,
                        } : r));
                    } catch (err: any) {
                        setResults(prev => prev.map((r, j) => j === i ? {
                            ...r, status: 'error', error: err.message || 'Dispatch failed',
                        } : r));
                    }
                }
            } else {
                // Single — first selected target
                const t = selected[0];
                setResults(prev => prev.map((r, j) => j === 0 ? { ...r, status: 'running' } : r));
                try {
                    const result = await dispatchToTarget(t, fullPrompt, 60000);
                    setResults(prev => prev.map((r, j) => j === 0 ? {
                        ...r, status: result.success ? 'success' : 'error',
                        response: result.response, duration: result.duration, error: result.error,
                    } : r));
                } catch (err: any) {
                    setResults(prev => prev.map((r, j) => j === 0 ? {
                        ...r, status: 'error', error: err.message || 'Dispatch failed',
                    } : r));
                }
            }
        } else {
            // ─── OFFLINE FALLBACK ───
            console.log('[JOC] BAS offline — simulating dispatch:', { prompt, strategy, targets: [...selectedTargets], context });
            for (let i = 0; i < initialResults.length; i++) {
                await new Promise(r => setTimeout(r, 500));
                setResults(prev => prev.map((r, j) => j === i ? {
                    ...r, status: 'error',
                    error: 'BAS offline — start the Browser Automation Service on port 5002',
                } : r));
            }
        }

        setIsDispatching(false);
        loadBASState(); // Refresh metrics
    };

    const charCount = prompt.length;
    const estimatedTokens = Math.ceil(charCount / 4);

    return (
        <div className="dispatch-page">
            {/* ─── Header ─── */}
            <div className="dispatch-header">
                <h2 className="dispatch-title">
                    <DispatchIcon size={16} />
                    Mission Dispatch
                </h2>
                <div className="dispatch-meta">
                    <span className="dispatch-meta-item">{selectedCount} target{selectedCount !== 1 ? 's' : ''}</span>
                    <span className="dispatch-meta-sep">·</span>
                    <span className="dispatch-meta-item">~{estimatedTokens} tokens</span>
                    <span className="dispatch-meta-sep">·</span>
                    <span className="dispatch-meta-item">{strategy} strategy</span>
                    <span className="dispatch-meta-sep">·</span>
                    <span className={`dispatch-bas-badge ${basConnected ? 'online' : 'offline'}`}>
                        <span className={`dispatch-bas-dot ${basConnected ? 'online' : 'offline'}`} />
                        BAS: {basConnected ? '✓' : '✗'}
                    </span>
                    {basMetrics && (
                        <>
                            <span className="dispatch-meta-sep">·</span>
                            <span className="dispatch-meta-item" style={{ color: 'var(--dsp-led-green)' }}>
                                {basMetrics.totalExecutions} runs ({Math.round(basMetrics.successRate * 100)}%)
                            </span>
                        </>
                    )}
                </div>
            </div>

            <div className="dispatch-layout">
                {/* ─── Left: Prompt Composer ─── */}
                <div className="dispatch-composer">
                    {/* Strategy Picker */}
                    <div className="dispatch-section">
                        <label className="dispatch-section-label">Strategy</label>
                        <div className="dispatch-strategy-grid">
                            {STRATEGIES.map(s => (
                                <button
                                    key={s.id}
                                    className={`dispatch-strategy-btn ${strategy === s.id ? 'active' : ''}`}
                                    onClick={() => setStrategy(s.id)}
                                >
                                    <span className="dispatch-strategy-icon"><s.Icon size={16} /></span>
                                    <span className="dispatch-strategy-label">{s.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Prompt Input */}
                    <div className="dispatch-section">
                        <label className="dispatch-section-label">Prompt</label>
                        <textarea
                            className="dispatch-textarea"
                            placeholder="Enter your prompt... (Ctrl+Enter to dispatch)"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.ctrlKey && e.key === 'Enter') handleDispatch();
                            }}
                            rows={8}
                        />
                        <div className="dispatch-textarea-footer">
                            <span>{charCount} chars · ~{estimatedTokens} tokens</span>
                        </div>
                    </div>

                    {/* Context */}
                    <button
                        className="dispatch-toggle-btn"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                    >
                        {showAdvanced ? '▼' : '▶'} Context & Attachments
                    </button>

                    {showAdvanced && (
                        <div className="dispatch-section">
                            <label className="dispatch-section-label">System Context</label>
                            <textarea
                                className="dispatch-textarea small"
                                placeholder="Optional system prompt or context..."
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                                rows={3}
                            />

                            {/* Context Capsule Pills */}
                            {contextCapsules.length > 0 && (
                                <div className="dispatch-capsule-list">
                                    {contextCapsules.map(cap => (
                                        <span key={cap.id} className="dispatch-capsule">
                                            <span>{cap.type.toUpperCase()}</span>
                                            <span>{cap.label}</span>
                                            {cap.tokens && <span style={{ opacity: 0.5 }}>~{cap.tokens}t</span>}
                                            <button
                                                className="dispatch-capsule-close"
                                                onClick={() => removeCapsule(cap.id)}
                                            >×</button>
                                        </span>
                                    ))}
                                    <span style={{ fontSize: '8px', color: 'var(--dsp-text-mute)', alignSelf: 'center', fontFamily: 'var(--font-mono)' }}>
                                        {contextCapsules.reduce((s, c) => s + (c.tokens || 0), 0)} total tokens
                                    </span>
                                </div>
                            )}

                            <div className="dispatch-attach-row">
                                <button className="dispatch-attach-btn" onClick={() => {
                                    addCapsule({
                                        id: `cap-${Date.now()}-file`,
                                        type: 'file',
                                        label: 'waterSim.wgsl',
                                        source: 'filesystem',
                                        tokens: 1200,
                                    });
                                }}>ATTACH FILE</button>
                                <button className="dispatch-attach-btn" onClick={() => {
                                    addCapsule({
                                        id: `cap-${Date.now()}-env`,
                                        type: 'envelope',
                                        label: 'Active Context Envelope',
                                        source: 'CMC',
                                        tokens: 3400,
                                    });
                                }}>ADD ENVELOPE</button>
                                <button className="dispatch-attach-btn" onClick={() => {
                                    addCapsule({
                                        id: `cap-${Date.now()}-auto`,
                                        type: 'auto',
                                        label: 'HHNI Auto-Context',
                                        source: 'HHNI',
                                        tokens: 2100,
                                    });
                                }}>AUTO-CONTEXT</button>
                            </div>
                        </div>
                    )}

                    {/* Dispatch Button */}
                    <button
                        className={`dispatch-send-btn ${isDispatching ? 'dispatching' : ''}`}
                        onClick={handleDispatch}
                        disabled={!prompt.trim() || selectedCount === 0}
                    >
                        {isDispatching ? (
                            <><span className="dispatch-spinner" /> DISPATCHING...</>
                        ) : (
                            <>
                                <DispatchIcon size={14} />
                                DISPATCH MISSION
                            </>
                        )}
                    </button>

                    {/* ─── Results Panel ─── */}
                    {showResults && results.length > 0 && (
                        <div className="dispatch-results">
                            <div className="dispatch-results-header">
                                <label className="dispatch-section-label">Results</label>
                                <button
                                    className="dispatch-results-close"
                                    onClick={() => { setShowResults(false); setResults([]); }}
                                >✕</button>
                            </div>
                            {results.map((r, i) => (
                                <div key={i} className={`dispatch-result-card ${r.status}`}>
                                    <div className="dispatch-result-header">
                                        <span className={`dispatch-result-dot ${r.status}`} />
                                        <span className="dispatch-result-name">{r.targetName}</span>
                                        <span className="dispatch-result-provider">{r.provider}</span>
                                        {r.duration && (
                                            <span className="dispatch-result-time">{(r.duration / 1000).toFixed(1)}s</span>
                                        )}
                                    </div>
                                    {r.status === 'running' && (
                                        <div className="dispatch-result-running">
                                            <span className="dispatch-spinner small" /> Waiting for response...
                                        </div>
                                    )}
                                    {r.response && (
                                        <div className="dispatch-result-response">
                                            {r.response.length > 500 ? r.response.slice(0, 500) + '…' : r.response}
                                        </div>
                                    )}
                                    {r.error && (
                                        <div className="dispatch-result-error">{r.error}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* ─── Right: Target Picker ─── */}
                <div className="dispatch-targets">
                    <label className="dispatch-section-label">Targets</label>

                    {[1, 2, 3].map(ring => {
                        const ringTargets = targets.filter(t => t.ring === ring);
                        if (ringTargets.length === 0) return null;
                        return (
                            <div key={ring} className="dispatch-ring-group">
                                <div className="dispatch-ring-label">
                                    Ring {ring}: {ring === 1 ? 'Browser' : ring === 2 ? 'API / CLI' : 'Cloud'}
                                </div>
                                {ringTargets.map(t => (
                                    <div
                                        key={t.id}
                                        className={`dispatch-target ${t.selected ? 'selected' : ''} ${t.session.status}`}
                                        onClick={() => toggleTarget(t.id)}
                                    >
                                        <div className={`dispatch-target-status ${t.session.status}`} />
                                        <div className="dispatch-target-info">
                                            <span className="dispatch-target-name">{t.session.name}</span>
                                            <span className="dispatch-target-provider">{t.session.provider}</span>
                                            <span className="dispatch-target-provider" style={{ opacity: 0.7 }}>
                                                {t.browserId ? `BAS ${t.browserId.slice(0, 12)}` : 'No live BAS browser'}
                                            </span>
                                        </div>
                                        {/* BAS account indicator */}
                                        {t.account && (
                                            <span className="dispatch-target-bas" title={`BAS: ${t.account.email || t.account.displayName}`}>
                                                <AutomationIcon size={10} />
                                            </span>
                                        )}
                                        <div className="dispatch-target-health">
                                            <div className="dispatch-health-bar">
                                                <div
                                                    className="dispatch-health-fill"
                                                    style={{
                                                        width: `${t.session.health}%`,
                                                        background: t.session.health > 70 ? 'var(--dsp-led-green)' : 'var(--dsp-led-amber)'
                                                    }}
                                                />
                                            </div>
                                            <span>{t.session.health}%</span>
                                        </div>
                                        <input
                                            type="checkbox"
                                            checked={t.selected}
                                            onChange={() => { }}
                                            className="dispatch-target-check"
                                        />
                                    </div>
                                ))}
                            </div>
                        );
                    })}

                    {/* BAS Providers (discovered from BAS) */}
                    {basProviders.length > 0 && (
                        <div className="dispatch-section" style={{ marginTop: 12 }}>
                            <label className="dispatch-section-label">BAS Providers</label>
                            {basProviders.map(p => (
                                <div key={p.name} className="dispatch-provider-card">
                                    <span className="dispatch-provider-name">{p.name}</span>
                                    <span className="dispatch-provider-selectors">
                                        {p.inputSelectors} input · {p.responseSelectors} response
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Recent Missions */}
                    <div className="dispatch-section" style={{ marginTop: 12 }}>
                        <label className="dispatch-section-label">Recent Missions</label>
                        {missions.slice(0, 3).map(m => (
                            <div key={m.id} className="dispatch-recent-mission">
                                <span className={`dispatch-mission-status ${m.status}`} />
                                <span className="dispatch-mission-title">{m.title}</span>
                                <span className="dispatch-mission-time">{m.createdAt}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <CaptureInspector />
        </div>
    );
}
