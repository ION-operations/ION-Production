import { useState, useEffect } from 'react';

// ─── Data ───

interface ShortcutGroup {
    title: string;
    shortcuts: { keys: string; action: string }[];
}

const SHORTCUT_GROUPS: ShortcutGroup[] = [
    {
        title: '🧭 Navigation',
        shortcuts: [
            { keys: 'Ctrl+Shift+P', action: 'Command Palette' },
            { keys: 'Ctrl+J', action: 'Toggle Bottom Panel' },
            { keys: 'Ctrl+Tab', action: 'Next Tab' },
            { keys: 'Ctrl+Shift+Tab', action: 'Previous Tab' },
            { keys: 'Ctrl+W', action: 'Close Tab' },
            { keys: 'Ctrl+K', action: 'Focus Search' },
            { keys: 'F11', action: 'Toggle Fullscreen' },
        ],
    },
    {
        title: '🎯 Dispatch',
        shortcuts: [
            { keys: 'Ctrl+D', action: 'Quick Dispatch' },
            { keys: 'Ctrl+Shift+D', action: 'Open Mission Builder' },
            { keys: 'Ctrl+Enter', action: 'Send Prompt' },
            { keys: 'Ctrl+Shift+A', action: 'Attach Files' },
        ],
    },
    {
        title: '🌐 Session',
        shortcuts: [
            { keys: 'Ctrl+1', action: 'Open ChatGPT' },
            { keys: 'Ctrl+2', action: 'Open Gemini' },
            { keys: 'Ctrl+3', action: 'Open Claude' },
            { keys: 'Ctrl+Shift+R', action: 'Refresh Session' },
            { keys: 'Ctrl+Shift+S', action: 'Take Screenshot' },
            { keys: 'Ctrl+Shift+I', action: 'Inject Prompt' },
            { keys: 'Ctrl+Shift+E', action: 'Extract Response' },
        ],
    },
    {
        title: '⚙ System',
        shortcuts: [
            { keys: '?', action: 'Show Keyboard Shortcuts' },
            { keys: 'Ctrl+,', action: 'Open Settings' },
            { keys: 'Ctrl+Shift+G', action: 'GPU Monitor' },
            { keys: 'Ctrl+Shift+L', action: 'Activity Log' },
            { keys: 'Escape', action: 'Close Modal / Cancel' },
        ],
    },
];

// ─── Component ───

interface Props {
    isOpen: boolean;
    onClose: () => void;
}

export function KeyboardShortcutsOverlay({ isOpen, onClose }: Props) {
    const [filter, setFilter] = useState('');

    useEffect(() => {
        if (isOpen) setFilter('');
    }, [isOpen]);

    if (!isOpen) return null;

    const filtered = SHORTCUT_GROUPS.map(group => ({
        ...group,
        shortcuts: group.shortcuts.filter(s =>
            s.action.toLowerCase().includes(filter.toLowerCase()) ||
            s.keys.toLowerCase().includes(filter.toLowerCase())
        ),
    })).filter(g => g.shortcuts.length > 0);

    return (
        <div className="kbs-overlay" onClick={onClose}>
            <div className="kbs-modal" onClick={e => e.stopPropagation()}>
                <div className="kbs-header">
                    <span className="kbs-title">⌨ Keyboard Shortcuts</span>
                    <button className="kbs-close" onClick={onClose}>✕</button>
                </div>
                <div className="kbs-search">
                    <input className="kbs-search-input" placeholder="Filter shortcuts..."
                        value={filter} onChange={e => setFilter(e.target.value)} autoFocus />
                </div>
                <div className="kbs-body">
                    {filtered.map(group => (
                        <div key={group.title} className="kbs-group">
                            <div className="kbs-group-title">{group.title}</div>
                            {group.shortcuts.map(s => (
                                <div key={s.action} className="kbs-shortcut-row">
                                    <span className="kbs-action">{s.action}</span>
                                    <span className="kbs-keys">
                                        {s.keys.split('+').map((k, i) => (
                                            <span key={i}>
                                                {i > 0 && <span className="kbs-plus">+</span>}
                                                <kbd className="kbs-key">{k}</kbd>
                                            </span>
                                        ))}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
                <div className="kbs-footer">
                    Press <kbd className="kbs-key">?</kbd> to toggle this overlay
                </div>
            </div>
        </div>
    );
}
