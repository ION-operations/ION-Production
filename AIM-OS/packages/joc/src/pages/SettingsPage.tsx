import { useState } from 'react';

// ─── Types ───

interface SettingsSection {
    id: string;
    label: string;
    icon: string;
}

const SECTIONS: SettingsSection[] = [
    { id: 'appearance', label: 'Appearance', icon: '🎨' },
    { id: 'keybindings', label: 'Keybindings', icon: '⌨' },
    { id: 'mcp', label: 'MCP Endpoints', icon: '🔌' },
    { id: 'diagnostics', label: 'MCP Diagnostics', icon: '🩺' },
    { id: 'polling', label: 'Polling & Refresh', icon: '🔄' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'storage', label: 'Storage Browser', icon: '💾' },
    { id: 'data', label: 'Data & Storage', icon: '💾' },
    { id: 'about', label: 'About', icon: 'ℹ️' },
];

const KEYBINDINGS = [
    { action: 'Command Palette', keys: 'Ctrl+Shift+P', category: 'Navigation' },
    { action: 'Quick Dispatch', keys: 'Ctrl+D', category: 'Dispatch' },
    { action: 'Toggle Bottom Panel', keys: 'Ctrl+J', category: 'Navigation' },
    { action: 'Open ChatGPT Session', keys: 'Ctrl+1', category: 'Session' },
    { action: 'Open Gemini Session', keys: 'Ctrl+2', category: 'Session' },
    { action: 'Focus Search', keys: 'Ctrl+K', category: 'Navigation' },
    { action: 'Close Tab', keys: 'Ctrl+W', category: 'Navigation' },
    { action: 'Next Tab', keys: 'Ctrl+Tab', category: 'Navigation' },
    { action: 'Keyboard Shortcuts', keys: '?', category: 'System' },
    { action: 'Toggle Fullscreen', keys: 'F11', category: 'System' },
    { action: 'Refresh Session', keys: 'Ctrl+Shift+R', category: 'Session' },
    { action: 'Take Screenshot', keys: 'Ctrl+Shift+S', category: 'Session' },
];

// ─── Component ───

export function SettingsPage() {
    const [activeSection, setActiveSection] = useState('appearance');
    const [theme, setTheme] = useState('midnight');
    const [accentColor, setAccentColor] = useState('#00d4ff');
    const [fontSize, setFontSize] = useState(12);
    const [mcpCore, setMcpCore] = useState('http://localhost:5001');
    const [mcpBas, setMcpBas] = useState('http://localhost:5002');
    const [pollInterval, setPollInterval] = useState(12);
    const [toastsEnabled, setToastsEnabled] = useState(true);
    const [soundEnabled, setSoundEnabled] = useState(false);
    const [desktopNotifs, setDesktopNotifs] = useState(false);

    const themes = [
        { id: 'midnight', label: 'Midnight', preview: '#0f0f23' },
        { id: 'dark', label: 'Dark', preview: '#1a1a2e' },
        { id: 'abyss', label: 'Abyss', preview: '#040410' },
        { id: 'light', label: 'Light', preview: '#f0f0f5' },
    ];

    const accents = ['#00d4ff', '#4ecdc4', '#a882ff', '#ff6b6b', '#ffd93d', '#ff85a2', '#7bed9f'];

    const renderSection = () => {
        switch (activeSection) {
            case 'appearance':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">Theme</h3>
                        <div className="sett-theme-grid">
                            {themes.map(t => (
                                <button key={t.id} className={`sett-theme-card ${theme === t.id ? 'active' : ''}`}
                                    onClick={() => setTheme(t.id)}>
                                    <div className="sett-theme-preview" style={{ background: t.preview }} />
                                    <span>{t.label}</span>
                                </button>
                            ))}
                        </div>

                        <h3 className="sett-section-title">Accent Color</h3>
                        <div className="sett-accent-row">
                            {accents.map(c => (
                                <button key={c} className={`sett-accent-dot ${accentColor === c ? 'active' : ''}`}
                                    style={{ background: c }} onClick={() => setAccentColor(c)} />
                            ))}
                        </div>

                        <h3 className="sett-section-title">Font Size</h3>
                        <div className="sett-slider-row">
                            <input type="range" min={10} max={16} value={fontSize}
                                onChange={e => setFontSize(Number(e.target.value))} className="sett-slider" />
                            <span className="sett-slider-value">{fontSize}px</span>
                        </div>
                    </div>
                );

            case 'keybindings':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">Keyboard Shortcuts</h3>
                        <div className="sett-keybind-table">
                            <div className="sett-keybind-header">
                                <span className="sett-kb-col-action">Action</span>
                                <span className="sett-kb-col-keys">Keys</span>
                                <span className="sett-kb-col-cat">Category</span>
                            </div>
                            {KEYBINDINGS.map(kb => (
                                <div key={kb.action} className="sett-keybind-row">
                                    <span className="sett-kb-col-action">{kb.action}</span>
                                    <span className="sett-kb-col-keys"><kbd>{kb.keys}</kbd></span>
                                    <span className="sett-kb-col-cat">{kb.category}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                );

            case 'mcp':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">MCP Endpoints</h3>
                        <div className="sett-field">
                            <label className="sett-label">Core MCP Server (Port 5001)</label>
                            <input className="sett-input" value={mcpCore} onChange={e => setMcpCore(e.target.value)} />
                            <span className="sett-hint">Lucid MCP — memory, goals, agents, consciousness</span>
                        </div>
                        <div className="sett-field">
                            <label className="sett-label">Browser Automation Service (Port 5002)</label>
                            <input className="sett-input" value={mcpBas} onChange={e => setMcpBas(e.target.value)} />
                            <span className="sett-hint">BAS — CDP sessions, DOM interaction, screenshots</span>
                        </div>
                        <button className="sett-test-btn">🔍 Test Connections</button>
                    </div>
                );

            case 'polling':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">Polling Intervals</h3>
                        <div className="sett-field">
                            <label className="sett-label">Dashboard Refresh</label>
                            <select className="sett-select" value={pollInterval} onChange={e => setPollInterval(Number(e.target.value))}>
                                <option value={5}>5 seconds</option>
                                <option value={12}>12 seconds (default)</option>
                                <option value={30}>30 seconds</option>
                                <option value={60}>60 seconds</option>
                            </select>
                        </div>
                        <div className="sett-field">
                            <label className="sett-label">Session Health Check</label>
                            <select className="sett-select" defaultValue={30}>
                                <option value={10}>10 seconds</option>
                                <option value={30}>30 seconds (default)</option>
                                <option value={60}>60 seconds</option>
                                <option value={120}>2 minutes</option>
                            </select>
                        </div>
                        <div className="sett-field">
                            <label className="sett-label">Agent Comms Poll</label>
                            <select className="sett-select" defaultValue={36}>
                                <option value={12}>12 seconds</option>
                                <option value={36}>36 seconds (default)</option>
                                <option value={72}>72 seconds</option>
                            </select>
                        </div>
                    </div>
                );

            case 'notifications':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">Notification Settings</h3>
                        <div className="sett-toggle-row">
                            <label className="sett-toggle-label">Toast Notifications</label>
                            <label className="sett-switch">
                                <input type="checkbox" checked={toastsEnabled} onChange={e => setToastsEnabled(e.target.checked)} />
                                <span className="sett-switch-slider" />
                            </label>
                        </div>
                        <div className="sett-toggle-row">
                            <label className="sett-toggle-label">Sound Effects</label>
                            <label className="sett-switch">
                                <input type="checkbox" checked={soundEnabled} onChange={e => setSoundEnabled(e.target.checked)} />
                                <span className="sett-switch-slider" />
                            </label>
                        </div>
                        <div className="sett-toggle-row">
                            <label className="sett-toggle-label">Desktop Notifications</label>
                            <label className="sett-switch">
                                <input type="checkbox" checked={desktopNotifs} onChange={e => setDesktopNotifs(e.target.checked)} />
                                <span className="sett-switch-slider" />
                            </label>
                        </div>
                    </div>
                );

            case 'data':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">Data Management</h3>
                        <div className="sett-data-actions">
                            <button className="sett-data-btn">📤 Export Settings</button>
                            <button className="sett-data-btn">📥 Import Settings</button>
                            <button className="sett-data-btn">💾 Backup Session Data</button>
                            <button className="sett-data-btn danger">🗑 Clear All Local Data</button>
                            <button className="sett-data-btn danger">↻ Reset to Defaults</button>
                        </div>
                    </div>
                );

            case 'about':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">About JOC</h3>
                        <div className="sett-about">
                            <div className="sett-about-title">Joint Operations Center</div>
                            <div className="sett-about-version">v1.0.0-alpha · AIM-OS</div>
                            <div className="sett-about-desc">
                                Unified AI orchestration shell for dispatching, monitoring, and coordinating
                                browser-based AI agents through a dual-MCP integration spine.
                            </div>
                            <div className="sett-about-stack">
                                React 18 · TypeScript · Vite · Zustand · Vanilla CSS
                            </div>
                            <div className="sett-about-credit">Built by Braden · Powered by Claude Opus 4.6</div>
                        </div>
                    </div>
                );

            case 'storage':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">Storage Browser</h3>
                        <div className="sett-data-actions">
                            {[
                                { provider: 'Google Drive', used: 4.2, total: 15, color: '#4285f4' },
                                { provider: 'Local Disk', used: 28.7, total: 256, color: '#666' },
                                { provider: 'AIM-OS Backup', used: 1.8, total: 10, color: '#33cc66' },
                            ].map(q => (
                                <div key={q.provider} style={{ marginBottom: 8 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#aaa', fontFamily: 'var(--font-mono)', marginBottom: 3 }}>
                                        <span>{q.provider}</span>
                                        <span>{q.used} / {q.total} GB</span>
                                    </div>
                                    <div style={{ height: 4, background: '#1a1a1a', borderRadius: 0 }}>
                                        <div style={{ height: '100%', width: `${(q.used / q.total) * 100}%`, background: q.color }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div style={{ marginTop: 12 }}>
                            <h3 className="sett-section-title">Recent Files</h3>
                            {[
                                { name: 'AIM-OS Backups', type: 'folder', modified: 'Today' },
                                { name: 'agent_genome_export.json', type: 'file', modified: '2h ago' },
                                { name: 'dispatch_results_log.csv', type: 'file', modified: '4h ago' },
                                { name: 'credential_vault.enc', type: 'file', modified: 'Today' },
                            ].map(f => (
                                <div key={f.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #1a1a1a', fontSize: 11, color: '#888' }}>
                                    <span style={{ color: f.type === 'folder' ? '#999' : '#666' }}>{f.type === 'folder' ? '📁' : '📄'} {f.name}</span>
                                    <span>{f.modified}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                );

            case 'diagnostics':
                return (
                    <div className="sett-section">
                        <h3 className="sett-section-title">MCP Diagnostics</h3>
                        <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
                            <div className="sett-data-btn" style={{ flex: 1, textAlign: 'center', padding: 8 }}>
                                <div style={{ fontSize: 18, fontFamily: 'var(--font-mono)', color: '#33cc66' }}>✓</div>
                                <div style={{ fontSize: 10, color: '#888' }}>Core MCP</div>
                                <div style={{ fontSize: 9, color: '#555' }}>:5001</div>
                            </div>
                            <div className="sett-data-btn" style={{ flex: 1, textAlign: 'center', padding: 8 }}>
                                <div style={{ fontSize: 18, fontFamily: 'var(--font-mono)', color: '#33cc66' }}>✓</div>
                                <div style={{ fontSize: 10, color: '#888' }}>BAS MCP</div>
                                <div style={{ fontSize: 9, color: '#555' }}>:5002</div>
                            </div>
                        </div>
                        <h3 className="sett-section-title">Available Tools</h3>
                        <div style={{ maxHeight: 200, overflow: 'auto' }}>
                            {['store_memory', 'retrieve_memory', 'synthesize_knowledge', 'track_confidence', 'create_plan', 'send_ai_message', 'get_problems', 'execute_math_code'].map(tool => (
                                <div key={tool} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '3px 0', fontSize: 11, fontFamily: 'var(--font-mono)', color: '#777', borderBottom: '1px solid #141414' }}>
                                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#33cc66', flexShrink: 0 }} />
                                    {tool}
                                </div>
                            ))}
                        </div>
                        <button className="sett-test-btn" style={{ marginTop: 8 }}>Run Health Check</button>
                    </div>
                );

            default: return null;
        }
    };

    return (
        <div className="sett-page">
            <div className="sett-sidebar">
                {SECTIONS.map(s => (
                    <button key={s.id} className={`sett-sidebar-btn ${activeSection === s.id ? 'active' : ''}`}
                        onClick={() => setActiveSection(s.id)}>
                        <span className="sett-sidebar-icon">{s.icon}</span>
                        <span className="sett-sidebar-label">{s.label}</span>
                    </button>
                ))}
            </div>
            <div className="sett-content">
                {renderSection()}
            </div>
        </div>
    );
}
