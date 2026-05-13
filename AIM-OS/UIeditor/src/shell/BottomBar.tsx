/* OmniBuilder — Bottom Panel (Timeline + Patches + Console) — Custom SVG Icons */
import { useEditorStore } from '../store/editorStore';
import { IconTimeline, IconPatches, IconConsole, IconPlay, IconPause, IconChevron } from '../icons/Icons';
import DesignQuality from '../panels/DesignQuality';

// ─── Timeline ───────────────────────────────────────────────────────────────
function TimelineView() {
    const tracks = useEditorStore((s) => s.motionTracks);
    const nodes = useEditorStore((s) => s.nodes);
    const playheadMs = useEditorStore((s) => s.playheadMs);
    const isPlaying = useEditorStore((s) => s.isPlaying);
    const duration = useEditorStore((s) => s.timelineDuration);
    const { togglePlayback, setPlayhead } = useEditorStore();

    const pxPerMs = 0.6;
    const totalWidth = duration * pxPerMs + 80;
    const ticks: number[] = [];
    for (let t = 0; t <= duration; t += 100) ticks.push(t);

    return (
        <div className="ob-timeline">
            <div className="ob-timeline-controls">
                <button className="ob-timeline-play-btn" onClick={togglePlayback}>
                    {isPlaying ? <IconPause size={10} /> : <IconPlay size={10} />}
                </button>
                <span className="ob-timeline-time">{playheadMs.toFixed(0)}ms</span>
                <span style={{ fontSize: '9px', color: 'var(--ob-text-tertiary)' }}>/ {duration}ms</span>
                <div style={{ flex: 1 }} />
                <span style={{ fontSize: '9px', color: 'var(--ob-text-tertiary)' }}>{tracks.length} tracks</span>
            </div>

            <div className="ob-timeline-body">
                <div className="ob-timeline-labels">
                    <div className="ob-timeline-label-row" style={{ height: 24, borderBottom: '1px solid var(--ob-border-subtle)' }}>
                        <span style={{ fontSize: '8px', color: 'var(--ob-text-tertiary)' }}>TRACK</span>
                    </div>
                    {tracks.map((track) => {
                        const node = nodes[track.nodeId];
                        return (
                            <div key={track.id} className="ob-timeline-label-row">
                                <span>{node?.label ?? track.nodeId}</span>
                                <span className="ob-timeline-label-prop">.{track.property}</span>
                            </div>
                        );
                    })}
                </div>

                <div className="ob-timeline-tracks-area" style={{ minWidth: totalWidth }}>
                    <div className="ob-time-ruler" style={{ width: totalWidth }}>
                        {ticks.map((t) => (
                            <div key={t} className={`ob-time-tick${t % 500 === 0 ? ' major' : ''}`}
                                style={{ left: t * pxPerMs }}
                            >{t % 200 === 0 ? `${t}ms` : ''}</div>
                        ))}
                    </div>

                    {tracks.map((track) => (
                        <div key={track.id} className="ob-timeline-track-row"
                            onClick={(e) => {
                                const rect = e.currentTarget.getBoundingClientRect();
                                setPlayhead(Math.max(0, Math.round((e.clientX - rect.left) / pxPerMs)));
                            }}
                        >
                            {track.keyframes.slice(0, -1).map((kf, i) => {
                                const next = track.keyframes[i + 1];
                                return (
                                    <div key={`seg_${i}`} className="ob-easing-segment" style={{
                                        left: kf.t * pxPerMs, width: (next.t - kf.t) * pxPerMs,
                                    }} />
                                );
                            })}
                            {track.keyframes.map((kf, i) => (
                                <div key={i} className="ob-keyframe" style={{ left: kf.t * pxPerMs }}
                                    title={`${kf.t}ms: ${kf.value}${kf.easing ? ` (${kf.easing})` : ''}`} />
                            ))}
                        </div>
                    ))}

                    <div className="ob-playhead" style={{ left: playheadMs * pxPerMs, top: 0 }} />
                </div>
            </div>
        </div>
    );
}

// ─── Patch Review ───────────────────────────────────────────────────────────
function PatchReview() {
    const candidates = useEditorStore((s) => s.patchCandidates);
    const { acceptPatch } = useEditorStore();

    if (candidates.length === 0) {
        return (
            <div className="ob-empty-state">
                <div style={{ fontSize: '24px', opacity: 0.2 }}>
                    <IconPatches size={32} />
                </div>
                <div className="ob-empty-state-text">No pending patches</div>
            </div>
        );
    }

    const maxScore = Math.max(...candidates.map((c) => c.score));

    return (
        <div className="ob-patches">
            {candidates.map((c, i) => (
                <div key={c.id} className={`ob-patch-card${i === 0 ? ' best' : ''}`}>
                    <div className="ob-patch-header">
                        <span className="ob-patch-rank">{i + 1}</span>
                        <span className="ob-patch-strategy">{c.strategy.replace(/-/g, ' ')}</span>
                        <div className="ob-patch-score-bar">
                            <div className="ob-patch-score-fill" style={{ width: `${(c.score / maxScore) * 100}%` }} />
                        </div>
                        <span className="ob-patch-score-num">{c.score}</span>
                    </div>
                    <div className="ob-patch-rationale">
                        {c.rationale.map((r, j) => (
                            <span key={j} className="ob-patch-rationale-item">{r}</span>
                        ))}
                    </div>
                    {c.risks.length > 0 && (
                        <div className="ob-patch-risks">
                            {c.risks.map((r, j) => (
                                <span key={j} className="ob-patch-risk-tag">{r}</span>
                            ))}
                        </div>
                    )}
                    {c.filePatches[0]?.before && (
                        <div className="ob-diff">
                            <div className="ob-diff-remove">- {c.filePatches[0].before}</div>
                            <div className="ob-diff-add">+ {c.filePatches[0].after}</div>
                            <div style={{ color: 'var(--ob-text-tertiary)', marginTop: 2 }}>
                // {c.filePatches[0].filePath}
                            </div>
                        </div>
                    )}
                    <div className="ob-patch-actions">
                        <button className="ob-patch-btn">Inspect</button>
                        <button className="ob-patch-btn accept" onClick={() => acceptPatch(c.id)}>Accept</button>
                    </div>
                </div>
            ))}
        </div>
    );
}

// ─── Console ────────────────────────────────────────────────────────────────
function ConsoleView() {
    const lastV = useEditorStore((s) => s.lastVerification);
    return (
        <div style={{ padding: '12px', fontFamily: 'var(--ob-font-mono)', fontSize: '11px' }}>
            <div style={{ color: 'var(--ob-text-tertiary)', marginBottom: 8 }}>OmniBuilder Console v0.1.0</div>
            {lastV ? (
                <>
                    <div style={{ color: lastV.buildOk ? 'var(--ob-success)' : 'var(--ob-danger)' }}>
                        [verify] Build: {lastV.buildOk ? 'PASS' : 'FAIL'}
                    </div>
                    <div style={{ color: lastV.runtimeOk ? 'var(--ob-success)' : 'var(--ob-danger)' }}>
                        [verify] Runtime: {lastV.runtimeOk ? 'PASS' : 'FAIL'}
                    </div>
                    <div style={{ color: 'var(--ob-info)' }}>
                        [verify] Visual similarity: {(lastV.visualSimilarity * 100).toFixed(1)}%
                    </div>
                    <div style={{ color: lastV.accepted ? 'var(--ob-success)' : 'var(--ob-warning)' }}>
                        [verify] Status: {lastV.accepted ? 'ACCEPTED' : 'PENDING'}
                    </div>
                </>
            ) : (
                <div style={{ color: 'var(--ob-text-tertiary)' }}>
                    <div>[ready] Edit-intent compiler loaded (5 strategies)</div>
                    <div>[ready] Source binding engine active</div>
                    <div>[ready] Verification pipeline standby</div>
                    <div style={{ color: 'var(--ob-success)', marginTop: 4 }}>[info] Awaiting edit intent...</div>
                </div>
            )}
        </div>
    );
}

// ─── Bottom Panel Shell ─────────────────────────────────────────────────────
export default function BottomPanel() {
    const { bottomPanelTab, setBottomPanelTab, toggleBottomPanel } = useEditorStore();

    return (
        <div className="ob-bottom-panel">
            <div className="ob-bottom-tabs">
                {([
                    { key: 'timeline' as const, Icon: IconTimeline, label: 'Timeline' },
                    { key: 'patches' as const, Icon: IconPatches, label: 'Patches' },
                    { key: 'console' as const, Icon: IconConsole, label: 'Console' },
                    { key: 'quality' as const, Icon: IconConsole, label: 'Quality' },
                ]).map(({ key, Icon, label }) => (
                    <button
                        key={key}
                        className={`ob-bottom-tab${bottomPanelTab === key ? ' active' : ''}`}
                        onClick={() => setBottomPanelTab(key)}
                    >
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                            <Icon size={12} /> {label}
                        </span>
                    </button>
                ))}
                <div className="ob-bottom-spacer" />
                <button className="ob-bottom-toggle" onClick={toggleBottomPanel}>
                    <IconChevron size={12} direction="down" />
                </button>
            </div>
            <div className="ob-bottom-content">
                {bottomPanelTab === 'timeline' && <TimelineView />}
                {bottomPanelTab === 'patches' && <PatchReview />}
                {bottomPanelTab === 'console' && <ConsoleView />}
                {bottomPanelTab === 'quality' && <DesignQuality />}
            </div>
        </div>
    );
}
