import { useState, useRef, useCallback, useEffect } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import type { editor as MonacoEditor } from 'monaco-editor';
import '../styles/code-editor.css';

// ─── Types (aligned with Sovereign Context Mapper) ───

type SyncState = 'fresh' | 'stale' | 'drift' | 'contradiction' | 'unknown';
type ParseConfidence = 'high' | 'degraded' | 'fallback';
type EnvelopeSection = 'target' | 'contract';

interface Dependency {
    path: string;
    shortName: string;
    symbols: string[];
    syncState: SyncState;
    confidence: ParseConfidence;
    lastChecked: string;
}

interface EditorFile {
    id: string;
    path: string;
    language: string;
    content: string;
    section: EnvelopeSection;
    modified: boolean;
    dependencies: Dependency[];
    parseConfidence: ParseConfidence;
}

// ─── Mock Data (today's JOC files) ───

const MOCK_FILES: EditorFile[] = [
    {
        id: 'f1',
        path: 'packages/joc/src/components/GitTimelineV2.tsx',
        language: 'typescript',
        section: 'target',
        modified: true,
        parseConfidence: 'high',
        content: `import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import '../styles/timeline-v2.css';

// ─── Core Types ───

type AgentId = 'opus' | 'aether' | 'gemini' | 'sev' | 'braden' | 'codex' | 'unknown';
type SemanticState = 'planning' | 'building' | 'testing' | 'deployed';
type CommitSize = 'small' | 'normal' | 'large' | 'milestone';

interface CommitV2 {
  hash: string;
  author: string;
  agent: AgentId;
  message: string;
  timestamp: string;
  branch: string;
  state: SemanticState;
  impact: number;
  size: CommitSize;
  isMerge: boolean;
  mission?: string;
  files?: { name: string; action: 'add' | 'modify' | 'delete' }[];
  dependsOn?: string;
}

// ─── Agent Config ───

const AGENTS: { id: AgentId; label: string; color: string }[] = [
  { id: 'opus',    label: 'OPUS',    color: '#CC7722' },
  { id: 'aether',  label: 'AETHER',  color: '#7C4DFF' },
  { id: 'gemini',  label: 'GEMINI',  color: '#4285F4' },
  { id: 'sev',     label: 'SEV',     color: '#00D4FF' },
  { id: 'braden',  label: 'BRADEN',  color: '#E8E8E8' },
  { id: 'codex',   label: 'CODEX',   color: '#4CAF50' },
];

const STATE_CONFIG: Record<SemanticState, { color: string; y: number; label: string }> = {
  planning: { color: '#7C4DFF', y: 0.15, label: 'Plan' },
  building: { color: '#00D4FF', y: 0.45, label: 'Build' },
  testing:  { color: '#4CAF50', y: 0.70, label: 'Test' },
  deployed: { color: '#FFB74D', y: 0.90, label: 'Ship' },
};

export function GitTimelineV2() {
  const [commits] = useState<CommitV2[]>([]);
  // ... component implementation
  return <div className="timeline-v2">Timeline V2</div>;
}`,
        dependencies: [
            {
                path: 'packages/joc/src/store/jocStore.ts',
                shortName: 'jocStore.ts',
                symbols: ['useJOCStore', 'BottomPanelTab', 'BottomPanelSize'],
                syncState: 'fresh',
                confidence: 'high',
                lastChecked: '12:44',
            },
            {
                path: 'packages/joc/src/styles/timeline-v2.css',
                shortName: 'timeline-v2.css',
                symbols: ['layer-agent-heat', 'commit-v2', 'flow-path'],
                syncState: 'fresh',
                confidence: 'high',
                lastChecked: '12:44',
            },
        ],
    },
    {
        id: 'f2',
        path: 'packages/joc/src/store/jocStore.ts',
        language: 'typescript',
        section: 'target',
        modified: true,
        parseConfidence: 'high',
        content: `import { create } from 'zustand';

// ─── Types ───

export type DrawerType = 'dashboard' | 'fleet' | 'missions' | 'comms';
export type BottomPanelTab = 'timeline' | 'comms' | 'output' | 'terminal';
export type BottomPanelSize = 'collapsed' | 'mid' | 'full';
export type PageType = 'dashboard' | 'session' | 'mission' | 'editor';

export interface AISession {
    id: string;
    name: string;
    provider: 'chatgpt' | 'gemini' | 'claude' | 'perplexity';
    status: 'active' | 'sleeping' | 'dead';
    health: number;
}

// ─── Store ───

interface JOCState {
    bottomPanelSize: BottomPanelSize;
    bottomActiveTab: BottomPanelTab;
    sessions: AISession[];
    toggleBottomPanel: () => void;
    setBottomPanelSize: (size: BottomPanelSize) => void;
}

export const useJOCStore = create<JOCState>((set, get) => ({
    bottomPanelSize: 'collapsed' as BottomPanelSize,
    bottomActiveTab: 'timeline',
    sessions: [],
    toggleBottomPanel: () => {
        const sizes: BottomPanelSize[] = ['collapsed', 'mid', 'full'];
        const current = sizes.indexOf(get().bottomPanelSize);
        set({ bottomPanelSize: sizes[(current + 1) % 3] });
    },
    setBottomPanelSize: (size) => set({ bottomPanelSize: size }),
}));`,
        dependencies: [
            {
                path: 'node_modules/zustand',
                shortName: 'zustand',
                symbols: ['create', 'StoreApi'],
                syncState: 'fresh',
                confidence: 'high',
                lastChecked: '12:44',
            },
        ],
    },
    {
        id: 'f3',
        path: 'packages/joc/src/components/layout/BottomBar.tsx',
        language: 'typescript',
        section: 'target',
        modified: false,
        parseConfidence: 'degraded',
        content: `import { useJOCStore } from '../../store/jocStore';
import { GitTimelineV2 } from '../GitTimelineV2';

// Bottom bar with 3 expansion states
export function BottomBar() {
    const { bottomPanelSize } = useJOCStore();
    return <div className="bottombar">Bottom Bar</div>;
}`,
        dependencies: [
            {
                path: 'packages/joc/src/store/jocStore.ts',
                shortName: 'jocStore.ts',
                symbols: ['useJOCStore', 'BottomPanelSize'],
                syncState: 'stale',
                confidence: 'high',
                lastChecked: '12:30',
            },
            {
                path: 'packages/joc/src/components/GitTimelineV2.tsx',
                shortName: 'GitTimelineV2.tsx',
                symbols: ['GitTimelineV2'],
                syncState: 'drift',
                confidence: 'degraded',
                lastChecked: '12:20',
            },
        ],
    },
    {
        id: 'f4',
        path: 'context_capsule_wire_and_mapper_v1/context_mapper_lab/src/extractor.rs',
        language: 'rust',
        section: 'contract',
        modified: false,
        parseConfidence: 'high',
        content: `/// Sovereign Context Mapper — Extractor Module
/// Deterministic syntax extraction via Tree-sitter backend

pub enum ParseConfidence {
    High,
    Degraded,
    Fallback,
}

pub struct ExtractedFile {
    pub path: std::path::PathBuf,
    pub imports: Vec<String>,
    pub contracts: String,
    pub confidence: ParseConfidence,
}

pub trait ContractExtractor {
    fn extract_file(&self, path: &std::path::Path, source: &str) -> Result<ExtractedFile, String>;
}

/// Tree-sitter backed implementation (v1 primary)
pub struct TreeSitterExtractor;

impl ContractExtractor for TreeSitterExtractor {
    fn extract_file(&self, path: &std::path::Path, source: &str) -> Result<ExtractedFile, String> {
        // Parse via tree-sitter, extract pub declarations
        // Strip bodies from exported contracts
        // Preserve semantically relevant attributes
        todo!("Implementation in progress")
    }
}`,
        dependencies: [
            {
                path: 'context_capsule_wire_and_mapper_v1/context_mapper_lab/src/types.rs',
                shortName: 'types.rs',
                symbols: ['ParseConfidence', 'ExtractedFile'],
                syncState: 'contradiction',
                confidence: 'fallback',
                lastChecked: '11:00',
            },
        ],
    },
];

// ─── Sync State Config ───

const SYNC_CONFIG: Record<SyncState, { color: string; label: string; icon: string }> = {
    fresh: { color: '#4CAF50', label: 'Fresh — synced', icon: '●' },
    stale: { color: '#FFD54F', label: 'Stale — source changed', icon: '◐' },
    drift: { color: '#FFB74D', label: 'Drift — semantic mismatch', icon: '◑' },
    contradiction: { color: '#F44336', label: 'Contradiction — incompatible facts', icon: '◉' },
    unknown: { color: '#666', label: 'Unknown — insufficient evidence', icon: '○' },
};

// ─── Component ───

export function CodeEditor() {
    const [files] = useState<EditorFile[]>(MOCK_FILES);
    const [activeFileId, setActiveFileId] = useState('f1');
    const [showDepPanel, setShowDepPanel] = useState(true);
    const [showRelationships, setShowRelationships] = useState(false);
    const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);
    const [cursorInfo, setCursorInfo] = useState({ line: 1, col: 1 });

    const activeFile = files.find(f => f.id === activeFileId) || files[0];

    // Monaco mount handler
    const handleEditorMount: OnMount = useCallback((editor, monaco) => {
        editorRef.current = editor;

        // Custom theme for AIM-OS
        monaco.editor.defineTheme('aimos-dark', {
            base: 'vs-dark',
            inherit: true,
            rules: [
                { token: 'comment', foreground: '5C6370', fontStyle: 'italic' },
                { token: 'keyword', foreground: 'C678DD' },
                { token: 'string', foreground: '98C379' },
                { token: 'number', foreground: 'D19A66' },
                { token: 'type', foreground: 'E5C07B' },
                { token: 'function', foreground: '61AFEF' },
                { token: 'variable', foreground: 'E06C75' },
            ],
            colors: {
                'editor.background': '#0B0E17',
                'editor.foreground': '#C8CCD4',
                'editor.lineHighlightBackground': '#1A1E2E',
                'editor.selectionBackground': '#264F78',
                'editorLineNumber.foreground': '#3D4556',
                'editorLineNumber.activeForeground': '#868CA0',
                'editor.inactiveSelectionBackground': '#1A2233',
                'editorIndentGuide.background1': '#1E2230',
                'editorCursor.foreground': '#00D4FF',
                'editorWidget.background': '#0F1320',
                'editorWidget.border': '#1E2536',
            },
        });
        monaco.editor.setTheme('aimos-dark');

        // Track cursor position
        editor.onDidChangeCursorPosition(e => {
            setCursorInfo({ line: e.position.lineNumber, col: e.position.column });
        });

        // Add import decorations for sync state
        addSyncDecorations(editor, monaco, activeFile);
    }, [activeFile]);

    // Add sync state decorations on import lines
    const addSyncDecorations = (
        editor: MonacoEditor.IStandaloneCodeEditor,
        monaco: typeof import('monaco-editor'),
        file: EditorFile
    ) => {
        const model = editor.getModel();
        if (!model) return;

        const decorations: MonacoEditor.IModelDeltaDecoration[] = [];
        const content = model.getValue();
        const lines = content.split('\n');

        // Find import lines and add sync state decorations
        lines.forEach((line, idx) => {
            if (line.trim().startsWith('import ') || line.trim().startsWith('use ')) {
                // Find matching dependency
                const matchedDep = file.dependencies.find(dep =>
                    line.includes(dep.shortName.replace('.tsx', '').replace('.ts', '').replace('.rs', ''))
                    || dep.symbols.some(sym => line.includes(sym))
                );

                if (matchedDep) {
                    const syncCfg = SYNC_CONFIG[matchedDep.syncState];
                    decorations.push({
                        range: new monaco.Range(idx + 1, 1, idx + 1, 1),
                        options: {
                            isWholeLine: true,
                            linesDecorationsClassName: `sync-gutter-marker ${matchedDep.syncState}`,
                            overviewRuler: {
                                color: syncCfg.color,
                                position: monaco.editor.OverviewRulerLane.Left,
                            },
                            minimap: {
                                color: syncCfg.color,
                                position: monaco.editor.MinimapPosition.Inline,
                            },
                            hoverMessage: {
                                value: `**${syncCfg.icon} ${matchedDep.syncState.toUpperCase()}** — ${matchedDep.shortName}\n\nSymbols: \`${matchedDep.symbols.join('`, `')}\`\n\nConfidence: ${matchedDep.confidence} | Last checked: ${matchedDep.lastChecked}`
                            } as any,
                        },
                    });
                }
            }
        });

        // Apply decorations
        editor.createDecorationsCollection(decorations);

        // Add read-only zone for contract files
        if (file.section === 'contract') {
            const totalLines = model.getLineCount();
            decorations.push({
                range: new monaco.Range(1, 1, totalLines, 1),
                options: {
                    isWholeLine: true,
                    className: 'contract-readonly-zone',
                    inlineClassName: 'contract-readonly-text',
                },
            });
        }
    };

    // AI Operations
    const handleCopyEnvelope = useCallback(() => {
        if (!activeFile) return;
        const envelope = {
            intent: 'Active Context Envelope for requested file.',
            parse_mode: activeFile.parseConfidence,
            target_file: {
                path: activeFile.path,
                content: activeFile.content,
            },
            dependency_index: activeFile.dependencies.map(d => ({
                path: d.path,
                symbols: d.symbols,
                sync_state: d.syncState,
                confidence: d.confidence,
            })),
            edit_rules: [
                'Modify only the target_file unless explicitly instructed.',
                'Treat outbound_contracts as read-only.',
                'Preserve public API compatibility unless the task requires otherwise.',
            ],
        };
        navigator.clipboard.writeText(JSON.stringify(envelope, null, 2));
    }, [activeFile]);

    const handleValidateDeps = useCallback(() => {
        // Mock validation — check all deps for non-fresh state
        const issues = activeFile.dependencies.filter(d => d.syncState !== 'fresh');
        if (issues.length === 0) {
            console.log('[JOC] All dependencies validated ✓');
        } else {
            console.log(`[JOC] ${issues.length} dependency issue(s):`,
                issues.map(i => `${i.shortName}: ${i.syncState}`));
        }
    }, [activeFile]);

    return (
        <div className="code-editor-page">
            {/* File Tabs */}
            <div className="code-editor-tab-bar">
                {files.map(f => (
                    <div
                        key={f.id}
                        className={`code-editor-tab ${activeFileId === f.id ? 'active' : ''}`}
                        onClick={() => setActiveFileId(f.id)}
                    >
                        <span style={{ opacity: 0.5, fontSize: '10px' }}>
                            {f.section === 'contract' ? '🔒' : '✏️'}
                        </span>
                        <span>{f.path.split('/').pop()}</span>
                        {f.modified && <span className="code-editor-tab-modified" />}
                        <span className="code-editor-tab-close">✕</span>
                    </div>
                ))}
            </div>

            {/* Toolbar */}
            <div className="code-editor-toolbar">
                <div className="code-editor-toolbar-section">
                    <span style={{ fontSize: '9px', color: 'var(--text-hint)', textTransform: 'uppercase' as const, letterSpacing: '0.5px' }}>
                        {activeFile.section === 'target' ? '⬤ TARGET FILE' : '◎ READ-ONLY CONTRACT'}
                    </span>
                </div>

                <div className="code-editor-toolbar-divider" />

                <div className="code-editor-toolbar-section">
                    <span style={{ fontSize: '9px', color: 'var(--text-hint)' }}>{activeFile.language}</span>
                </div>

                <div className="code-editor-toolbar-divider" />

                {/* Parse confidence indicator */}
                <div className={`parse-confidence-banner ${activeFile.parseConfidence}`} style={{ border: 'none', padding: '0 4px' }}>
                    <span className="parse-confidence-dot" />
                    <span style={{ fontSize: '9px' }}>
                        Parse: {activeFile.parseConfidence.toUpperCase()}
                    </span>
                </div>

                <div style={{ flex: 1 }} />

                <span style={{ fontSize: '9px', color: 'var(--text-hint)', fontFamily: 'var(--font-mono)' }}>
                    Ln {cursorInfo.line}, Col {cursorInfo.col}
                </span>
            </div>

            {/* Main Editor + Dependency Panel */}
            <div className="code-editor-main">
                <div className="code-editor-monaco">
                    <Editor
                        height="100%"
                        language={activeFile.language === 'typescript' ? 'typescript' : 'rust'}
                        value={activeFile.content}
                        theme="vs-dark"
                        onMount={handleEditorMount}
                        options={{
                            fontSize: 13,
                            fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
                            fontLigatures: true,
                            minimap: { enabled: true, scale: 1 },
                            lineNumbers: 'on',
                            glyphMargin: true,
                            folding: true,
                            lineDecorationsWidth: 16,
                            renderLineHighlight: 'all',
                            scrollBeyondLastLine: false,
                            smoothScrolling: true,
                            cursorBlinking: 'smooth',
                            cursorSmoothCaretAnimation: 'on',
                            renderWhitespace: 'selection',
                            bracketPairColorization: { enabled: true },
                            guides: { bracketPairs: true, indentation: true },
                            padding: { top: 8 },
                            readOnly: activeFile.section === 'contract',
                        }}
                    />
                </div>

                {/* Dependency Panel */}
                {showDepPanel && (
                    <div className="code-editor-dep-panel">
                        <div className="dep-panel-header">
                            <span className="dep-panel-title">Dependencies</span>
                            <button
                                className="bottombar-expand-btn"
                                onClick={() => setShowDepPanel(false)}
                                style={{ padding: '2px' }}
                            >
                                ✕
                            </button>
                        </div>

                        {/* Parse Confidence */}
                        <div className={`parse-confidence-banner ${activeFile.parseConfidence}`}>
                            <span className="parse-confidence-dot" />
                            <span>Context Mapper: {activeFile.parseConfidence}</span>
                        </div>

                        <div className="dep-panel-content">
                            {activeFile.dependencies.map(dep => (
                                <div key={dep.path} className="dep-item">
                                    <span
                                        className={`dep-item-sync ${dep.syncState}`}
                                        title={SYNC_CONFIG[dep.syncState].label}
                                    />
                                    <div className="dep-item-info">
                                        <div className="dep-item-name">{dep.shortName}</div>
                                        <div className="dep-item-meta">
                                            {SYNC_CONFIG[dep.syncState].icon} {dep.syncState} • {dep.confidence} • {dep.lastChecked}
                                        </div>
                                        <div className="dep-item-symbols">
                                            {dep.symbols.map(s => (
                                                <span key={s} className="dep-item-symbol">{s}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {activeFile.dependencies.length === 0 && (
                                <div style={{ padding: '16px', color: 'var(--text-hint)', fontSize: '10px', textAlign: 'center' as const }}>
                                    No dependencies detected
                                </div>
                            )}
                        </div>

                        {/* Sync Advisory Summary */}
                        <div style={{
                            padding: '6px 10px',
                            borderTop: '1px solid var(--border-subtle)',
                            fontSize: '9px',
                            color: 'var(--text-hint)',
                        }}>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <span>
                                    <span style={{ color: SYNC_CONFIG.fresh.color }}>●</span> {activeFile.dependencies.filter(d => d.syncState === 'fresh').length}
                                </span>
                                <span>
                                    <span style={{ color: SYNC_CONFIG.stale.color }}>●</span> {activeFile.dependencies.filter(d => d.syncState === 'stale').length}
                                </span>
                                <span>
                                    <span style={{ color: SYNC_CONFIG.drift.color }}>●</span> {activeFile.dependencies.filter(d => d.syncState === 'drift').length}
                                </span>
                                <span>
                                    <span style={{ color: SYNC_CONFIG.contradiction.color }}>●</span> {activeFile.dependencies.filter(d => d.syncState === 'contradiction').length}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* AI Operations Bar */}
            <div className="ai-ops-bar">
                <button className="ai-ops-btn" onClick={handleCopyEnvelope} title="Copy file + dependencies as structured envelope for AI consumption">
                    <span className="ai-ops-btn-icon">📋</span> Copy Envelope
                </button>
                <button className="ai-ops-btn" title="Paste structured code from AI with automatic validation">
                    <span className="ai-ops-btn-icon">📥</span> Paste from AI
                </button>
                <button className={`ai-ops-btn ${showRelationships ? 'active' : ''}`} onClick={() => setShowRelationships(!showRelationships)} title="Show import/export relationship lines">
                    <span className="ai-ops-btn-icon">🔗</span> Relationships
                </button>
                <button className="ai-ops-btn" onClick={handleValidateDeps} title="Validate all dependency sync states">
                    <span className="ai-ops-btn-icon">✓</span> Validate Deps
                </button>
                <button className={`ai-ops-btn ${showDepPanel ? 'active' : ''}`} onClick={() => setShowDepPanel(!showDepPanel)} title="Toggle dependency panel">
                    <span className="ai-ops-btn-icon">◫</span> Dep Panel
                </button>

                <div className="ai-ops-spacer" />

                <div className="ai-ops-status">
                    <span style={{ color: activeFile.section === 'contract' ? 'var(--warning)' : 'var(--success)' }}>
                        {activeFile.section === 'target' ? '● EDIT' : '◎ READ-ONLY'}
                    </span>
                    <span>•</span>
                    <span>{activeFile.dependencies.length} deps</span>
                    <span>•</span>
                    <span style={{
                        color: activeFile.parseConfidence === 'high' ? 'var(--success)'
                            : activeFile.parseConfidence === 'degraded' ? 'var(--warning)'
                                : 'var(--danger)'
                    }}>
                        {activeFile.parseConfidence}
                    </span>
                </div>
            </div>
        </div>
    );
}
