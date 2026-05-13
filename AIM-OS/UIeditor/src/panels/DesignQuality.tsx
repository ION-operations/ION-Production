/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Design Quality Panel
   5-dimension quality indicator: spacing, contrast, type, responsive, perf.
   Awareness, not enforcement.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useEditorStore } from '../store/editorStore';
import type { DesignIssue } from '../types';

const DIMENSIONS: { key: keyof Omit<import('../types').DesignQualityScore, 'overall' | 'issues'>; label: string; icon: string }[] = [
    { key: 'spacing', label: 'Spacing Consistency', icon: '⊞' },
    { key: 'contrast', label: 'Color Contrast', icon: '◐' },
    { key: 'typeHierarchy', label: 'Type Hierarchy', icon: '𝐓' },
    { key: 'responsiveFlow', label: 'Responsive Flow', icon: '⇔' },
    { key: 'animationPerf', label: 'Animation Perf', icon: '▸' },
];

function scoreColor(score: number): string {
    if (score >= 90) return 'var(--ob-success)';
    if (score >= 70) return 'var(--ob-accent)';
    if (score >= 50) return 'var(--ob-warning, #f59e0b)';
    return 'var(--ob-error, #ef4444)';
}

function severityIcon(sev: DesignIssue['severity']): string {
    if (sev === 'error') return '●';
    if (sev === 'warning') return '▲';
    return '○';
}

export default function DesignQuality() {
    const quality = useEditorStore((s) => s.designQuality);
    const selectNode = useEditorStore((s) => s.selectNode);

    return (
        <div className="ob-dq-panel">
            {/* Overall score */}
            <div className="ob-dq-overall">
                <svg width={64} height={64} viewBox="0 0 64 64">
                    {/* Background ring */}
                    <circle cx="32" cy="32" r="27" fill="none" stroke="rgba(255,255,255,0.06)"
                        strokeWidth="5" />
                    {/* Score arc */}
                    <circle cx="32" cy="32" r="27" fill="none"
                        stroke={scoreColor(quality.overall)}
                        strokeWidth="5"
                        strokeDasharray={`${(quality.overall / 100) * 170} 170`}
                        strokeDashoffset="0"
                        strokeLinecap="round"
                        transform="rotate(-90,32,32)"
                        opacity="0.8"
                    />
                    {/* Score text */}
                    <text x="32" y="30" textAnchor="middle" fill="var(--ob-text-primary)"
                        fontSize="16" fontWeight="700">{quality.overall}</text>
                    <text x="32" y="42" textAnchor="middle" fill="rgba(255,255,255,0.3)"
                        fontSize="7" fontWeight="500">QUALITY</text>
                </svg>
                <div className="ob-dq-overall-label">
                    <span className="ob-dq-grade" style={{ color: scoreColor(quality.overall) }}>
                        {quality.overall >= 90 ? 'Excellent' : quality.overall >= 70 ? 'Good' : quality.overall >= 50 ? 'Fair' : 'Needs Work'}
                    </span>
                    <span className="ob-dq-issues-count">{quality.issues.length} suggestions</span>
                </div>
            </div>

            {/* Dimension bars */}
            <div className="ob-dq-dimensions">
                {DIMENSIONS.map(({ key, label, icon }) => {
                    const score = quality[key];
                    return (
                        <div key={key} className="ob-dq-dim">
                            <div className="ob-dq-dim-header">
                                <span className="ob-dq-dim-icon">{icon}</span>
                                <span className="ob-dq-dim-label">{label}</span>
                                <span className="ob-dq-dim-score" style={{ color: scoreColor(score) }}>{score}</span>
                            </div>
                            <div className="ob-dq-dim-track">
                                <div className="ob-dq-dim-fill" style={{
                                    width: `${score}%`,
                                    background: scoreColor(score),
                                }} />
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Issues list */}
            <div className="ob-dq-issues">
                <div className="ob-dq-issues-title">SUGGESTIONS</div>
                {quality.issues.map((issue, i) => (
                    <button key={i} className={`ob-dq-issue ${issue.severity}`}
                        onClick={() => issue.nodeId && selectNode(issue.nodeId)}>
                        <span className="ob-dq-issue-icon">{severityIcon(issue.severity)}</span>
                        <span className="ob-dq-issue-msg">{issue.message}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
