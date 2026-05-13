import { useState, useMemo } from 'react';

// ─── Types ───

interface Project {
    id: string;
    name: string;
    path: string;
    status: 'active' | 'building' | 'dormant' | 'archived';
    stack: string[];
    branch: string;
    lastCommit: string;
    lastCommitTime: string;
    changes: { added: number; modified: number; deleted: number };
    description: string;
    linesOfCode: number;
    fileCount: number;
}

// ─── Mock Data ───

const PROJECTS: Project[] = [
    {
        id: 'joc', name: 'JOC — Joint Operations Center', path: 'packages/joc',
        status: 'active', stack: ['React', 'TypeScript', 'Vite', 'Zustand'],
        branch: 'main', lastCommit: 'feat: add Agent Comms + Synthesizer pages',
        lastCommitTime: '2 min ago', changes: { added: 6, modified: 4, deleted: 0 },
        description: 'Unified AI orchestration shell — cockpit for dispatching, monitoring, and coordinating browser-based AI agents.',
        linesOfCode: 14200, fileCount: 42,
    },
    {
        id: 'bas', name: 'Browser Automation Service', path: 'packages/browser-automation-service',
        status: 'active', stack: ['Node.js', 'Express', 'Puppeteer'],
        branch: 'main', lastCommit: 'fix: session recovery on CDP disconnect',
        lastCommitTime: '1h ago', changes: { added: 1, modified: 2, deleted: 0 },
        description: 'Headless browser orchestration — CDP integration, page management, DOM interaction, and screenshot streaming.',
        linesOfCode: 5800, fileCount: 18,
    },
    {
        id: 'lucid-mcp', name: 'Lucid MCP Server', path: 'packages/lucid-mcp',
        status: 'active', stack: ['TypeScript', 'MCP SDK', 'CMC', 'HHNI'],
        branch: 'main', lastCommit: 'feat: add send_ai_message tool',
        lastCommitTime: '30 min ago', changes: { added: 2, modified: 3, deleted: 0 },
        description: 'Consciousness Model Context Protocol server — 80+ tools for memory, goals, timeline, AI comms, and cognitive analysis.',
        linesOfCode: 22000, fileCount: 95,
    },
    {
        id: 'saios', name: 'SAIOS Kernel', path: 'packages/saios-kernel',
        status: 'building', stack: ['Rust', 'WebGPU', 'Quaternion'],
        branch: 'dev', lastCommit: 'wip: quaternion activation layer',
        lastCommitTime: '3d ago', changes: { added: 0, modified: 1, deleted: 0 },
        description: 'Self-Aware Intelligence Operating System kernel — quaternion-based neural computation substrate.',
        linesOfCode: 8400, fileCount: 37,
    },
    {
        id: 'water-sim', name: 'Multi-Regime Water', path: 'projects/water-sim',
        status: 'active', stack: ['WebGPU', 'WGSL', 'JavaScript'],
        branch: 'v2', lastCommit: 'feat: spillover mechanics + deck respawn',
        lastCommitTime: '6h ago', changes: { added: 3, modified: 5, deleted: 1 },
        description: 'GPU-accelerated fluid simulation — MPM/FLIP hybrid with heightfield control and multi-regime behavior.',
        linesOfCode: 4200, fileCount: 22,
    },
    {
        id: 'omni-builder', name: 'OmniBuilder', path: 'packages/omni-builder',
        status: 'active', stack: ['React', 'TypeScript', 'Canvas', 'Zustand'],
        branch: 'main', lastCommit: 'feat: color relationship editor + design whispers',
        lastCommitTime: '4h ago', changes: { added: 8, modified: 3, deleted: 0 },
        description: 'Visual design system editor — component catalog, color editor, responsive breakpoints, and design quality scoring.',
        linesOfCode: 18500, fileCount: 68,
    },
    {
        id: 'aim-os-docs', name: 'AIM-OS Documentation', path: 'docs',
        status: 'dormant', stack: ['Markdown'],
        branch: 'main', lastCommit: 'docs: update JOC roadmap',
        lastCommitTime: '2d ago', changes: { added: 0, modified: 1, deleted: 0 },
        description: 'Architecture documents, design specs, and operational guides for the AIM-OS ecosystem.',
        linesOfCode: 12000, fileCount: 25,
    },
];

// ─── Component ───

export function ProjectCatalogPage() {
    const [search, setSearch] = useState('');
    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [sortBy, setSortBy] = useState<'name' | 'recent' | 'loc'>('recent');
    const [view, setView] = useState<'grid' | 'list'>('grid');

    const filtered = useMemo(() => {
        let result = PROJECTS.filter(p => {
            if (search && !p.name.toLowerCase().includes(search.toLowerCase()) && !p.description.toLowerCase().includes(search.toLowerCase())) return false;
            if (filterStatus !== 'all' && p.status !== filterStatus) return false;
            return true;
        });
        if (sortBy === 'name') result.sort((a, b) => a.name.localeCompare(b.name));
        else if (sortBy === 'loc') result.sort((a, b) => b.linesOfCode - a.linesOfCode);
        return result;
    }, [search, filterStatus, sortBy]);

    const statusColors: Record<string, { bg: string; text: string }> = {
        active: { bg: 'rgba(78, 205, 196, 0.1)', text: '#4ecdc4' },
        building: { bg: 'rgba(168, 130, 255, 0.1)', text: '#a882ff' },
        dormant: { bg: 'rgba(136, 136, 136, 0.1)', text: '#888' },
        archived: { bg: 'rgba(100, 100, 100, 0.08)', text: '#666' },
    };

    const statusIcons: Record<string, string> = {
        active: '● ', building: '◑ ', dormant: '○ ', archived: '◌ ',
    };

    const fmtLoc = (n: number) => {
        if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
        return String(n);
    };

    return (
        <div className="proj-page">
            {/* ─── Header ─── */}
            <div className="proj-header">
                <div className="proj-header-left">
                    <span className="proj-title">📂 Project Catalog</span>
                    <span className="proj-subtitle">{PROJECTS.length} projects · {PROJECTS.filter(p => p.status === 'active').length} active</span>
                </div>
                <div className="proj-header-right">
                    <input className="proj-search" placeholder="Search projects..." value={search}
                        onChange={e => setSearch(e.target.value)} />
                    <select className="proj-filter-select" value={filterStatus}
                        onChange={e => setFilterStatus(e.target.value)}>
                        <option value="all">All Status</option>
                        <option value="active">Active</option>
                        <option value="building">Building</option>
                        <option value="dormant">Dormant</option>
                        <option value="archived">Archived</option>
                    </select>
                    <select className="proj-sort-select" value={sortBy}
                        onChange={e => setSortBy(e.target.value as any)}>
                        <option value="recent">Recent</option>
                        <option value="name">Name</option>
                        <option value="loc">Lines of Code</option>
                    </select>
                    <div className="proj-view-toggle">
                        <button className={`proj-view-btn ${view === 'grid' ? 'active' : ''}`} onClick={() => setView('grid')}>▦</button>
                        <button className={`proj-view-btn ${view === 'list' ? 'active' : ''}`} onClick={() => setView('list')}>☰</button>
                    </div>
                </div>
            </div>

            {/* ─── Project Grid ─── */}
            <div className={`proj-grid ${view}`}>
                {filtered.map(proj => (
                    <div key={proj.id} className={`proj-card ${proj.status}`}>
                        <div className="proj-card-header">
                            <span className="proj-card-name">{proj.name}</span>
                            <span className="proj-card-status" style={{ background: statusColors[proj.status].bg, color: statusColors[proj.status].text }}>
                                {statusIcons[proj.status]}{proj.status}
                            </span>
                        </div>
                        <p className="proj-card-desc">{proj.description}</p>

                        {/* Stack tags */}
                        <div className="proj-card-stack">
                            {proj.stack.map(s => (
                                <span key={s} className="proj-stack-tag">{s}</span>
                            ))}
                        </div>

                        {/* Git info */}
                        <div className="proj-card-git">
                            <span className="proj-git-branch">⎇ {proj.branch}</span>
                            <span className="proj-git-commit" title={proj.lastCommit}>{proj.lastCommit}</span>
                            <span className="proj-git-time">{proj.lastCommitTime}</span>
                        </div>

                        {/* Stats row */}
                        <div className="proj-card-stats">
                            <span className="proj-stat">{fmtLoc(proj.linesOfCode)} LOC</span>
                            <span className="proj-stat">{proj.fileCount} files</span>
                            {(proj.changes.added + proj.changes.modified + proj.changes.deleted > 0) && (
                                <span className="proj-stat changes">
                                    <span style={{ color: '#4ecdc4' }}>+{proj.changes.added}</span>{' '}
                                    <span style={{ color: '#ffd93d' }}>~{proj.changes.modified}</span>{' '}
                                    <span style={{ color: '#ff6b6b' }}>{proj.changes.deleted > 0 ? `-${proj.changes.deleted}` : ''}</span>
                                </span>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="proj-card-actions">
                            <button className="proj-action-btn">🔍 Context</button>
                            <button className="proj-action-btn">📋 Dispatch</button>
                            <button className="proj-action-btn">⌨ Terminal</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
