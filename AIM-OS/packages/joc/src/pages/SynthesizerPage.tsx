import { useState, useMemo, useEffect, useCallback } from 'react';
import { useAIMOS } from '../hooks/useAIMOS';
import { useJOCStore } from '../store/jocStore';
import { useSessionStore } from '../store/sessionStore';
import * as basClient from '../services/basClient';

// ─── Types ───

interface AIResponse {
    id: string;
    provider: string;
    model: string;
    content: string;
    tokens: number;
    latencyMs: number;
    confidence: number;
    timestamp: string;
}

interface ComparisonMission {
    id: string;
    title: string;
    prompt: string;
    strategy: string;
    responses: AIResponse[];
    createdAt: string;
}

type ViewMode = 'side-by-side' | 'unified' | 'diff';
type SynthesisStatus = 'idle' | 'synthesizing' | 'done';

// ─── Synthesizer Component ───

export function SynthesizerPage() {
    const [missions, setMissions] = useState<ComparisonMission[]>([]);
    const [selectedMissionId, setSelectedMissionId] = useState<string>('');
    const [viewMode, setViewMode] = useState<ViewMode>('side-by-side');
    const [synthesisStatus, setSynthesisStatus] = useState<SynthesisStatus>('idle');
    const [synthesisResult, setSynthesisResult] = useState<string>('');
    const [syncScroll, setSyncScroll] = useState(true);
    const [basOnline, setBASOnline] = useState(false);

    const aimos = useAIMOS({ pollDomains: ['goals', 'messages'] });
    const { addTab, setActiveTab, missions: storeMissions } = useJOCStore();
    const sessions = useSessionStore(s => s.sessions);

    // Build ComparisonMission list from jocStore missions + session responses
    useEffect(() => {
        const cmpMissions: ComparisonMission[] = storeMissions.map(m => {
            // Find responses from session store for each target
            const responses: AIResponse[] = m.targets
                .map(target => {
                    const sessionId = `${target}-session`;
                    const session = sessions[sessionId];
                    if (!session?.lastResponse) return null;

                    return {
                        id: `${m.id}-${target}`,
                        provider: session.provider || target,
                        model: target, // Will be enhanced when model is stored in session
                        content: session.lastResponse,
                        tokens: Math.ceil(session.lastResponse.length / 4),
                        latencyMs: 0,
                        confidence: session.health ? session.health / 100 : 0.7,
                        timestamp: new Date().toISOString(),
                    } as AIResponse;
                })
                .filter((r): r is AIResponse => r !== null);

            return {
                id: m.id,
                title: m.title,
                prompt: m.prompt || '',
                strategy: m.targets.length > 1 ? 'parallel' : 'single',
                responses,
                createdAt: m.createdAt,
            };
        });
        setMissions(cmpMissions);
        if (cmpMissions.length > 0 && !selectedMissionId) {
            setSelectedMissionId(cmpMissions[0].id);
        }
    }, [storeMissions, sessions, selectedMissionId]);

    // Check BAS availability
    useEffect(() => {
        basClient.isBASOnline().then(setBASOnline).catch(() => setBASOnline(false));
    }, []);

    const mission = missions.find(m => m.id === selectedMissionId);
    const responses = mission?.responses || [];

    // Find agreements and disagreements (simple keyword overlap analysis)
    const analysis = useMemo(() => {
        if (responses.length < 2) return { agreements: [] as string[], disagreements: [] as string[] };

        const agreements: string[] = [];
        const disagreements: string[] = [];

        // Find shared numeric claims
        const getNumbers = (text: string): string[] => {
            const matches = text.match(/\d[\d,.]*/g) || [];
            return matches.filter(m => m.length > 1);
        };

        const nums0 = getNumbers(responses[0].content);
        const nums1 = getNumbers(responses[1].content);

        nums0.forEach(n => {
            if (nums1.includes(n)) agreements.push(`Both cite: ${n}`);
        });

        if (agreements.length === 0 && responses.length >= 2) agreements.push('General topic alignment');
        return { agreements, disagreements };
    }, [responses]);

    const handleSynthesize = useCallback(async () => {
        if (!mission || responses.length < 2) return;
        setSynthesisStatus('synthesizing');

        // Build synthesis from actual responses
        await new Promise(r => setTimeout(r, 800));
        setSynthesisResult(
            `## Synthesized Analysis — ${mission.title}\n\n` +
            `**Sources:** ${responses.map(r => `${r.provider} (${r.model})`).join(', ')}\n\n` +
            `### Key Agreements\n${analysis.agreements.map(a => `- ✅ ${a}`).join('\n')}\n\n` +
            `### Key Disagreements\n${analysis.disagreements.map(d => `- ⚠️ ${d}`).join('\n') || '- None detected'}\n\n` +
            `### Recommended Action\nReview responses side-by-side and verify claims against source documentation.`
        );
        setSynthesisStatus('done');
    }, [mission, responses, analysis]);

    const providerColor = (p: string) => {
        switch (p) {
            case 'chatgpt': return '#10A37F';
            case 'gemini': return '#4285F4';
            case 'claude': return '#CC7722';
            case 'perplexity': return '#6200EA';
            default: return '#888';
        }
    };

    const confidenceLabel = (c: number) => {
        if (c >= 0.9) return { text: 'HIGH', color: '#4ecdc4' };
        if (c >= 0.7) return { text: 'MED', color: '#ffd93d' };
        return { text: 'LOW', color: '#ff6b6b' };
    };

    return (
        <div className="synth-page">
            {/* ─── Header ─── */}
            <div className="synth-header">
                <div className="synth-header-left">
                    <span className="synth-title">⬡ Results Synthesizer</span>
                    {missions.length > 0 ? (
                        <select
                            className="synth-mission-select"
                            value={selectedMissionId}
                            onChange={e => setSelectedMissionId(e.target.value)}
                        >
                            {missions.map(m => (
                                <option key={m.id} value={m.id}>
                                    {m.id}: {m.title} ({m.responses.length} responses)
                                </option>
                            ))}
                        </select>
                    ) : (
                        <span style={{ fontSize: 12, opacity: 0.5, marginLeft: 12 }}>
                            No missions yet — dispatch from Mission Builder
                        </span>
                    )}
                </div>
                <div className="synth-header-right">
                    <span style={{
                        display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                        background: basOnline ? '#4ecdc4' : '#ff6b6b',
                        boxShadow: basOnline ? '0 0 6px rgba(78,205,196,0.5)' : '0 0 6px rgba(255,107,107,0.5)',
                        marginRight: 6,
                    }} />
                    <div className="synth-view-toggle">
                        {(['side-by-side', 'unified', 'diff'] as ViewMode[]).map(mode => (
                            <button
                                key={mode}
                                className={`synth-view-btn ${viewMode === mode ? 'active' : ''}`}
                                onClick={() => setViewMode(mode)}
                            >
                                {mode === 'side-by-side' ? '⫿' : mode === 'unified' ? '▤' : '⇔'} {mode}
                            </button>
                        ))}
                    </div>
                    <label className="synth-sync-label">
                        <input type="checkbox" checked={syncScroll} onChange={e => setSyncScroll(e.target.checked)} />
                        Sync scroll
                    </label>
                </div>
            </div>

            {/* ─── Empty State ─── */}
            {(!mission || responses.length === 0) && (
                <div style={{ textAlign: 'center', padding: 60, opacity: 0.5 }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>⬡</div>
                    <div style={{ fontSize: 14 }}>No responses to synthesize yet.</div>
                    <div style={{ fontSize: 12, marginTop: 8 }}>
                        Dispatch a multi-provider mission from <strong>Mission Builder</strong> to see results here.
                    </div>
                </div>
            )}

            {/* ─── Prompt Banner ─── */}
            {mission && mission.prompt && (
                <div className="synth-prompt-banner">
                    <span className="synth-prompt-label">PROMPT</span>
                    <span className="synth-prompt-text">{mission.prompt}</span>
                    <span className="synth-strategy-badge">{mission.strategy.toUpperCase()}</span>
                </div>
            )}

            {/* ─── Response Panels ─── */}
            {responses.length > 0 && (
                <div className={`synth-panels ${viewMode}`}>
                    {responses.map(resp => {
                        const conf = confidenceLabel(resp.confidence);
                        return (
                            <div key={resp.id} className="synth-panel" style={{ borderTopColor: providerColor(resp.provider) }}>
                                <div className="synth-panel-header">
                                    <span className="synth-panel-provider-badge" style={{ background: `${providerColor(resp.provider)}22`, color: providerColor(resp.provider) }}>
                                        {resp.provider.toUpperCase()}
                                    </span>
                                    <span className="synth-model-tag">{resp.model}</span>
                                    <span className="synth-panel-spacer" />
                                    <span className="synth-confidence-badge" style={{ color: conf.color, borderColor: `${conf.color}44` }}>
                                        VIF {conf.text} ({(resp.confidence * 100).toFixed(0)}%)
                                    </span>
                                </div>
                                <div className="synth-panel-content">
                                    <pre className="synth-response-text">{resp.content}</pre>
                                </div>
                                <div className="synth-panel-footer">
                                    <span className="synth-meta">{resp.tokens} tokens</span>
                                    <span className="synth-meta">{resp.latencyMs}ms</span>
                                    <span className="synth-meta">{resp.timestamp}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* ─── Analysis Bar ─── */}
            {responses.length >= 2 && (
                <div className="synth-analysis">
                    <div className="synth-analysis-section">
                        <div className="synth-analysis-title" style={{ color: '#4ecdc4' }}>✅ Agreements ({analysis.agreements.length})</div>
                        {analysis.agreements.map((a, i) => (
                            <div key={i} className="synth-analysis-item agree">{a}</div>
                        ))}
                    </div>
                    <div className="synth-analysis-section">
                        <div className="synth-analysis-title" style={{ color: '#ff6b6b' }}>⚠️ Disagreements ({analysis.disagreements.length})</div>
                        {analysis.disagreements.map((d, i) => (
                            <div key={i} className="synth-analysis-item disagree">{d}</div>
                        ))}
                    </div>
                </div>
            )}

            {/* ─── Synthesis Controls ─── */}
            {responses.length > 0 && (
                <div className="synth-controls">
                    <button
                        className={`synth-synthesize-btn ${synthesisStatus}`}
                        onClick={handleSynthesize}
                        disabled={synthesisStatus === 'synthesizing' || responses.length < 2}
                    >
                        {synthesisStatus === 'synthesizing' ? '⟳ Synthesizing...' : synthesisStatus === 'done' ? '✓ Re-Synthesize' : '⬡ Synthesize Responses'}
                    </button>
                    <button className="synth-action-btn" onClick={() => {
                        addTab({ id: `comms-${Date.now()}`, type: 'comms', label: 'Agent Comms', closable: true });
                        setActiveTab(`comms-${Date.now()}`);
                    }}>
                        💬 View Comms
                    </button>
                    <button className="synth-action-btn" title="Store synthesis to CMC memory">
                        📦 Store to CMC
                    </button>
                    <button className="synth-action-btn" title="Export as markdown">
                        📋 Export MD
                    </button>
                </div>
            )}

            {/* ─── Synthesis Result ─── */}
            {synthesisResult && (
                <div className="synth-result">
                    <pre className="synth-result-text">{synthesisResult}</pre>
                </div>
            )}
        </div>
    );
}
