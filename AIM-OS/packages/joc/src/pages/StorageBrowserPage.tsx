import { useState, useMemo } from 'react';

// ─── Types ───

interface StorageItem {
    id: string;
    name: string;
    type: 'file' | 'folder';
    size?: number;
    modified: string;
    icon: string;
    location: 'drive' | 'local' | 'backup';
    shared?: boolean;
}

interface StorageQuota {
    provider: string;
    used: number;
    total: number;
    icon: string;
}

// ─── Mock Data ───

const STORAGE_ITEMS: StorageItem[] = [
    { id: '1', name: 'AIM-OS Backups', type: 'folder', modified: 'Today', icon: '📁', location: 'drive', shared: false },
    { id: '2', name: 'JOC Screenshots', type: 'folder', modified: 'Today', icon: '📸', location: 'drive', shared: true },
    { id: '3', name: 'Model Checkpoints', type: 'folder', modified: 'Yesterday', icon: '🧠', location: 'drive', shared: false },
    { id: '4', name: 'Session Recordings', type: 'folder', modified: '2 days ago', icon: '🎬', location: 'drive', shared: false },
    { id: '5', name: 'agent_comms_export.json', type: 'file', size: 284000, modified: '1h ago', icon: '📄', location: 'drive' },
    { id: '6', name: 'system_atlas_snapshot.png', type: 'file', size: 2450000, modified: '2h ago', icon: '🖼', location: 'drive' },
    { id: '7', name: 'joc_config_backup.yaml', type: 'file', size: 8400, modified: 'Today', icon: '⚙', location: 'backup' },
    { id: '8', name: 'memory_export_2026-03.json', type: 'file', size: 1560000, modified: 'Yesterday', icon: '💾', location: 'backup' },
    { id: '9', name: 'ollama_models_cache', type: 'folder', modified: '3 days ago', icon: '📦', location: 'local' },
    { id: '10', name: 'chromium_profiles', type: 'folder', modified: 'Today', icon: '🌐', location: 'local' },
    { id: '11', name: 'dispatch_results_log.csv', type: 'file', size: 456000, modified: '4h ago', icon: '📊', location: 'local' },
    { id: '12', name: 'credential_vault.enc', type: 'file', size: 3200, modified: 'Today', icon: '🔐', location: 'local' },
];

const QUOTAS: StorageQuota[] = [
    { provider: 'Google Drive', used: 4.2e9, total: 15e9, icon: '☁️' },
    { provider: 'Local Disk', used: 28.7e9, total: 256e9, icon: '💻' },
    { provider: 'AIM-OS Backup', used: 1.8e9, total: 10e9, icon: '🛡️' },
];

// ─── Component ───

export function StorageBrowserPage() {
    const [search, setSearch] = useState('');
    const [locationFilter, setLocationFilter] = useState<string>('all');
    const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');

    const filtered = useMemo(() => {
        return STORAGE_ITEMS.filter(item => {
            if (search && !item.name.toLowerCase().includes(search.toLowerCase())) return false;
            if (locationFilter !== 'all' && item.location !== locationFilter) return false;
            return true;
        });
    }, [search, locationFilter]);

    const toggleSelect = (id: string) => {
        setSelectedItems(prev => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    };

    const fmtSize = (b?: number) => {
        if (!b) return '—';
        if (b >= 1e9) return `${(b / 1e9).toFixed(1)} GB`;
        if (b >= 1e6) return `${(b / 1e6).toFixed(1)} MB`;
        if (b >= 1e3) return `${(b / 1e3).toFixed(1)} KB`;
        return `${b} B`;
    };

    const locationColors: Record<string, { bg: string; text: string; label: string }> = {
        drive: { bg: 'rgba(78, 205, 196, 0.1)', text: '#4ecdc4', label: 'Drive' },
        local: { bg: 'rgba(168, 130, 255, 0.1)', text: '#a882ff', label: 'Local' },
        backup: { bg: 'rgba(255, 217, 61, 0.1)', text: '#ffd93d', label: 'Backup' },
    };

    return (
        <div className="stor-page">
            {/* ─── Header ─── */}
            <div className="stor-header">
                <div className="stor-header-left">
                    <span className="stor-title">☁️ Storage Browser</span>
                    <span className="stor-subtitle">{STORAGE_ITEMS.length} items · Google Drive + Local + Backups</span>
                </div>
                <div className="stor-header-right">
                    <input className="stor-search" placeholder="Search files..." value={search}
                        onChange={e => setSearch(e.target.value)} />
                    <select className="stor-filter" value={locationFilter}
                        onChange={e => setLocationFilter(e.target.value)}>
                        <option value="all">All Locations</option>
                        <option value="drive">Google Drive</option>
                        <option value="local">Local</option>
                        <option value="backup">Backup</option>
                    </select>
                    <div className="stor-view-toggle">
                        <button className={`stor-view-btn ${viewMode === 'grid' ? 'active' : ''}`} onClick={() => setViewMode('grid')}>▦</button>
                        <button className={`stor-view-btn ${viewMode === 'list' ? 'active' : ''}`} onClick={() => setViewMode('list')}>☰</button>
                    </div>
                    <button className="stor-upload-btn">⬆ Upload</button>
                </div>
            </div>

            <div className="stor-body">
                {/* ─── Main area ─── */}
                <div className="stor-main">
                    {/* ─── Breadcrumb ─── */}
                    <div className="stor-breadcrumb">
                        <span className="stor-bc-item active">☁️ Root</span>
                        <span className="stor-bc-sep">/</span>
                        <span className="stor-bc-item">AIM-OS</span>
                    </div>

                    {/* ─── File List ─── */}
                    {viewMode === 'list' ? (
                        <div className="stor-list">
                            <div className="stor-list-header">
                                <span className="stor-col-check" />
                                <span className="stor-col-name">Name</span>
                                <span className="stor-col-loc">Location</span>
                                <span className="stor-col-size">Size</span>
                                <span className="stor-col-date">Modified</span>
                                <span className="stor-col-actions" />
                            </div>
                            {filtered.map(item => {
                                const loc = locationColors[item.location];
                                const isSelected = selectedItems.has(item.id);
                                return (
                                    <div key={item.id} className={`stor-list-row ${isSelected ? 'selected' : ''}`}>
                                        <span className="stor-col-check" onClick={() => toggleSelect(item.id)}>
                                            {isSelected ? '☑' : '☐'}
                                        </span>
                                        <span className="stor-col-name">
                                            <span className="stor-item-icon">{item.icon}</span>
                                            {item.name}
                                            {item.shared && <span className="stor-shared-badge">👥</span>}
                                        </span>
                                        <span className="stor-col-loc">
                                            <span className="stor-loc-badge" style={{ background: loc.bg, color: loc.text }}>{loc.label}</span>
                                        </span>
                                        <span className="stor-col-size">{item.type === 'folder' ? '—' : fmtSize(item.size)}</span>
                                        <span className="stor-col-date">{item.modified}</span>
                                        <span className="stor-col-actions">
                                            <button className="stor-action-btn">⬇</button>
                                            <button className="stor-action-btn">🗑</button>
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="stor-grid">
                            {filtered.map(item => {
                                const loc = locationColors[item.location];
                                return (
                                    <div key={item.id} className="stor-grid-card" onClick={() => toggleSelect(item.id)}>
                                        <span className="stor-grid-icon">{item.icon}</span>
                                        <span className="stor-grid-name">{item.name}</span>
                                        <div className="stor-grid-meta">
                                            <span className="stor-loc-badge" style={{ background: loc.bg, color: loc.text }}>{loc.label}</span>
                                            <span>{fmtSize(item.size)}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* ─── Quota Sidebar ─── */}
                <div className="stor-quota-panel">
                    <div className="stor-quota-title">Storage Usage</div>
                    {QUOTAS.map(q => {
                        const pct = (q.used / q.total) * 100;
                        const color = pct > 85 ? '#ff6b6b' : pct > 60 ? '#ffd93d' : '#4ecdc4';
                        return (
                            <div key={q.provider} className="stor-quota-item">
                                <div className="stor-quota-header">
                                    <span>{q.icon} {q.provider}</span>
                                    <span style={{ color }}>{pct.toFixed(0)}%</span>
                                </div>
                                <div className="stor-quota-bar">
                                    <div className="stor-quota-fill" style={{ width: `${pct}%`, background: color }} />
                                </div>
                                <div className="stor-quota-detail">
                                    {fmtSize(q.used)} / {fmtSize(q.total)}
                                </div>
                            </div>
                        );
                    })}

                    {/* Quick Actions */}
                    <div className="stor-quota-title" style={{ marginTop: 16 }}>Quick Actions</div>
                    <button className="stor-sidebar-btn">🔄 Sync Google Drive</button>
                    <button className="stor-sidebar-btn">💾 Backup AIM-OS</button>
                    <button className="stor-sidebar-btn">🧹 Clean Cache</button>
                    <button className="stor-sidebar-btn">📤 Export Memory</button>
                </div>
            </div>
        </div>
    );
}
