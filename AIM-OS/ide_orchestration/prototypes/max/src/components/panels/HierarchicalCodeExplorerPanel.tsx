// Hierarchical Code Explorer Panel - Max V2
// 3 Variants: Tree-based, Graph-based, HHNI-powered
// Progressive disclosure, connection visualization, semantic navigation

import React, { useState, useMemo } from 'react';
import { ChevronRight, File, FolderOpen, Network, Brain, Search, Filter } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { PanelLoading } from '../Loading/Loading';
import './HierarchicalCodeExplorerPanel.css';

export type ExplorerVariant = 'tree' | 'graph' | 'hhni';

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  exports?: string[];
  imports?: string[];
  sections?: CodeSection[];
  connections?: FileConnection[];
  semantic?: SemanticSection[];
  aimosConnections?: {
    cmc?: string[];
    vif?: { confidence: number };
    seg?: string[];
    hhni?: string[];
  };
}

export interface CodeSection {
  name: string;
  lines: [number, number];
  type?: string;
  semantic?: string;
  dependencies?: string[];
  aimosIntegration?: string[];
  confidence?: number;
}

export interface FileConnection {
  type: 'imports' | 'exports' | 'uses' | 'imported_by';
  target: string;
  direction: 'in' | 'out';
}

export interface SemanticSection {
  name: string;
  type: string;
  semantic: string;
  lines: [number, number];
  dependencies: string[];
  aimosIntegration: string[];
  confidence: number;
}

export const HierarchicalCodeExplorerPanel: React.FC = () => {
  const { hhni, loading, errors } = useAIMOS();
  const [variant, setVariant] = useState<ExplorerVariant>('tree');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  // Mock codebase structure (will be replaced with real file system + HHNI data)
  const codebase: FileNode = useMemo(() => ({
    name: 'AIM-OS',
    path: '',
    type: 'folder',
    children: [
      {
        name: 'packages',
        path: 'packages',
        type: 'folder',
        children: [
          {
            name: 'ide_chat_app',
            path: 'packages/ide_chat_app',
            type: 'folder',
            children: [
              {
                name: 'src',
                path: 'packages/ide_chat_app/src',
                type: 'folder',
                children: [
                  {
                    name: 'components',
                    path: 'packages/ide_chat_app/src/components',
                    type: 'folder',
                    children: [
                      {
                        name: 'IDELayout.tsx',
                        path: 'packages/ide_chat_app/src/components/IDELayout.tsx',
                        type: 'file',
                        exports: ['AetherIDELayout', 'PanelGroup'],
                        imports: ['react', 'react-resizable-panels', 'lucide-react'],
                        sections: [
                          { name: 'Top Bar', lines: [1, 50], type: 'ui_component' },
                          { name: 'Left Drawer', lines: [51, 150], type: 'navigation' },
                          { name: 'Main Content', lines: [151, 300], type: 'workspace' },
                          { name: 'Right Drawer', lines: [301, 450], type: 'panel_dock' },
                          { name: 'Bottom Drawer', lines: [451, 603], type: 'utility' },
                        ],
                        connections: [
                          { type: 'imports', target: 'react', direction: 'in' },
                          { type: 'imports', target: 'react-resizable-panels', direction: 'in' },
                          { type: 'exports', target: 'AetherIDELayout', direction: 'out' },
                          { type: 'uses', target: 'FileExplorerPanel', direction: 'out' },
                        ],
                        semantic: [
                          {
                            name: 'Top Bar',
                            type: 'ui_component',
                            semantic: 'Header navigation and status display',
                            lines: [1, 50],
                            dependencies: ['react', 'lucide-react'],
                            aimosIntegration: ['VIF: confidence display', 'CAS: consciousness status'],
                            confidence: 0.95,
                          },
                          {
                            name: 'Left Drawer',
                            type: 'navigation',
                            semantic: 'Primary navigation panel with system access',
                            lines: [51, 150],
                            dependencies: ['react-resizable-panels'],
                            aimosIntegration: ['CMC: file explorer', 'HHNI: component library'],
                            confidence: 0.92,
                          },
                          {
                            name: 'Main Content',
                            type: 'workspace',
                            semantic: 'Primary work area with multiple zones',
                            lines: [151, 300],
                            dependencies: ['react-resizable-panels'],
                            aimosIntegration: ['APOE: orchestrator', 'CAS: consciousness visualization'],
                            confidence: 0.88,
                          },
                        ],
                        aimosConnections: {
                          cmc: ['atom_123', 'atom_456'],
                          vif: { confidence: 0.92 },
                          seg: ['evidence_node_1', 'evidence_node_2'],
                          hhni: ['concept_layout', 'concept_panel'],
                        },
                      },
                      {
                        name: 'FileExplorerPanel.tsx',
                        path: 'packages/ide_chat_app/src/components/FileExplorerPanel.tsx',
                        type: 'file',
                        exports: ['FileExplorerPanel'],
                        imports: ['react', 'lucide-react'],
                        connections: [
                          { type: 'imported_by', target: 'IDELayout.tsx', direction: 'in' },
                          { type: 'uses', target: 'mockFileTree', direction: 'out' },
                        ],
                        aimosConnections: {
                          cmc: ['atom_789'],
                          vif: { confidence: 0.90 },
                        },
                      },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  }), []);

  const toggleExpand = (path: string) => {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpanded(newExpanded);
  };

  const toggleSection = (filePath: string, sectionName: string) => {
    const key = `${filePath}:${sectionName}`;
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedSections(newExpanded);
  };

  // V1: Tree-based Progressive Disclosure
  const renderTree = (node: FileNode, depth: number = 0): React.ReactNode => {
    if (!node.children && node.type === 'file') {
      const isExpanded = expanded.has(node.path);
      return (
        <div key={node.path} className="file-node">
          <div
            className={`file-node-header ${selectedFile === node.path ? 'file-node-selected' : ''}`}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => {
              toggleExpand(node.path);
              setSelectedFile(node.path);
            }}
            role="button"
            tabIndex={0}
            aria-label={`File: ${node.name}`}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleExpand(node.path);
                setSelectedFile(node.path);
              }
            }}
          >
            <ChevronRight className={`chevron-icon ${isExpanded ? 'chevron-expanded' : ''}`} />
            <File className="file-icon" />
            <span className="file-name">{node.name}</span>
          </div>
          {isExpanded && (
            <div className="file-details" style={{ paddingLeft: `${(depth + 1) * 16 + 8}px` }}>
              {node.exports && (
                <div className="file-meta">
                  <span className="meta-label">Exports:</span>
                  <span className="meta-value">{node.exports.join(', ')}</span>
                </div>
              )}
              {node.imports && (
                <div className="file-meta">
                  <span className="meta-label">Imports:</span>
                  <span className="meta-value">{node.imports.join(', ')}</span>
                </div>
              )}
              {node.sections && (
                <div className="file-sections">
                  <div className="sections-header">Sections:</div>
                  {node.sections.map((section) => {
                    const sectionKey = `${node.path}:${section.name}`;
                    const isSectionExpanded = expandedSections.has(sectionKey);
                    return (
                      <div key={section.name} className="section-item">
                        <div
                          className="section-header"
                          onClick={() => toggleSection(node.path, section.name)}
                          role="button"
                          tabIndex={0}
                          aria-label={`Section: ${section.name}`}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              toggleSection(node.path, section.name);
                            }
                          }}
                        >
                          <ChevronRight className={`chevron-icon ${isSectionExpanded ? 'chevron-expanded' : ''}`} />
                          <span className="section-name">{section.name}</span>
                          <span className="section-lines">lines {section.lines[0]}-{section.lines[1]}</span>
                        </div>
                        {isSectionExpanded && (
                          <div className="section-preview">
                            <div className="section-preview-text">// Section code preview...</div>
                            <div className="section-preview-hint">Click "Full Expand" to see complete code</div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
              {node.aimosConnections && (
                <div className="aimos-connections">
                  <div className="aimos-header">AIM-OS:</div>
                  {node.aimosConnections.cmc && (
                    <div className="aimos-item">
                      <span className="aimos-label">CMC:</span>
                      <span className="aimos-value">{node.aimosConnections.cmc.join(', ')}</span>
                    </div>
                  )}
                  {node.aimosConnections.vif && (
                    <div className="aimos-item">
                      <span className="aimos-label">VIF:</span>
                      <span className="aimos-value">Conf {(node.aimosConnections.vif.confidence * 100).toFixed(0)}%</span>
                    </div>
                  )}
                  {node.aimosConnections.seg && (
                    <div className="aimos-item">
                      <span className="aimos-label">SEG:</span>
                      <span className="aimos-value">{node.aimosConnections.seg.join(', ')}</span>
                    </div>
                  )}
                  {node.aimosConnections.hhni && (
                    <div className="aimos-item">
                      <span className="aimos-label">HHNI:</span>
                      <span className="aimos-value">{node.aimosConnections.hhni.join(', ')}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    // Folder
    const isExpanded = expanded.has(node.path);
    return (
      <div key={node.path} className="folder-node">
        <div
          className="folder-node-header"
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => toggleExpand(node.path)}
          role="button"
          tabIndex={0}
          aria-label={`Folder: ${node.name}`}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              toggleExpand(node.path);
            }
          }}
        >
          <ChevronRight className={`chevron-icon ${isExpanded ? 'chevron-expanded' : ''}`} />
          <FolderOpen className="folder-icon" />
          <span className="folder-name">{node.name}</span>
        </div>
        {isExpanded && node.children && (
          <div className="folder-children">
            {node.children.map((child) => renderTree(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  // V2: Graph-based Connection Visualization
  const renderGraph = (node: FileNode): React.ReactNode => {
    const files: FileNode[] = [];
    const collectFiles = (n: FileNode) => {
      if (n.type === 'file') {
        files.push(n);
      }
      if (n.children) {
        n.children.forEach(collectFiles);
      }
    };
    collectFiles(node);

    return (
      <div className="graph-view">
        {files.map((file) => (
          <div
            key={file.path}
            className={`graph-file-card ${selectedFile === file.path ? 'graph-file-selected' : ''}`}
            onClick={() => setSelectedFile(file.path)}
            role="button"
            tabIndex={0}
            aria-label={`File: ${file.name}`}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setSelectedFile(file.path);
              }
            }}
          >
            <div className="graph-file-header">
              <File className="graph-file-icon" />
              <span className="graph-file-name">{file.name}</span>
            </div>
            {file.sections && (
              <div className="graph-file-meta">
                <span>{file.sections.length} sections</span>
                {file.aimosConnections && (
                  <>
                    <span>•</span>
                    <span>
                      {Object.keys(file.aimosConnections).length} AIM-OS connections
                    </span>
                  </>
                )}
              </div>
            )}
            {file.connections && file.connections.length > 0 && (
              <div className="graph-connections">
                <div className="connections-header">Connections:</div>
                <div className="connections-list">
                  {file.connections.map((conn, idx) => (
                    <div key={idx} className="connection-item">
                      <span className={`connection-badge connection-${conn.direction}`}>
                        {conn.type}
                      </span>
                      <span className="connection-target">{conn.target}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // V3: HHNI-powered Semantic Explorer
  const renderHHNI = (node: FileNode): React.ReactNode => {
    const files: FileNode[] = [];
    const collectFiles = (n: FileNode) => {
      if (n.type === 'file' && n.semantic) {
        files.push(n);
      }
      if (n.children) {
        n.children.forEach(collectFiles);
      }
    };
    collectFiles(node);

    return (
      <div className="hhni-view">
        {files.map((file) => (
          <div key={file.path} className="hhni-file-card">
            <div className="hhni-file-header">
              <File className="hhni-file-icon" />
              <div>
                <div className="hhni-file-name">{file.name}</div>
                <div className="hhni-file-subtitle">Semantic code structure analysis</div>
              </div>
            </div>
            {file.semantic && (
              <div className="hhni-sections">
                {file.semantic.map((section) => (
                  <div key={section.name} className="hhni-section-card">
                    <div className="hhni-section-header">
                      <span className="hhni-section-name">{section.name}</span>
                      <span className="hhni-section-confidence">
                        Conf: {(section.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="hhni-section-semantic">{section.semantic}</div>
                    <div className="hhni-section-meta">
                      <span className={`hhni-section-type hhni-type-${section.type}`}>
                        {section.type}
                      </span>
                      <span className="hhni-section-lines">lines {section.lines[0]}-{section.lines[1]}</span>
                    </div>
                    {section.dependencies && section.dependencies.length > 0 && (
                      <div className="hhni-dependencies">
                        <div className="hhni-dependencies-header">Dependencies:</div>
                        <div className="hhni-dependencies-list">
                          {section.dependencies.map((dep) => (
                            <span key={dep} className="hhni-dependency-badge">
                              {dep}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {section.aimosIntegration && section.aimosIntegration.length > 0 && (
                      <div className="hhni-integration">
                        <div className="hhni-integration-header">AIM-OS Integration:</div>
                        <div className="hhni-integration-list">
                          {section.aimosIntegration.map((integration, idx) => (
                            <div key={idx} className="hhni-integration-item">{integration}</div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  if (loading.hhni) {
    return <PanelLoading message="Loading Hierarchical Code Explorer..." />;
  }

  if (errors.hhni) {
    return (
      <div className="code-explorer-error" role="alert">
        <p>Error loading Hierarchical Code Explorer: {errors.hhni.message}</p>
      </div>
    );
  }

  return (
    <div className="hierarchical-code-explorer" role="region" aria-label="Hierarchical Code Explorer">
      {/* Header */}
      <div className="code-explorer-header">
        <div className="code-explorer-header-top">
          <div className="code-explorer-title">
            {variant === 'tree' && <FolderOpen className="code-explorer-icon" />}
            {variant === 'graph' && <Network className="code-explorer-icon" />}
            {variant === 'hhni' && <Brain className="code-explorer-icon" />}
            <div>
              <h3 className="code-explorer-title-text">Hierarchical Code Explorer</h3>
              <p className="code-explorer-subtitle">
                {variant === 'tree' && 'Tree-Based • Progressive Disclosure • AIM-OS Integrated'}
                {variant === 'graph' && 'Graph-Based • Connection Visualization • Relationship Mapping'}
                {variant === 'hhni' && 'HHNI-Powered • Semantic Sections • Intent-Based Navigation'}
              </p>
            </div>
          </div>
        </div>

        {/* Variant Selector */}
        <div className="variant-selector">
          <button
            onClick={() => setVariant('tree')}
            className={`variant-button ${variant === 'tree' ? 'variant-button-active' : ''}`}
            aria-pressed={variant === 'tree'}
            aria-label="Tree view variant"
          >
            <FolderOpen className="variant-icon" />
            <span>Tree</span>
          </button>
          <button
            onClick={() => setVariant('graph')}
            className={`variant-button ${variant === 'graph' ? 'variant-button-active' : ''}`}
            aria-pressed={variant === 'graph'}
            aria-label="Graph view variant"
          >
            <Network className="variant-icon" />
            <span>Graph</span>
          </button>
          <button
            onClick={() => setVariant('hhni')}
            className={`variant-button ${variant === 'hhni' ? 'variant-button-active' : ''}`}
            aria-pressed={variant === 'hhni'}
            aria-label="HHNI semantic view variant"
          >
            <Brain className="variant-icon" />
            <span>HHNI</span>
          </button>
        </div>

        {/* Search */}
        <div className="code-explorer-search">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search files, sections, or concepts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
            aria-label="Search code explorer"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="search-clear"
              aria-label="Clear search"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="code-explorer-content">
        {variant === 'tree' && renderTree(codebase)}
        {variant === 'graph' && renderGraph(codebase)}
        {variant === 'hhni' && renderHHNI(codebase)}
      </div>
    </div>
  );
};

