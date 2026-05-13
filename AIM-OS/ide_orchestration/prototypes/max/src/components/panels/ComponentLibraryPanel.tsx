// Component Library Panel - Max V2
// Reusable component library with AIM-OS integration (HHNI, VIF, SEG)

import React, { useState, useMemo } from 'react';
import { Package, Code, FileText, Zap, Search, Filter, Eye, Copy, ExternalLink } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './ComponentLibraryPanel.css';

export type ComponentCategory = 'all' | 'layout' | 'panel' | 'ui' | 'hook' | 'utility' | 'visualization';

export interface Component {
  id: string;
  name: string;
  category: ComponentCategory;
  description: string;
  usage: string;
  filePath: string;
  tags: string[];
  confidence?: number;
  usageCount?: number;
  hhniPath?: string[];
  semanticScore?: number;
  dependencies?: string[];
  examples?: string[];
}

export const ComponentLibraryPanel: React.FC = () => {
  const { hhni, vif, loading, errors } = useAIMOS();
  const [selectedCategory, setSelectedCategory] = useState<ComponentCategory>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

  // Mock components with AIM-OS integration
  const components: Component[] = useMemo(() => [
    {
      id: 'comp_1',
      name: 'TerminalPanel',
      category: 'panel',
      description: 'Enhanced terminal panel with multi-session support, command execution, and AIM-OS integration',
      usage: "import { TerminalPanel } from '../panels/TerminalPanel';",
      filePath: 'src/components/panels/TerminalPanel.tsx',
      tags: ['terminal', 'command', 'cmc', 'vif', 'seg'],
      confidence: 0.95,
      usageCount: 1,
      hhniPath: ['IDE', 'Components', 'Panels', 'TerminalPanel'],
      semanticScore: 0.95,
      dependencies: ['useAIMOS', 'ConfidenceIndicator', 'ContradictionAlert'],
      examples: [
        '<TerminalPanel />',
        '// Multi-session terminal with AIM-OS integration',
      ],
    },
    {
      id: 'comp_2',
      name: 'GitPanel',
      category: 'panel',
      description: 'Version control panel with status, commits, branches, and history tabs',
      usage: "import { GitPanel } from '../panels/GitPanel';",
      filePath: 'src/components/panels/GitPanel.tsx',
      tags: ['git', 'version-control', 'cmc', 'vif', 'seg'],
      confidence: 0.93,
      usageCount: 1,
      hhniPath: ['IDE', 'Components', 'Panels', 'GitPanel'],
      semanticScore: 0.93,
      dependencies: ['useAIMOS', 'ConfidenceIndicator', 'EvidenceTrailDisplay'],
      examples: [
        '<GitPanel />',
        '// Git integration with AIM-OS evidence trails',
      ],
    },
    {
      id: 'comp_3',
      name: 'OutlinePanel',
      category: 'panel',
      description: 'Code structure navigation with tree, flat, and semantic view modes',
      usage: "import { OutlinePanel } from '../panels/OutlinePanel';",
      filePath: 'src/components/panels/OutlinePanel.tsx',
      tags: ['outline', 'navigation', 'hhni', 'vif'],
      confidence: 0.92,
      usageCount: 1,
      hhniPath: ['IDE', 'Components', 'Panels', 'OutlinePanel'],
      semanticScore: 0.92,
      dependencies: ['useAIMOS', 'ConfidenceIndicator'],
      examples: [
        '<OutlinePanel />',
        '// Symbol navigation with HHNI integration',
      ],
    },
    {
      id: 'comp_4',
      name: 'useAIMOS',
      category: 'hook',
      description: 'Comprehensive hook providing access to all 8 AIM-OS core systems',
      usage: "import { useAIMOS } from '../../hooks/useAIMOS';",
      filePath: 'src/hooks/useAIMOS.ts',
      tags: ['hook', 'aimos', 'cmc', 'hhni', 'vif', 'seg', 'tcs', 'cas', 'apoe', 'sdfcvf'],
      confidence: 0.98,
      usageCount: 15,
      hhniPath: ['IDE', 'Hooks', 'AIMOS', 'useAIMOS'],
      semanticScore: 0.98,
      dependencies: [],
      examples: [
        'const { cmc, vif, seg } = useAIMOS();',
        'const { storeAtom } = cmc;',
        'const { trackConfidence } = vif;',
      ],
    },
    {
      id: 'comp_5',
      name: 'ConfidenceIndicator',
      category: 'ui',
      description: 'VIF confidence indicator component with multiple variants and sizes',
      usage: "import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';",
      filePath: 'src/components/ConfidenceIndicator/ConfidenceIndicator.tsx',
      tags: ['ui', 'confidence', 'vif', 'indicator'],
      confidence: 0.90,
      usageCount: 8,
      hhniPath: ['IDE', 'Components', 'UI', 'ConfidenceIndicator'],
      semanticScore: 0.90,
      dependencies: [],
      examples: [
        '<ConfidenceIndicator confidence={0.95} size="sm" variant="inline" />',
      ],
    },
    {
      id: 'comp_6',
      name: 'ContextWebPanel',
      category: 'visualization',
      description: 'Interactive knowledge graph visualization with semantic clustering',
      usage: "import { ContextWebPanel } from '../panels/ContextWebPanel';",
      filePath: 'src/components/panels/ContextWebPanel.tsx',
      tags: ['visualization', 'graph', 'hhni', 'seg', 'cmc'],
      confidence: 0.95,
      usageCount: 1,
      hhniPath: ['IDE', 'Components', 'Panels', 'ContextWebPanel'],
      semanticScore: 0.95,
      dependencies: ['useAIMOS'],
      examples: [
        '<ContextWebPanel />',
        '// Revolutionary knowledge graph visualization',
      ],
    },
    {
      id: 'comp_7',
      name: 'Layout',
      category: 'layout',
      description: '5-zone layout system with resizable panels and customizable zones',
      usage: "import { Layout } from '../Layout/Layout';",
      filePath: 'src/components/Layout/Layout.tsx',
      tags: ['layout', 'panels', 'resizable', 'zones'],
      confidence: 0.92,
      usageCount: 1,
      hhniPath: ['IDE', 'Components', 'Layout', 'Layout'],
      semanticScore: 0.92,
      dependencies: ['react-resizable-panels', 'usePanelStore'],
      examples: [
        '<Layout />',
        '// 5-zone layout: Top, Left, Center, Right, Bottom',
      ],
    },
  ], []);

  // Filter components
  const filteredComponents = useMemo(() => {
    return components.filter((comp) => {
      const matchesCategory = selectedCategory === 'all' || comp.category === selectedCategory;
      const matchesSearch =
        comp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        comp.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        comp.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesCategory && matchesSearch;
    });
  }, [components, selectedCategory, searchQuery]);

  const selectedComponentData = useMemo(() => {
    return selectedComponent ? components.find(c => c.id === selectedComponent) : null;
  }, [selectedComponent, components]);

  const categories: ComponentCategory[] = ['all', 'layout', 'panel', 'ui', 'hook', 'utility', 'visualization'];

  if (loading.hhni || loading.vif) {
    return <PanelLoading message="Loading Component Library..." />;
  }

  if (errors.hhni || errors.vif) {
    return (
      <div className="component-library-error" role="alert">
        <p>Error loading Component Library: {errors.hhni?.message || errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="component-library-panel" role="region" aria-label="Component Library Panel">
      {/* Header */}
      <div className="component-library-header">
        <div className="component-library-header-left">
          <Package className="component-library-header-icon" />
          <div>
            <h3 className="component-library-header-title">Component Library</h3>
            <p className="component-library-header-subtitle">
              Reusable Components • HHNI Search • VIF Confidence
            </p>
          </div>
        </div>
        <div className="component-library-header-right">
          <span className="component-library-count">{filteredComponents.length} components</span>
        </div>
      </div>

      {/* Controls */}
      <div className="component-library-controls">
        <div className="component-library-search">
          <Search className="component-library-search-icon" />
          <input
            type="text"
            className="component-library-search-input"
            placeholder="Search components..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search components"
          />
        </div>
        <div className="component-library-categories">
          {categories.map((category) => (
            <button
              key={category}
              className={`component-library-category ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category)}
              aria-label={`Filter by ${category}`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Component List */}
      <div className="component-library-list">
        {filteredComponents.length === 0 ? (
          <div className="component-library-empty">
            <Package className="component-library-empty-icon" />
            <p>No components found</p>
            {searchQuery && <p className="component-library-empty-hint">Try a different search query</p>}
          </div>
        ) : (
          filteredComponents.map((component) => (
            <div
              key={component.id}
              className={`component-library-item ${selectedComponent === component.id ? 'selected' : ''}`}
              onClick={() => setSelectedComponent(selectedComponent === component.id ? null : component.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedComponent(selectedComponent === component.id ? null : component.id);
                }
              }}
            >
              <div className="component-library-item-header">
                <div className="component-library-item-left">
                  {component.category === 'layout' && <Code className="component-library-item-icon" />}
                  {component.category === 'panel' && <FileText className="component-library-item-icon" />}
                  {component.category === 'ui' && <Eye className="component-library-item-icon" />}
                  {component.category === 'hook' && <Zap className="component-library-item-icon" />}
                  {component.category === 'visualization' && <Package className="component-library-item-icon" />}
                  <div className="component-library-item-info">
                    <div className="component-library-item-name">{component.name}</div>
                    <div className="component-library-item-description">{component.description}</div>
                  </div>
                </div>
                <div className="component-library-item-right">
                  {component.confidence !== undefined && (
                    <ConfidenceIndicator confidence={component.confidence} size="sm" variant="inline" />
                  )}
                  {component.usageCount !== undefined && (
                    <span className="component-library-item-usage">{component.usageCount}x</span>
                  )}
                </div>
              </div>

              {selectedComponent === component.id && (
                <div className="component-library-item-details">
                  {/* Usage */}
                  <div className="component-library-detail-section">
                    <div className="component-library-detail-section-header">Usage</div>
                    <div className="component-library-usage">
                      <code className="component-library-code">{component.usage}</code>
                      <button
                        className="component-library-copy-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigator.clipboard.writeText(component.usage);
                        }}
                        aria-label="Copy usage code"
                      >
                        <Copy className="component-library-copy-icon" />
                      </button>
                    </div>
                  </div>

                  {/* File Path */}
                  <div className="component-library-detail-section">
                    <div className="component-library-detail-section-header">File Path</div>
                    <div className="component-library-file-path">
                      <code className="component-library-code">{component.filePath}</code>
                      <button
                        className="component-library-external-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Open file in editor
                        }}
                        aria-label="Open file"
                      >
                        <ExternalLink className="component-library-external-icon" />
                      </button>
                    </div>
                  </div>

                  {/* Tags */}
                  {component.tags.length > 0 && (
                    <div className="component-library-detail-section">
                      <div className="component-library-detail-section-header">Tags</div>
                      <div className="component-library-tags">
                        {component.tags.map((tag) => (
                          <span key={tag} className="component-library-tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Dependencies */}
                  {component.dependencies && component.dependencies.length > 0 && (
                    <div className="component-library-detail-section">
                      <div className="component-library-detail-section-header">Dependencies</div>
                      <div className="component-library-dependencies">
                        {component.dependencies.map((dep) => (
                          <span key={dep} className="component-library-dependency">
                            {dep}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Examples */}
                  {component.examples && component.examples.length > 0 && (
                    <div className="component-library-detail-section">
                      <div className="component-library-detail-section-header">Examples</div>
                      <div className="component-library-examples">
                        {component.examples.map((example, index) => (
                          <code key={index} className="component-library-example-code">
                            {example}
                          </code>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

