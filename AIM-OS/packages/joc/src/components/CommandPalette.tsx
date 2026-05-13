import { useState, useEffect, useCallback, useRef } from 'react';
import { useJOCStore } from '../store/jocStore';

// ─── Action Registry ───

interface CommandAction {
    id: string;
    label: string;
    category: 'navigate' | 'session' | 'mission' | 'compute' | 'system';
    icon: string;
    shortcut?: string;
    action: () => void;
}

function useCommandActions(): CommandAction[] {
    const { addTab, setActiveTab, toggleDrawer, setBottomTab, toggleBottomPanel, sessions } = useJOCStore();

    return [
        // ─── Navigate ───
        {
            id: 'nav-dashboard', label: 'Open Dashboard', category: 'navigate', icon: '📊',
            action: () => setActiveTab('dashboard')
        },
        {
            id: 'nav-atlas', label: 'Open System Atlas', category: 'navigate', icon: '🗺️',
            action: () => setActiveTab('atlas')
        },
        {
            id: 'nav-editor', label: 'Open Code Editor', category: 'navigate', icon: '📝',
            action: () => setActiveTab('editor')
        },
        {
            id: 'nav-compute', label: 'Open Compute Fabric', category: 'navigate', icon: '🖥️',
            action: () => { addTab({ id: 'compute', type: 'compute' as any, label: 'Compute', closable: true }); setActiveTab('compute'); }
        },
        {
            id: 'nav-dispatch', label: 'New Mission: Quick Dispatch', category: 'navigate', icon: '🚀', shortcut: 'Ctrl+N',
            action: () => { addTab({ id: `dispatch-${Date.now()}`, type: 'dispatch' as any, label: 'New Dispatch', closable: true }); setActiveTab(`dispatch-${Date.now()}`); }
        },
        {
            id: 'nav-synthesizer', label: 'Open Results Synthesizer', category: 'navigate', icon: '⬡',
            action: () => { addTab({ id: 'synthesizer', type: 'synthesizer' as any, label: 'Synthesizer', closable: true }); setActiveTab('synthesizer'); }
        },
        {
            id: 'nav-comms', label: 'Open Agent Comms', category: 'navigate', icon: '📡',
            action: () => { addTab({ id: 'comms', type: 'comms' as any, label: 'Agent Comms', closable: true }); setActiveTab('comms'); }
        },
        {
            id: 'nav-health', label: 'Fleet Health Monitor', category: 'navigate', icon: '◎',
            action: () => { addTab({ id: 'health', type: 'health' as any, label: 'Fleet Health', closable: true }); setActiveTab('health'); }
        },
        {
            id: 'nav-context', label: 'Auto-Context Engine', category: 'navigate', icon: '🔍',
            action: () => { addTab({ id: 'context', type: 'context' as any, label: 'Auto-Context', closable: true }); setActiveTab('context'); }
        },
        {
            id: 'nav-projects', label: 'Project Catalog', category: 'navigate', icon: '📂',
            action: () => { addTab({ id: 'projects', type: 'projects' as any, label: 'Projects', closable: true }); setActiveTab('projects'); }
        },
        {
            id: 'nav-vault', label: 'Credential Vault', category: 'navigate', icon: '🔐',
            action: () => { addTab({ id: 'vault', type: 'vault' as any, label: 'Credentials', closable: true }); setActiveTab('vault'); }
        },
        {
            id: 'nav-cli', label: 'CLI Terminal', category: 'navigate', icon: '⌨',
            action: () => { addTab({ id: 'cli', type: 'cli' as any, label: 'CLI Terminal', closable: true }); setActiveTab('cli'); }
        },
        {
            id: 'nav-storage', label: 'Storage Browser', category: 'navigate', icon: '☁️',
            action: () => { addTab({ id: 'storage', type: 'storage' as any, label: 'Storage', closable: true }); setActiveTab('storage'); }
        },
        {
            id: 'nav-settings', label: 'Settings', category: 'navigate', icon: '⚙',
            action: () => { addTab({ id: 'settings', type: 'settings' as any, label: 'Settings', closable: true }); setActiveTab('settings'); }
        },
        {
            id: 'nav-mission-builder', label: 'Mission Builder', category: 'navigate', icon: '🎯',
            action: () => { addTab({ id: 'mission-builder', type: 'mission-builder' as any, label: 'Mission Builder', closable: true }); setActiveTab('mission-builder'); }
        },
        {
            id: 'nav-gpu', label: 'GPU Monitor', category: 'navigate', icon: '🖥',
            action: () => { addTab({ id: 'gpu', type: 'gpu' as any, label: 'GPU Monitor', closable: true }); setActiveTab('gpu'); }
        },
        {
            id: 'nav-activity', label: 'Activity Log', category: 'navigate', icon: '📋',
            action: () => { addTab({ id: 'activity', type: 'activity' as any, label: 'Activity Log', closable: true }); setActiveTab('activity'); }
        },
        {
            id: 'nav-welcome', label: 'Welcome / Home', category: 'navigate', icon: '◎',
            action: () => { addTab({ id: 'welcome', type: 'welcome' as any, label: 'Welcome', closable: true }); setActiveTab('welcome'); }
        },
        {
            id: 'nav-context-graph', label: 'Context Graph', category: 'navigate', icon: '🕸️',
            action: () => { addTab({ id: 'context-graph', type: 'context-graph' as any, label: 'Context Graph', closable: true }); setActiveTab('context-graph'); }
        },

        // ─── Session ───
        {
            id: 'session-chatgpt', label: 'Open ChatGPT Session', category: 'session', icon: '🌐',
            action: () => { addTab({ id: 'chatgpt-session', type: 'session', label: 'ChatGPT', closable: true, data: { sessionId: 'gpt-1' } }); setActiveTab('chatgpt-session'); }
        },
        {
            id: 'session-gemini', label: 'Open Gemini Session', category: 'session', icon: '🌐',
            action: () => { addTab({ id: 'gemini-session', type: 'session', label: 'Gemini', closable: true, data: { sessionId: 'gem-1' } }); setActiveTab('gemini-session'); }
        },
        {
            id: 'session-refresh', label: 'Refresh All Sessions', category: 'session', icon: '🔄', shortcut: 'F5',
            action: () => console.log('[JOC] Refreshing all sessions...')
        },
        {
            id: 'session-health', label: 'Session Health Check (All)', category: 'session', icon: '💚', shortcut: 'F6',
            action: () => console.log('[JOC] Running health check on', sessions.length, 'sessions')
        },

        // ─── Mission ───
        {
            id: 'mission-new', label: 'New Mission: Full Composer', category: 'mission', icon: '📋',
            action: () => { addTab({ id: `dispatch-${Date.now()}`, type: 'dispatch' as any, label: 'New Mission', closable: true }); }
        },
        {
            id: 'mission-queue', label: 'Show Mission Queue', category: 'mission', icon: '📋',
            action: () => { setBottomTab('missions'); toggleBottomPanel(); }
        },

        // ─── Compute ───
        {
            id: 'compute-gpu', label: 'GPU Status', category: 'compute', icon: '🖥️',
            action: () => toggleDrawer('compute', 'full')
        },
        {
            id: 'compute-ollama', label: 'Load Local Model (Ollama)', category: 'compute', icon: '🧠',
            action: () => console.log('[JOC] Opening Ollama model manager...')
        },

        // ─── System ───
        {
            id: 'sys-comms', label: 'Open Agent Communications', category: 'system', icon: '💬', shortcut: 'Ctrl+Shift+C',
            action: () => toggleDrawer('comms', 'full')
        },
        {
            id: 'sys-timeline', label: 'Show Git Timeline', category: 'system', icon: '📈',
            action: () => { setBottomTab('timeline'); toggleBottomPanel(); }
        },
        {
            id: 'sys-terminal', label: 'Toggle Terminal', category: 'system', icon: '⌨️', shortcut: 'Ctrl+J',
            action: () => { setBottomTab('terminal'); toggleBottomPanel(); }
        },
        {
            id: 'sys-settings', label: 'Open Settings', category: 'system', icon: '⚙️',
            action: () => toggleDrawer('settings', 'full')
        },
    ];
}

// ─── Fuzzy Search ───

function fuzzyMatch(query: string, text: string): { matches: boolean; score: number } {
    if (!query) return { matches: true, score: 0 };
    const q = query.toLowerCase();
    const t = text.toLowerCase();

    // Exact substring match → highest score
    if (t.includes(q)) return { matches: true, score: 100 };

    // Fuzzy: all chars must appear in order
    let qi = 0;
    let consecutiveBonus = 0;
    let lastMatchIdx = -2;
    for (let ti = 0; ti < t.length && qi < q.length; ti++) {
        if (t[ti] === q[qi]) {
            consecutiveBonus += (ti === lastMatchIdx + 1) ? 10 : 0;
            lastMatchIdx = ti;
            qi++;
        }
    }
    if (qi === q.length) {
        return { matches: true, score: 50 + consecutiveBonus - query.length };
    }
    return { matches: false, score: 0 };
}

// ─── Category Labels ───

const CATEGORY_LABELS: Record<string, string> = {
    navigate: '🗺️ Navigate',
    session: '🌐 Sessions',
    mission: '📋 Missions',
    compute: '🖥️ Compute',
    system: '⚙️ System',
};

// ─── Component ───

export function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const listRef = useRef<HTMLDivElement>(null);
    const actions = useCommandActions();

    // Filter actions by query
    const filtered = actions
        .map(a => ({ ...a, ...fuzzyMatch(query, a.label + ' ' + a.category) }))
        .filter(a => a.matches)
        .sort((a, b) => b.score - a.score);

    // Group by category
    const grouped = filtered.reduce((acc, action) => {
        if (!acc[action.category]) acc[action.category] = [];
        acc[action.category].push(action);
        return acc;
    }, {} as Record<string, typeof filtered>);

    // Flat list for keyboard navigation
    const flatList = Object.values(grouped).flat();

    // Keyboard shortcut to open
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
                e.preventDefault();
                setIsOpen(prev => !prev);
                setQuery('');
                setSelectedIndex(0);
            }
            if (e.key === 'Escape' && isOpen) {
                setIsOpen(false);
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [isOpen]);

    // Focus input on open
    useEffect(() => {
        if (isOpen) {
            requestAnimationFrame(() => inputRef.current?.focus());
        }
    }, [isOpen]);

    // Keyboard navigation
    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(i => Math.min(i + 1, flatList.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(i => Math.max(i - 1, 0));
        } else if (e.key === 'Enter' && flatList[selectedIndex]) {
            e.preventDefault();
            flatList[selectedIndex].action();
            setIsOpen(false);
        }
    }, [flatList, selectedIndex]);

    // Scroll selected into view
    useEffect(() => {
        const el = listRef.current?.querySelector('.cmd-item.selected');
        el?.scrollIntoView({ block: 'nearest' });
    }, [selectedIndex]);

    if (!isOpen) return null;

    return (
        <div className="cmd-palette-overlay" onClick={() => setIsOpen(false)}>
            <div className="cmd-palette" onClick={(e) => e.stopPropagation()}>
                <div className="cmd-input-row">
                    <span className="cmd-icon">⌘</span>
                    <input
                        ref={inputRef}
                        className="cmd-input"
                        placeholder="Type a command..."
                        value={query}
                        onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
                        onKeyDown={handleKeyDown}
                    />
                    <kbd className="cmd-kbd">ESC</kbd>
                </div>

                <div className="cmd-results" ref={listRef}>
                    {Object.entries(grouped).map(([category, items]) => (
                        <div key={category} className="cmd-category">
                            <div className="cmd-category-label">{CATEGORY_LABELS[category] || category}</div>
                            {items.map((item) => {
                                const idx = flatList.indexOf(item);
                                return (
                                    <div
                                        key={item.id}
                                        className={`cmd-item ${idx === selectedIndex ? 'selected' : ''}`}
                                        onClick={() => { item.action(); setIsOpen(false); }}
                                        onMouseEnter={() => setSelectedIndex(idx)}
                                    >
                                        <span className="cmd-item-icon">{item.icon}</span>
                                        <span className="cmd-item-label">{item.label}</span>
                                        {item.shortcut && <kbd className="cmd-item-shortcut">{item.shortcut}</kbd>}
                                    </div>
                                );
                            })}
                        </div>
                    ))}

                    {flatList.length === 0 && (
                        <div className="cmd-empty">No matching commands</div>
                    )}
                </div>

                <div className="cmd-footer">
                    <span>↑↓ Navigate</span>
                    <span>↵ Select</span>
                    <span>esc Close</span>
                </div>
            </div>
        </div>
    );
}
