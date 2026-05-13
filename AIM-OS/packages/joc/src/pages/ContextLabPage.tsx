import { useState } from 'react';
import { useContextLab } from '../hooks/useContextLab';

// ─── Helpers ───

const medal = (rank: number) => ['🥇', '🥈', '🥉'][rank - 1] || `#${rank}`;
const genTag = (g: number) => g > 0 ? `G${g}` : 'Base';
const pct = (v: number) => `${(v * 100).toFixed(1)}%`;
const timeAgo = (ts: number) => {
    const mins = Math.floor((Date.now() - ts) / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
};

// ─── Component ───

export function ContextLabPage() {
    const {
        leaderboard, strategies, history,
        loading, mcpConnected, lastError, lastResult, tournamentRunning,
        refresh, forkVariant, runTournament,
    } = useContextLab();

    const [tab, setTab] = useState<'leaderboard' | 'strategies' | 'evolution' | 'history'>('leaderboard');
    const [forkParent, setForkParent] = useState('');
    const [forkChild, setForkChild] = useState('');
    const [forkMutations, setForkMutations] = useState('');
    const [tournamentTask, setTournamentTask] = useState('');

    // Stats
    const bestQuality = leaderboard.length > 0 ? leaderboard[0].avg_quality : 0;
    const totalRuns = leaderboard.reduce((s, e) => s + e.runs, 0);
    const totalVariants = leaderboard.length;
    const avgTime = leaderboard.length > 0
        ? leaderboard.reduce((s, e) => s + e.avg_time_ms, 0) / leaderboard.length
        : 0;

    const handleFork = async () => {
        const mutations: Record<string, string> = {};
        if (forkMutations.trim()) {
            forkMutations.split(',').forEach(pair => {
                const [k, v] = pair.split('=');
                if (k && v) mutations[k.trim()] = v.trim();
            });
        }
        await forkVariant(forkParent, forkChild, mutations);
        setForkChild('');
        setForkMutations('');
    };

    return (
        <div className="clab-page">
            {/* ─── Header ─── */}
            <div className="clab-header">
                <div className="clab-title-area">
                    <span className="clab-title">🧬 Context Lab</span>
                    <span className="clab-subtitle">
                        Strategy Evolution &amp; Tournament R&amp;D
                        {mcpConnected && <span style={{ color: '#4ecdc4', marginLeft: 8 }}>● MCP Live</span>}
                        {!mcpConnected && <span style={{ color: '#8b949e', marginLeft: 8 }}>○ Mock Data</span>}
                        {loading && <span style={{ color: '#58a6ff', marginLeft: 8 }}>⟳</span>}
                    </span>
                </div>
                <div className="clab-header-stats">
                    <div className="clab-stat">
                        <span className="clab-stat-value">{totalVariants}</span>
                        <span className="clab-stat-label">Variants</span>
                    </div>
                    <div className="clab-stat">
                        <span className="clab-stat-value">{totalRuns}</span>
                        <span className="clab-stat-label">Runs</span>
                    </div>
                    <div className="clab-stat">
                        <span className="clab-stat-value" style={{ color: '#4ecdc4' }}>{pct(bestQuality)}</span>
                        <span className="clab-stat-label">Best Quality</span>
                    </div>
                    <div className="clab-stat">
                        <span className="clab-stat-value">{Math.round(avgTime)}ms</span>
                        <span className="clab-stat-label">Avg Time</span>
                    </div>
                    <button className="clab-btn-sm" onClick={refresh} title="Refresh from MCP" style={{ alignSelf: 'center' }}>
                        ⟳ Refresh
                    </button>
                </div>
            </div>

            {/* ─── Tabs ─── */}
            <div className="clab-tabs">
                {(['leaderboard', 'strategies', 'evolution', 'history'] as const).map(t => (
                    <button
                        key={t}
                        className={`clab-tab ${tab === t ? 'active' : ''}`}
                        onClick={() => setTab(t)}
                    >
                        {t === 'leaderboard' ? '🏆 Leaderboard' :
                            t === 'strategies' ? '🔌 Strategies' :
                                t === 'evolution' ? '🧬 Evolution' :
                                    '📜 History'}
                    </button>
                ))}
            </div>

            {/* ─── Tab Content ─── */}
            <div className="clab-body">
                {tab === 'leaderboard' && (
                    <div className="clab-leaderboard">
                        <div className="clab-table">
                            <div className="clab-table-header">
                                <span className="clab-col-rank">Rank</span>
                                <span className="clab-col-name">Variant</span>
                                <span className="clab-col-gen">Gen</span>
                                <span className="clab-col-quality">Quality</span>
                                <span className="clab-col-bar"></span>
                                <span className="clab-col-time">Time</span>
                                <span className="clab-col-runs">Runs</span>
                                <span className="clab-col-range">Range</span>
                            </div>
                            {leaderboard.map(entry => (
                                <div key={entry.variant} className={`clab-table-row ${entry.rank <= 3 ? 'top3' : ''}`}>
                                    <span className="clab-col-rank">{medal(entry.rank)}</span>
                                    <span className="clab-col-name">
                                        <span className="clab-variant-name">{entry.variant}</span>
                                        {entry.parent && <span className="clab-variant-parent">← {entry.parent}</span>}
                                    </span>
                                    <span className="clab-col-gen">
                                        <span className={`clab-gen-badge gen-${entry.generation}`}>
                                            {genTag(entry.generation)}
                                        </span>
                                    </span>
                                    <span className="clab-col-quality">{pct(entry.avg_quality)}</span>
                                    <span className="clab-col-bar">
                                        <div className="clab-quality-bar">
                                            <div
                                                className="clab-quality-fill"
                                                style={{
                                                    width: `${entry.avg_quality * 100}%`,
                                                    background: entry.rank === 1 ? 'var(--clab-gold)' :
                                                        entry.rank === 2 ? 'var(--clab-silver)' :
                                                            entry.rank === 3 ? 'var(--clab-bronze)' :
                                                                'var(--clab-bar)',
                                                }}
                                            />
                                        </div>
                                    </span>
                                    <span className="clab-col-time">{Math.round(entry.avg_time_ms)}ms</span>
                                    <span className="clab-col-runs">{entry.runs}</span>
                                    <span className="clab-col-range">{pct(entry.worst)}–{pct(entry.best)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {tab === 'strategies' && (
                    <div className="clab-strategies-grid">
                        {strategies.map(s => {
                            const score = leaderboard.find(l => l.variant === s.name);
                            return (
                                <div key={s.name} className="clab-strategy-card">
                                    <div className="clab-strategy-header">
                                        <span className="clab-strategy-name">{s.name}</span>
                                        {score && <span className="clab-strategy-rank">{medal(score.rank)}</span>}
                                    </div>
                                    <div className="clab-strategy-desc">{s.description}</div>
                                    {score && (
                                        <div className="clab-strategy-stats">
                                            <span>Quality: <strong>{pct(score.avg_quality)}</strong></span>
                                            <span>Time: <strong>{Math.round(score.avg_time_ms)}ms</strong></span>
                                            <span>Runs: <strong>{score.runs}</strong></span>
                                        </div>
                                    )}
                                    <div className="clab-strategy-actions">
                                        <button className="clab-btn-sm" onClick={() => { setForkParent(s.name); setTab('evolution'); }}>
                                            🧬 Fork
                                        </button>
                                        <button className="clab-btn-sm" onClick={() => { setTournamentTask('Audit registry'); setTab('evolution'); }}>
                                            🏟️ Test
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {tab === 'evolution' && (
                    <div className="clab-evolution">
                        {/* Fork Controls */}
                        <div className="clab-section">
                            <div className="clab-section-title">Fork a Variant</div>
                            <div className="clab-fork-form">
                                <div className="clab-form-row">
                                    <label>Parent</label>
                                    <select value={forkParent} onChange={e => setForkParent(e.target.value)}>
                                        <option value="">Select parent...</option>
                                        {leaderboard.map(e => (
                                            <option key={e.variant} value={e.variant}>{e.variant} ({pct(e.avg_quality)})</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="clab-form-row">
                                    <label>Child Name</label>
                                    <input
                                        value={forkChild}
                                        onChange={e => setForkChild(e.target.value)}
                                        placeholder="e.g. hhni_deep_v3"
                                    />
                                </div>
                                <div className="clab-form-row">
                                    <label>Mutations</label>
                                    <input
                                        value={forkMutations}
                                        onChange={e => setForkMutations(e.target.value)}
                                        placeholder="max_results=30,timeout=60"
                                    />
                                </div>
                                <button
                                    className="clab-btn-primary"
                                    disabled={!forkParent || !forkChild}
                                    onClick={handleFork}
                                >
                                    🧬 Fork Variant
                                </button>
                            </div>
                        </div>

                        {/* Tournament Controls */}
                        <div className="clab-section">
                            <div className="clab-section-title">Run Tournament</div>
                            <div className="clab-fork-form">
                                <div className="clab-form-row">
                                    <label>Task</label>
                                    <input
                                        value={tournamentTask}
                                        onChange={e => setTournamentTask(e.target.value)}
                                        placeholder="Audit the registry module"
                                    />
                                </div>
                                <button
                                    className="clab-btn-primary"
                                    disabled={tournamentRunning || !tournamentTask.trim()}
                                    onClick={() => runTournament(tournamentTask)}
                                >
                                    {tournamentRunning ? '⟳ Running...' : '🏟️ Run Tournament'}
                                </button>
                            </div>
                        </div>

                        {/* Lineage Tree */}
                        <div className="clab-section">
                            <div className="clab-section-title">Lineage Tree</div>
                            <div className="clab-lineage">
                                {leaderboard
                                    .filter(e => !e.parent)
                                    .map(base => (
                                        <div key={base.variant} className="clab-lineage-branch">
                                            <div className="clab-lineage-node root">
                                                <span className="clab-lineage-name">{base.variant}</span>
                                                <span className="clab-lineage-score">{pct(base.avg_quality)}</span>
                                            </div>
                                            {leaderboard
                                                .filter(e => e.base === base.variant && e.parent)
                                                .sort((a, b) => a.generation - b.generation)
                                                .map(child => (
                                                    <div key={child.variant} className="clab-lineage-node child" style={{ marginLeft: child.generation * 24 }}>
                                                        <span className="clab-lineage-arrow">└─</span>
                                                        <span className="clab-lineage-name">{child.variant}</span>
                                                        <span className={`clab-gen-badge gen-${child.generation}`}>{genTag(child.generation)}</span>
                                                        <span className="clab-lineage-score">{pct(child.avg_quality)}</span>
                                                    </div>
                                                ))
                                            }
                                        </div>
                                    ))
                                }
                            </div>
                        </div>
                    </div>
                )}

                {tab === 'history' && (
                    <div className="clab-history">
                        {history.map(h => (
                            <div key={h.id} className="clab-history-card">
                                <div className="clab-history-header">
                                    <span className="clab-history-id">{h.id}</span>
                                    <span className="clab-history-time">{timeAgo(h.timestamp)}</span>
                                </div>
                                <div className="clab-history-tasks">
                                    {h.tasks.map(t => <span key={t} className="clab-history-task">{t}</span>)}
                                </div>
                                <div className="clab-history-meta">
                                    <span>{h.variants.length} variants · {h.scoreCount} scores</span>
                                    <span className="clab-history-winner">Winner: <strong>{h.winner}</strong></span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* ─── Toast ─── */}
            {(lastResult || lastError) && (
                <div className="clab-result-toast" style={lastError ? { borderColor: 'var(--clab-danger)', color: 'var(--clab-danger)' } : {}}>
                    {lastResult || lastError}
                </div>
            )}
        </div>
    );
}
