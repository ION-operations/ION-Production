/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Design Whispers
   Contextual AI suggestions that slide in at the bottom of the canvas.
   Non-intrusive, dismissible, and genuinely helpful.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useEditorStore } from '../store/editorStore';

const TYPE_ICON: Record<string, string> = {
    'token-suggestion': '🎯',
    'contrast-warning': '◐',
    'pattern-detected': '✦',
    'spacing-unify': '⊞',
    'accessibility': '♿',
};

const TYPE_COLOR: Record<string, string> = {
    'token-suggestion': 'var(--ob-accent)',
    'contrast-warning': 'var(--ob-warning, #f59e0b)',
    'pattern-detected': 'var(--ob-purple)',
    'spacing-unify': 'var(--ob-success)',
    'accessibility': 'var(--ob-accent)',
};

export default function DesignWhispers() {
    const whispers = useEditorStore((s) => s.whispers);
    const dismissWhisper = useEditorStore((s) => s.dismissWhisper);
    const acceptWhisper = useEditorStore((s) => s.acceptWhisper);

    // Show only the first non-dismissed whisper
    const active = whispers.find((w) => !w.dismissed);
    if (!active) return null;

    const color = TYPE_COLOR[active.type] ?? 'var(--ob-accent)';
    const icon = TYPE_ICON[active.type] ?? '💡';

    return (
        <div className="ob-whisper" style={{ '--whisper-color': color } as React.CSSProperties}>
            <div className="ob-whisper-icon">{icon}</div>
            <div className="ob-whisper-body">
                <div className="ob-whisper-message">{active.message}</div>
                {active.suggestion && (
                    <div className="ob-whisper-suggestion">
                        <code>{active.suggestion}</code>
                    </div>
                )}
            </div>
            <div className="ob-whisper-actions">
                <button className="ob-whisper-accept" onClick={() => acceptWhisper(active.id)}>
                    Apply
                </button>
                <button className="ob-whisper-dismiss" onClick={() => dismissWhisper(active.id)}>
                    ✕
                </button>
            </div>
        </div>
    );
}
