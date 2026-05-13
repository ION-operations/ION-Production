import { useState, useMemo } from 'react';
import { useAIMOS } from '../hooks/useAIMOS';

// ─── Types ───

interface ProjectFile {
    name: string;
    path: string;
    size: number;
    tokens: number;
    type: 'file' | 'dir';
    children?: ProjectFile[];
    language?: string;
    selected?: boolean;
}

interface TokenBudget {
    provider: string;
    maxTokens: number;
    used: number;
    available: number;
}

// ─── Mock Project Tree ───

const MOCK_FILES: ProjectFile[] = [
    {
        name: 'packages', path: '/packages', size: 0, tokens: 0, type: 'dir', children: [
            {
                name: 'joc', path: '/packages/joc', size: 0, tokens: 0, type: 'dir', children: [
                    { name: 'App.tsx', path: '/packages/joc/src/App.tsx', size: 2112, tokens: 520, type: 'file', language: 'tsx' },
                    { name: 'jocStore.ts', path: '/packages/joc/src/store/jocStore.ts', size: 8416, tokens: 2100, type: 'file', language: 'ts' },
                    { name: 'sessionStore.ts', path: '/packages/joc/src/store/sessionStore.ts', size: 14600, tokens: 3650, type: 'file', language: 'ts' },
                    { name: 'mcpClient.ts', path: '/packages/joc/src/services/mcpClient.ts', size: 4893, tokens: 1220, type: 'file', language: 'ts' },
                    { name: 'aiDrivers.ts', path: '/packages/joc/src/drivers/aiDrivers.ts', size: 17213, tokens: 4300, type: 'file', language: 'ts' },
                    { name: 'useAIMOS.ts', path: '/packages/joc/src/hooks/useAIMOS.ts', size: 8338, tokens: 2080, type: 'file', language: 'ts' },
                    { name: 'DashboardPage.tsx', path: '/packages/joc/src/pages/DashboardPage.tsx', size: 19198, tokens: 4800, type: 'file', language: 'tsx' },
                    { name: 'SessionPage.tsx', path: '/packages/joc/src/pages/SessionPage.tsx', size: 12000, tokens: 3000, type: 'file', language: 'tsx' },
                ]
            },
            {
                name: 'browser-automation-service', path: '/packages/browser-automation-service', size: 0, tokens: 0, type: 'dir', children: [
                    { name: 'server.ts', path: '/packages/browser-automation-service/src/server.ts', size: 3200, tokens: 800, type: 'file', language: 'ts' },
                    { name: 'automation.ts', path: '/packages/browser-automation-service/src/api/automation.ts', size: 5716, tokens: 1430, type: 'file', language: 'ts' },
                    { name: 'scriptEngine.ts', path: '/packages/browser-automation-service/src/services/scriptEngine.ts', size: 8900, tokens: 2225, type: 'file', language: 'ts' },
                ]
            },
        ]
    },
    {
        name: 'docs', path: '/docs', size: 0, tokens: 0, type: 'dir', children: [
            { name: 'JOC_GOALS_AND_ROADMAP.md', path: '/docs/OPUS1_JOC_GOALS_AND_ROADMAP.md', size: 7764, tokens: 1941, type: 'file', language: 'md' },
            { name: 'JOC_ARCHITECTURE.md', path: '/docs/OPUS1_JOC_ARCHITECTURE.md', size: 12000, tokens: 3000, type: 'file', language: 'md' },
            { name: 'JOC_MASTER_VISION.md', path: '/docs/OPUS1_JOC_MASTER_VISION.md', size: 15000, tokens: 3750, type: 'file', language: 'md' },
        ]
    },
];

const BUDGETS: TokenBudget[] = [
    { provider: 'ChatGPT (GPT-4o)', maxTokens: 128000, used: 0, available: 128000 },
    { provider: 'Gemini 2.5 Pro', maxTokens: 1000000, used: 0, available: 1000000 },
    { provider: 'Claude Opus', maxTokens: 200000, used: 0, available: 200000 },
    { provider: 'Perplexity Pro', maxTokens: 127000, used: 0, available: 127000 },
];

// ─── Component ───

export function AutoContextPage() {
    const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
    const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set(['/packages', '/packages/joc', '/docs']));
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState<'name' | 'size' | 'tokens'>('name');

    const aimos = useAIMOS({ pollDomains: ['goals'] });

    // Calculate totals
    const totalTokens = useMemo(() => {
        let total = 0;
        const countTokens = (files: ProjectFile[]) => {
            files.forEach(f => {
                if (f.type === 'file' && selectedFiles.has(f.path)) total += f.tokens;
                if (f.children) countTokens(f.children);
            });
        };
        countTokens(MOCK_FILES);
        return total;
    }, [selectedFiles]);

    const totalSize = useMemo(() => {
        let total = 0;
        const countSize = (files: ProjectFile[]) => {
            files.forEach(f => {
                if (f.type === 'file' && selectedFiles.has(f.path)) total += f.size;
                if (f.children) countSize(f.children);
            });
        };
        countSize(MOCK_FILES);
        return total;
    }, [selectedFiles]);

    const budgets = BUDGETS.map(b => ({
        ...b,
        used: totalTokens,
        available: b.maxTokens - totalTokens,
    }));

    const toggleFile = (path: string) => {
        setSelectedFiles(prev => {
            const next = new Set(prev);
            next.has(path) ? next.delete(path) : next.add(path);
            return next;
        });
    };

    const toggleDir = (path: string) => {
        setExpandedDirs(prev => {
            const next = new Set(prev);
            next.has(path) ? next.delete(path) : next.add(path);
            return next;
        });
    };

    const selectAll = (files: ProjectFile[]) => {
        const paths: string[] = [];
        const collect = (fs: ProjectFile[]) => {
            fs.forEach(f => {
                if (f.type === 'file') paths.push(f.path);
                if (f.children) collect(f.children);
            });
        };
        collect(files);
        setSelectedFiles(new Set(paths));
    };

    const clearAll = () => setSelectedFiles(new Set());

    const fmtBytes = (b: number) => {
        if (b >= 1024 * 1024) return `${(b / 1024 / 1024).toFixed(1)} MB`;
        if (b >= 1024) return `${(b / 1024).toFixed(1)} KB`;
        return `${b} B`;
    };

    const fmtTokens = (t: number) => {
        if (t >= 1000000) return `${(t / 1000000).toFixed(1)}M`;
        if (t >= 1000) return `${(t / 1000).toFixed(1)}K`;
        return String(t);
    };

    const langColor: Record<string, string> = {
        tsx: '#2f74c0', ts: '#3178c6', md: '#083fa1', js: '#f7df1e', css: '#264de4',
    };

    const renderTree = (files: ProjectFile[], depth = 0): JSX.Element[] => {
        return files
            .filter(f => !searchQuery || f.name.toLowerCase().includes(searchQuery.toLowerCase()) || (f.children && f.children.length > 0))
            .flatMap(f => {
                const items: JSX.Element[] = [];
                if (f.type === 'dir') {
                    const isExpanded = expandedDirs.has(f.path);
                    items.push(
                        <div key={f.path} className="ctx-tree-item dir" style={{ paddingLeft: `${12 + depth * 16}px` }}
                            onClick={() => toggleDir(f.path)}>
                            <span className="ctx-tree-arrow">{isExpanded ? '▾' : '▸'}</span>
                            <span className="ctx-tree-icon">📁</span>
                            <span className="ctx-tree-name">{f.name}</span>
                        </div>
                    );
                    if (isExpanded && f.children) {
                        items.push(...renderTree(f.children, depth + 1));
                    }
                } else {
                    const isSelected = selectedFiles.has(f.path);
                    items.push(
                        <div key={f.path} className={`ctx-tree-item file ${isSelected ? 'selected' : ''}`}
                            style={{ paddingLeft: `${12 + depth * 16}px` }}
                            onClick={() => toggleFile(f.path)}>
                            <span className="ctx-tree-check">{isSelected ? '☑' : '☐'}</span>
                            <span className="ctx-tree-lang-dot" style={{ background: langColor[f.language || ''] || '#888' }} />
                            <span className="ctx-tree-name">{f.name}</span>
                            <span className="ctx-tree-spacer" />
                            <span className="ctx-tree-tokens">{fmtTokens(f.tokens)} tok</span>
                            <span className="ctx-tree-size">{fmtBytes(f.size)}</span>
                        </div>
                    );
                }
                return items;
            });
    };

    return (
        <div className="ctx-page">
            {/* ─── Header ─── */}
            <div className="ctx-header">
                <div className="ctx-header-left">
                    <span className="ctx-title">🔍 Auto-Context Engine</span>
                    <span className="ctx-subtitle">{selectedFiles.size} files · {fmtTokens(totalTokens)} tokens · {fmtBytes(totalSize)}</span>
                </div>
                <div className="ctx-header-right">
                    <button className="ctx-action-btn" onClick={() => selectAll(MOCK_FILES)}>Select All</button>
                    <button className="ctx-action-btn" onClick={clearAll}>Clear</button>
                    <button className="ctx-attach-btn">📎 Attach to Mission</button>
                </div>
            </div>

            <div className="ctx-body">
                {/* ─── File Tree ─── */}
                <div className="ctx-tree-panel">
                    <div className="ctx-tree-toolbar">
                        <input
                            className="ctx-search-input"
                            placeholder="Search files..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                        />
                        <select className="ctx-sort-select" value={sortBy} onChange={e => setSortBy(e.target.value as any)}>
                            <option value="name">Name</option>
                            <option value="tokens">Tokens</option>
                            <option value="size">Size</option>
                        </select>
                    </div>
                    <div className="ctx-tree-list">
                        {renderTree(MOCK_FILES)}
                    </div>
                </div>

                {/* ─── Budget Panel ─── */}
                <div className="ctx-budget-panel">
                    <div className="ctx-budget-title">Token Budget by Provider</div>
                    {budgets.map(b => {
                        const pct = Math.min((b.used / b.maxTokens) * 100, 100);
                        const color = pct > 90 ? '#ff6b6b' : pct > 70 ? '#ffd93d' : '#4ecdc4';
                        return (
                            <div key={b.provider} className="ctx-budget-row">
                                <div className="ctx-budget-label">
                                    <span className="ctx-budget-provider">{b.provider}</span>
                                    <span className="ctx-budget-numbers" style={{ color }}>
                                        {fmtTokens(b.used)} / {fmtTokens(b.maxTokens)}
                                    </span>
                                </div>
                                <div className="ctx-budget-bar">
                                    <div className="ctx-budget-bar-fill" style={{ width: `${pct}%`, background: color }} />
                                </div>
                                <div className="ctx-budget-avail">
                                    {fmtTokens(b.available)} available
                                </div>
                            </div>
                        );
                    })}

                    {/* Selected files summary */}
                    <div className="ctx-selected-title">Selected Files ({selectedFiles.size})</div>
                    <div className="ctx-selected-list">
                        {Array.from(selectedFiles).map(path => {
                            const name = path.split('/').pop() || path;
                            return (
                                <div key={path} className="ctx-selected-item">
                                    <span className="ctx-selected-name">{name}</span>
                                    <button className="ctx-selected-remove" onClick={() => toggleFile(path)}>✕</button>
                                </div>
                            );
                        })}
                        {selectedFiles.size === 0 && (
                            <div className="ctx-selected-empty">Click files to add to context</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
