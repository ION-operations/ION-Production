import { useState, useEffect, useCallback, useRef } from 'react';
import * as basClient from '../services/basClient';
import * as github from '../services/githubContext';
import { useJOCStore } from '../store/jocStore';
import { useSessionStore } from '../store/sessionStore';

// ─── Types ───

interface AgentTarget {
    id: string;
    name: string;
    icon: string;
    available: boolean;
    maxTokens: number;
    selectorCount?: number;
}

type Strategy = 'parallel' | 'sequential' | 'debate' | 'roundrobin';

// Provider icons and known token limits
const PROVIDER_META: Record<string, { icon: string; maxTokens: number }> = {
    chatgpt: { icon: '⚡', maxTokens: 128000 },
    gemini: { icon: '✦', maxTokens: 1000000 },
    claude: { icon: '◈', maxTokens: 200000 },
    perplexity: { icon: '◇', maxTokens: 127000 },
    ollama: { icon: '🖥', maxTokens: 8192 },
    deepseek: { icon: '🔮', maxTokens: 64000 },
};

const STRATEGIES: { id: Strategy; label: string; icon: string; desc: string }[] = [
    { id: 'parallel', label: 'Parallel', icon: '⫿', desc: 'Dispatch to all agents simultaneously' },
    { id: 'sequential', label: 'Sequential', icon: '→', desc: 'Chain output of one into next' },
    { id: 'debate', label: 'Debate', icon: '⚔', desc: 'Agents respond then critique each other' },
    { id: 'roundrobin', label: 'Round Robin', icon: '↺', desc: 'Each agent handles a section' },
];

interface ContextFile {
    name: string;
    tokens: number;
    content: string;
    sizeBytes: number;
}

// ─── Component ───

export function MissionBuilderPage() {
    const [agents, setAgents] = useState<AgentTarget[]>([]);
    const [loading, setLoading] = useState(true);
    const [basOnline, setBASOnline] = useState(false);
    const [missionName, setMissionName] = useState('');
    const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
    const [strategy, setStrategy] = useState<Strategy>('parallel');
    const [prompt, setPrompt] = useState('');
    const [contextFiles, setContextFiles] = useState<ContextFile[]>([]);
    const [autoSynthesize, setAutoSynthesize] = useState(true);
    const [savedTemplates] = useState(['Code Review', 'Architecture Analysis', 'Bug Hunt', 'Docs Generation']);
    const [dispatching, setDispatching] = useState(false);
    const [dispatchResult, setDispatchResult] = useState<string | null>(null);
    const [selectedModel, setSelectedModel] = useState<string>('');
    const [startFreshChat, setStartFreshChat] = useState(true);

    // GitHub state
    const [githubUrl, setGithubUrl] = useState('');
    const [githubTree, setGithubTree] = useState<github.GitHubTreeItem[]>([]);
    const [githubRepo, setGithubRepo] = useState<github.GitHubRepo | null>(null);
    const [githubLoading, setGithubLoading] = useState(false);
    const [githubError, setGithubError] = useState<string | null>(null);
    const [selectedGithubFiles, setSelectedGithubFiles] = useState<Set<string>>(new Set());

    const { addMission, updateMission, addTab, setActiveTab } = useJOCStore();
    const { launchSession, injectPrompt } = useSessionStore();
    const fileInputRef = useRef<HTMLInputElement>(null);

    // ─── File Picker Handler ───
    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files) return;

        const newFiles: ContextFile[] = [];
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            try {
                const content = await new Promise<string>((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result as string);
                    reader.onerror = () => reject(new Error(`Failed to read ${file.name}`));
                    reader.readAsText(file);
                });
                newFiles.push({
                    name: file.name,
                    content,
                    tokens: Math.ceil(content.length / 4),
                    sizeBytes: file.size,
                });
            } catch (err) {
                console.error(`Failed to read file: ${file.name}`, err);
            }
        }
        setContextFiles(prev => [...prev, ...newFiles]);
        // Reset input so the same file can be re-selected
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    // ─── GitHub Repo Fetch ───
    const handleFetchRepo = async () => {
        if (!githubUrl.trim()) return;
        setGithubLoading(true);
        setGithubError(null);
        setGithubTree([]);
        setSelectedGithubFiles(new Set());

        try {
            const repo = github.parseGitHubUrl(githubUrl.trim());
            if (!repo) throw new Error('Invalid GitHub URL. Use: owner/repo or https://github.com/owner/repo');
            setGithubRepo(repo);

            const tree = await github.getRepoTree(repo);
            const codeFiles = github.filterCodeFiles(tree);
            setGithubTree(codeFiles.slice(0, 200)); // Cap at 200 files for UI performance
        } catch (err: any) {
            setGithubError(err.message);
        } finally {
            setGithubLoading(false);
        }
    };

    // ─── Add GitHub Files to Context ───
    const handleAddGithubFiles = async () => {
        if (!githubRepo || selectedGithubFiles.size === 0) return;
        setGithubLoading(true);

        try {
            const context = await github.fetchRepoContext(
                githubRepo,
                Array.from(selectedGithubFiles),
                50000 // 50K token budget
            );

            const newFiles: ContextFile[] = context.files.map(f => ({
                name: `${githubRepo.owner}/${githubRepo.repo}/${f.path}`,
                content: f.content,
                tokens: f.tokens,
                sizeBytes: f.sizeBytes,
            }));

            setContextFiles(prev => [...prev, ...newFiles]);
            setSelectedGithubFiles(new Set());
        } catch (err: any) {
            setGithubError(err.message);
        } finally {
            setGithubLoading(false);
        }
    };

    // ─── Build Full Prompt with Context ───
    const buildFullPrompt = (): string => {
        if (contextFiles.length === 0) return prompt;

        const totalContextTokens = contextFiles.reduce((sum, f) => sum + f.tokens, 0);
        const contextBlock = contextFiles
            .map(f => `--- FILE: ${f.name} (${f.tokens} tokens) ---\n${f.content}`)
            .join('\n\n');

        return `<context files="${contextFiles.length}" tokens="${totalContextTokens}">\n${contextBlock}\n</context>\n\n${prompt}`;
    };

    // Fetch live providers from BAS
    const fetchProviders = useCallback(async () => {
        setLoading(true);
        try {
            const online = await basClient.isBASOnline();
            setBASOnline(online);

            if (online) {
                const providers = await basClient.getProviders();
                const liveAgents: AgentTarget[] = providers.map(p => {
                    const key = p.name.toLowerCase();
                    const meta = PROVIDER_META[key] || { icon: '◆', maxTokens: 4096 };
                    return {
                        id: key,
                        name: p.name,
                        icon: meta.icon,
                        available: true,
                        maxTokens: meta.maxTokens,
                        selectorCount: p.inputSelectors + p.responseSelectors,
                    };
                });
                setAgents(liveAgents);
                // Auto-select first two available
                if (liveAgents.length >= 2) {
                    setSelectedAgents(new Set([liveAgents[0].id, liveAgents[1].id]));
                } else if (liveAgents.length === 1) {
                    setSelectedAgents(new Set([liveAgents[0].id]));
                }
            } else {
                // Fallback: show known providers as offline
                const fallback = Object.entries(PROVIDER_META).map(([id, meta]) => ({
                    id,
                    name: id.charAt(0).toUpperCase() + id.slice(1),
                    icon: meta.icon,
                    available: false,
                    maxTokens: meta.maxTokens,
                }));
                setAgents(fallback);
            }
        } catch {
            setAgents([]);
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        fetchProviders();
    }, [fetchProviders]);

    const toggleAgent = (id: string) => {
        setSelectedAgents(prev => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    };

    const totalTokens = contextFiles.reduce((sum, f) => sum + f.tokens, 0);
    const promptTokens = Math.ceil(prompt.length / 4);
    const totalPayload = totalTokens + promptTokens;

    const strategyColors: Record<Strategy, string> = {
        parallel: '#4ecdc4', sequential: '#a882ff', debate: '#ff6b6b', roundrobin: '#ffd93d',
    };

    // ─── Launch Mission Handler ───
    const handleLaunchMission = async () => {
        if (selectedAgents.size === 0 || !prompt.trim()) return;
        setDispatching(true);
        setDispatchResult(null);

        const targets = Array.from(selectedAgents);
        const missionId = `M-${Date.now().toString(36).toUpperCase()}`;
        const title = missionName.trim() || `Mission ${missionId}`;
        const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });

        // Build the full prompt with context files prepended
        const fullPrompt = buildFullPrompt();

        // Track mission in jocStore
        addMission({
            id: missionId,
            title,
            status: 'dispatched',
            progress: 0,
            targets,
            prompt: fullPrompt,
            createdAt: now,
        });

        let successCount = 0;
        let errorCount = 0;

        // ─── Parallel Dispatch to all providers ───
        updateMission(missionId, { status: 'running', progress: 10 });

        const dispatchPromises = targets.map(async (providerId, i) => {
            const sessionId = `${providerId}-session`;

            try {
                // Launch browser session via sessionStore (BAS pipeline)
                await launchSession(sessionId);

                // Select model if specified
                if (selectedModel) {
                    const sessionState = useSessionStore.getState().sessions[sessionId];
                    if (sessionState?.browserId) {
                        try {
                            await basClient.selectModel(sessionState.browserId, providerId, selectedModel);
                        } catch {
                            console.warn(`[Mission] Could not select model ${selectedModel} for ${providerId}`);
                        }
                    }
                }

                // Inject prompt with context
                if (prompt.trim()) {
                    await injectPrompt(sessionId, fullPrompt);
                }

                successCount++;
            } catch (err: any) {
                errorCount++;
                console.error(`[Mission ${missionId}] Failed for ${providerId}:`, err.message);
            }

            // Update progress per-provider
            updateMission(missionId, {
                progress: Math.round(((successCount + errorCount) / targets.length) * 100),
            });
        });

        // Wait for ALL providers to complete (parallel)
        await Promise.allSettled(dispatchPromises);

        // Finalize mission status
        updateMission(missionId, {
            status: errorCount === targets.length ? 'failed' : 'complete',
            progress: 100,
        });

        setDispatching(false);
        setDispatchResult(
            errorCount === 0
                ? `✅ Mission ${missionId} complete — ${successCount} providers launched in parallel`
                : `⚠️ Mission ${missionId} — ${successCount} succeeded, ${errorCount} failed`
        );

        // Open session tabs for all targets (not just the first)
        targets.forEach((providerId, i) => {
            const tabId = `session-${providerId}`;
            addTab({
                id: tabId,
                type: 'session',
                label: `${providerId.charAt(0).toUpperCase() + providerId.slice(1)} Session`,
                closable: true,
                data: { sessionId: `${providerId}-session` },
            });
            if (i === 0) setActiveTab(tabId); // Focus the first
        });
    };

    return (
        <div className="mb-page">
            {/* ─── Header ─── */}
            <div className="mb-header">
                <div className="mb-header-left">
                    <span className="mb-title">🎯 Mission Builder</span>
                    <input className="mb-name-input" placeholder="Mission name..." value={missionName}
                        onChange={e => setMissionName(e.target.value)} />
                </div>
                <div className="mb-header-right">
                    <span style={{
                        display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                        background: basOnline ? '#4ecdc4' : '#ff6b6b',
                        boxShadow: basOnline ? '0 0 6px rgba(78,205,196,0.5)' : '0 0 6px rgba(255,107,107,0.5)',
                        marginRight: 6,
                    }} />
                    <span style={{ fontSize: 11, opacity: 0.6, marginRight: 12 }}>
                        {basOnline ? 'BAS online' : 'BAS offline'}
                    </span>
                    <select className="mb-template-select" defaultValue="">
                        <option value="" disabled>Load template...</option>
                        {savedTemplates.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                    <button className="mb-save-btn">💾 Save Template</button>
                    <button
                        className="mb-launch-btn"
                        disabled={selectedAgents.size === 0 || !prompt.trim() || dispatching}
                        onClick={handleLaunchMission}
                    >
                        {dispatching ? '⟳ Dispatching...' : '🚀 Launch Mission'}
                    </button>
                </div>
            </div>

            {/* ─── Dispatch Result Banner ─── */}
            {dispatchResult && (
                <div style={{
                    padding: '8px 16px',
                    fontSize: 12,
                    background: dispatchResult.startsWith('✅') ? 'rgba(78,205,196,0.1)' : 'rgba(255,107,107,0.1)',
                    borderBottom: `1px solid ${dispatchResult.startsWith('✅') ? '#4ecdc4' : '#ff6b6b'}`,
                    color: dispatchResult.startsWith('✅') ? '#4ecdc4' : '#ff6b6b',
                }}>
                    {dispatchResult}
                </div>
            )}

            <div className="mb-body">
                {/* ─── Left: Builder ─── */}
                <div className="mb-builder">
                    {/* Agent Selection */}
                    <div className="mb-section">
                        <div className="mb-section-title">
                            Target Agents ({selectedAgents.size})
                            {loading && <span style={{ fontSize: 10, opacity: 0.5, marginLeft: 8 }}>loading...</span>}
                        </div>
                        <div className="mb-agent-grid">
                            {agents.map(agent => {
                                const isSelected = selectedAgents.has(agent.id);
                                return (
                                    <button key={agent.id}
                                        className={`mb-agent-card ${isSelected ? 'selected' : ''} ${!agent.available ? 'offline' : ''}`}
                                        onClick={() => agent.available && toggleAgent(agent.id)}
                                        disabled={!agent.available}>
                                        <span className="mb-agent-icon">{agent.icon}</span>
                                        <span className="mb-agent-name">{agent.name}</span>
                                        <span className="mb-agent-status">{agent.available ? '● online' : '○ offline'}</span>
                                        {agent.selectorCount !== undefined && (
                                            <span style={{ fontSize: 9, opacity: 0.4 }}>{agent.selectorCount} selectors</span>
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Strategy */}
                    <div className="mb-section">
                        <div className="mb-section-title">Dispatch Strategy</div>
                        <div className="mb-strategy-grid">
                            {STRATEGIES.map(s => (
                                <button key={s.id}
                                    className={`mb-strategy-card ${strategy === s.id ? 'selected' : ''}`}
                                    onClick={() => setStrategy(s.id)}
                                    style={strategy === s.id ? { borderColor: strategyColors[s.id] } : {}}>
                                    <span className="mb-strategy-icon" style={strategy === s.id ? { color: strategyColors[s.id] } : {}}>
                                        {s.icon}
                                    </span>
                                    <span className="mb-strategy-label">{s.label}</span>
                                    <span className="mb-strategy-desc">{s.desc}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Prompt */}
                    <div className="mb-section">
                        <div className="mb-section-title">
                            Prompt
                            <span className="mb-token-badge">{promptTokens} tokens</span>
                        </div>
                        <textarea className="mb-prompt-area" rows={6} placeholder="Enter your mission prompt..."
                            value={prompt} onChange={e => setPrompt(e.target.value)} />
                    </div>
                </div>

                {/* ─── Right: Context + Pipeline ─── */}
                <div className="mb-sidebar">
                    {/* Context Files */}
                    <div className="mb-section">
                        <div className="mb-section-title">Context Files ({contextFiles.length})</div>
                        <div className="mb-context-list">
                            {contextFiles.map((f, i) => (
                                <div key={i} className="mb-context-item">
                                    <span className="mb-context-name">{f.name}</span>
                                    <span className="mb-context-tokens">
                                        {f.tokens} tok · {(f.sizeBytes / 1024).toFixed(1)}KB
                                    </span>
                                    <button className="mb-context-remove"
                                        onClick={() => setContextFiles(prev => prev.filter((_, j) => j !== i))}>✕</button>
                                </div>
                            ))}
                        </div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept=".ts,.tsx,.js,.jsx,.py,.md,.txt,.json,.css,.html,.rs,.go,.java,.c,.cpp,.h,.yml,.yaml,.toml,.cfg,.env,.sh"
                            style={{ display: 'none' }}
                            onChange={handleFileSelect}
                        />
                        <button className="mb-add-context-btn" onClick={() => fileInputRef.current?.click()}>
                            + Attach Files
                        </button>
                    </div>

                    {/* GitHub Context */}
                    <div className="mb-section">
                        <div className="mb-section-title">⛓ GitHub Context</div>
                        <div style={{ display: 'flex', gap: 4 }}>
                            <input
                                type="text"
                                placeholder="owner/repo or GitHub URL"
                                value={githubUrl}
                                onChange={e => setGithubUrl(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleFetchRepo()}
                                style={{
                                    flex: 1,
                                    padding: '5px 8px',
                                    fontSize: 11,
                                    background: 'var(--bg-input)',
                                    border: '1px solid var(--border)',
                                    borderRadius: 'var(--radius-sm)',
                                    color: 'var(--text-primary)',
                                }}
                            />
                            <button
                                className="mb-add-context-btn"
                                onClick={handleFetchRepo}
                                disabled={githubLoading || !githubUrl.trim()}
                                style={{ whiteSpace: 'nowrap', fontSize: 11 }}
                            >
                                {githubLoading ? '⏳' : '🔍 Fetch'}
                            </button>
                        </div>
                        {githubError && (
                            <div style={{ color: 'var(--status-error)', fontSize: 10, marginTop: 4 }}>{githubError}</div>
                        )}
                        {githubTree.length > 0 && (
                            <>
                                <div style={{ fontSize: 10, color: 'var(--text-secondary)', margin: '6px 0 4px' }}>
                                    {githubRepo?.owner}/{githubRepo?.repo} · {githubTree.length} code files
                                </div>
                                <div style={{
                                    maxHeight: 140,
                                    overflowY: 'auto',
                                    border: '1px solid var(--border)',
                                    borderRadius: 'var(--radius-sm)',
                                    fontSize: 10,
                                }}>
                                    {githubTree.map(file => (
                                        <label
                                            key={file.path}
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: 4,
                                                padding: '2px 6px',
                                                cursor: 'pointer',
                                                borderBottom: '1px solid var(--border)',
                                            }}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedGithubFiles.has(file.path)}
                                                onChange={e => {
                                                    const next = new Set(selectedGithubFiles);
                                                    e.target.checked ? next.add(file.path) : next.delete(file.path);
                                                    setSelectedGithubFiles(next);
                                                }}
                                            />
                                            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {file.path}
                                            </span>
                                            <span style={{ color: 'var(--text-tertiary)', flexShrink: 0 }}>
                                                {(file.size / 1024).toFixed(1)}KB
                                            </span>
                                        </label>
                                    ))}
                                </div>
                                {selectedGithubFiles.size > 0 && (
                                    <button
                                        className="mb-add-context-btn"
                                        onClick={handleAddGithubFiles}
                                        disabled={githubLoading}
                                        style={{ marginTop: 4 }}
                                    >
                                        {githubLoading ? '⏳ Fetching...' : `+ Add ${selectedGithubFiles.size} files to context`}
                                    </button>
                                )}
                            </>
                        )}
                    </div>

                    {/* Pipeline Preview */}
                    <div className="mb-section">
                        <div className="mb-section-title">Pipeline Preview</div>
                        <div className="mb-pipeline">
                            <div className="mb-pipeline-node start">📎 Context</div>
                            <div className="mb-pipeline-arrow">↓ {totalPayload} tokens</div>
                            <div className="mb-pipeline-node" style={{ borderColor: strategyColors[strategy] }}>
                                {STRATEGIES.find(s => s.id === strategy)?.icon} {strategy}
                            </div>
                            <div className="mb-pipeline-arrow">↓</div>
                            {Array.from(selectedAgents).map(id => {
                                const agent = agents.find(a => a.id === id);
                                return (
                                    <div key={id} className="mb-pipeline-node agent">
                                        {agent?.icon} {agent?.name}
                                    </div>
                                );
                            })}
                            <div className="mb-pipeline-arrow">↓</div>
                            <div className="mb-pipeline-node end">
                                {autoSynthesize ? '⬡ Synthesize' : '📦 Collect'}
                            </div>
                        </div>
                    </div>

                    {/* Options */}
                    <div className="mb-section">
                        <div className="mb-section-title">Options</div>
                        <label className="mb-option">
                            <input type="checkbox" checked={autoSynthesize}
                                onChange={e => setAutoSynthesize(e.target.checked)} />
                            Auto-synthesize results
                        </label>
                        <label className="mb-option">
                            <input type="checkbox" checked={startFreshChat}
                                onChange={e => setStartFreshChat(e.target.checked)} />
                            Start fresh conversation
                        </label>
                    </div>

                    {/* Model Selection */}
                    <div className="mb-section">
                        <div className="mb-section-title">Model</div>
                        <select
                            className="mb-model-select"
                            value={selectedModel}
                            onChange={e => setSelectedModel(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '6px 10px',
                                fontSize: 12,
                                background: 'var(--bg-input)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-sm)',
                                color: 'var(--text-primary)',
                            }}
                        >
                            <option value="">Auto (provider default)</option>
                            <optgroup label="ChatGPT">
                                <option value="gpt-4o">GPT-4o</option>
                                <option value="gpt-4o-mini">GPT-4o Mini</option>
                                <option value="o3-mini">o3-mini</option>
                                <option value="o3">o3</option>
                                <option value="gpt-4.1">GPT-4.1</option>
                            </optgroup>
                            <optgroup label="Gemini">
                                <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                            </optgroup>
                            <optgroup label="Claude">
                                <option value="claude-4-sonnet">Claude 4 Sonnet</option>
                                <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                                <option value="claude-3.5-haiku">Claude 3.5 Haiku</option>
                            </optgroup>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
}
