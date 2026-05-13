// Enhanced Outline Panel - Max V2
// Code structure navigation with AIM-OS integration (HHNI, VIF, SEG)

import React, { useState, useMemo } from 'react';
import { FileText, Function, Class, Variable, ChevronRight, ChevronDown, Search, Network, Code, Refresh } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './OutlinePanel.css';

export type OutlineViewMode = 'tree' | 'flat' | 'semantic';

export interface OutlineSymbol {
  id: string;
  name: string;
  type: 'file' | 'function' | 'class' | 'interface' | 'variable' | 'type' | 'module' | 'namespace' | 'enum';
  line: number;
  column?: number;
  file?: string;
  children?: OutlineSymbol[];
  
  // AIM-OS Integration
  hhniNode?: {
    id: string;
    level: 'document' | 'paragraph' | 'sentence';
    content: string;
    summary?: string;
  };
  hhniPath?: string[];
  semanticScore?: number;
  confidence?: number;
  evidenceTrail?: any;
}

export const OutlinePanel: React.FC = () => {
  const { hhni, vif, loading, errors } = useAIMOS();
  const [viewMode, setViewMode] = useState<OutlineViewMode>('tree');
  const [searchQuery, setSearchQuery] = useState('');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

  // Mock symbols with AIM-OS integration
  const symbols: OutlineSymbol[] = useMemo(() => [
    {
      id: 'symbol_1',
      name: 'TerminalPanel.tsx',
      type: 'file',
      line: 1,
      file: 'src/components/panels/TerminalPanel.tsx',
      hhniPath: ['IDE', 'Components', 'Panels', 'TerminalPanel'],
      semanticScore: 0.95,
      confidence: 0.95,
      children: [
        {
          id: 'symbol_1_1',
          name: 'TerminalPanel',
          type: 'class',
          line: 28,
          column: 1,
          file: 'src/components/panels/TerminalPanel.tsx',
          hhniPath: ['IDE', 'Components', 'Panels', 'TerminalPanel', 'TerminalPanel'],
          semanticScore: 0.95,
          confidence: 0.95,
          children: [
            {
              id: 'symbol_1_1_1',
              name: 'executeCommand',
              type: 'function',
              line: 45,
              column: 5,
              file: 'src/components/panels/TerminalPanel.tsx',
              hhniPath: ['IDE', 'Components', 'Panels', 'TerminalPanel', 'TerminalPanel', 'executeCommand'],
              semanticScore: 0.92,
              confidence: 0.92,
            },
            {
              id: 'symbol_1_1_2',
              name: 'handleKeyDown',
              type: 'function',
              line: 180,
              column: 5,
              file: 'src/components/panels/TerminalPanel.tsx',
              hhniPath: ['IDE', 'Components', 'Panels', 'TerminalPanel', 'TerminalPanel', 'handleKeyDown'],
              semanticScore: 0.88,
              confidence: 0.88,
            },
          ],
        },
        {
          id: 'symbol_1_2',
          name: 'TerminalCommand',
          type: 'interface',
          line: 10,
          column: 1,
          file: 'src/components/panels/TerminalPanel.tsx',
          hhniPath: ['IDE', 'Components', 'Panels', 'TerminalPanel', 'TerminalCommand'],
          semanticScore: 0.90,
          confidence: 0.90,
        },
      ],
    },
    {
      id: 'symbol_2',
      name: 'GitPanel.tsx',
      type: 'file',
      line: 1,
      file: 'src/components/panels/GitPanel.tsx',
      hhniPath: ['IDE', 'Components', 'Panels', 'GitPanel'],
      semanticScore: 0.93,
      confidence: 0.93,
      children: [
        {
          id: 'symbol_2_1',
          name: 'GitPanel',
          type: 'class',
          line: 67,
          column: 1,
          file: 'src/components/panels/GitPanel.tsx',
          hhniPath: ['IDE', 'Components', 'Panels', 'GitPanel', 'GitPanel'],
          semanticScore: 0.93,
          confidence: 0.93,
          children: [
            {
              id: 'symbol_2_1_1',
              name: 'gitStatus',
              type: 'variable',
              line: 75,
              column: 3,
              file: 'src/components/panels/GitPanel.tsx',
              hhniPath: ['IDE', 'Components', 'Panels', 'GitPanel', 'GitPanel', 'gitStatus'],
              semanticScore: 0.90,
              confidence: 0.90,
            },
          ],
        },
      ],
    },
    {
      id: 'symbol_3',
      name: 'useAIMOS',
      type: 'function',
      line: 243,
      column: 1,
      file: 'src/hooks/useAIMOS.ts',
      hhniPath: ['IDE', 'Hooks', 'AIMOS', 'useAIMOS'],
      semanticScore: 0.98,
      confidence: 0.98,
      children: [
        {
          id: 'symbol_3_1',
          name: 'cmc',
          type: 'variable',
          line: 636,
          column: 3,
          file: 'src/hooks/useAIMOS.ts',
          hhniPath: ['IDE', 'Hooks', 'AIMOS', 'useAIMOS', 'cmc'],
          semanticScore: 0.95,
          confidence: 0.95,
        },
        {
          id: 'symbol_3_2',
          name: 'vif',
          type: 'variable',
          line: 649,
          column: 3,
          file: 'src/hooks/useAIMOS.ts',
          hhniPath: ['IDE', 'Hooks', 'AIMOS', 'useAIMOS', 'vif'],
          semanticScore: 0.95,
          confidence: 0.95,
        },
      ],
    },
  ], []);

  // Filter symbols based on search query
  const filteredSymbols = useMemo(() => {
    if (!searchQuery.trim()) return symbols;

    const query = searchQuery.toLowerCase();
    const filterSymbol = (symbol: OutlineSymbol): OutlineSymbol | null => {
      const matches = 
        symbol.name.toLowerCase().includes(query) ||
        symbol.type.toLowerCase().includes(query) ||
        symbol.hhniPath?.some(path => path.toLowerCase().includes(query));

      const filteredChildren = symbol.children
        ?.map(child => filterSymbol(child))
        .filter((child): child is OutlineSymbol => child !== null);

      if (matches || (filteredChildren && filteredChildren.length > 0)) {
        return {
          ...symbol,
          children: filteredChildren,
        };
      }

      return null;
    };

    return symbols
      .map(symbol => filterSymbol(symbol))
      .filter((symbol): symbol is OutlineSymbol => symbol !== null);
  }, [symbols, searchQuery]);

  // Flatten symbols for flat view
  const flatSymbols = useMemo(() => {
    const flatten = (symbols: OutlineSymbol[], level: number = 0): OutlineSymbol[] => {
      const result: OutlineSymbol[] = [];
      for (const symbol of symbols) {
        result.push({ ...symbol, line: symbol.line + level });
        if (symbol.children) {
          result.push(...flatten(symbol.children, level + 1));
        }
      }
      return result;
    };
    return flatten(filteredSymbols);
  }, [filteredSymbols]);

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpanded(newExpanded);
  };

  const getTypeIcon = (type: OutlineSymbol['type']) => {
    switch (type) {
      case 'file':
        return <FileText className="outline-icon" />;
      case 'function':
        return <Function className="outline-icon" />;
      case 'class':
      case 'interface':
      case 'type':
        return <Class className="outline-icon" />;
      case 'variable':
        return <Variable className="outline-icon" />;
      case 'module':
      case 'namespace':
        return <Code className="outline-icon" />;
      default:
        return <Code className="outline-icon" />;
    }
  };

  const handleSymbolClick = (symbol: OutlineSymbol) => {
    setSelectedSymbol(symbol.id);
    // TODO: Navigate to symbol location in editor
    console.log('Navigate to:', symbol.file, symbol.line, symbol.column);
  };

  const renderTreeSymbol = (symbol: OutlineSymbol, level: number = 0): React.ReactNode => {
    const isExpanded = expanded.has(symbol.id);
    const hasChildren = symbol.children && symbol.children.length > 0;
    const isSelected = selectedSymbol === symbol.id;

    return (
      <div key={symbol.id}>
        <div
          className={`outline-item ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => handleSymbolClick(symbol)}
          onDoubleClick={() => hasChildren && toggleExpand(symbol.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              if (hasChildren) {
                toggleExpand(symbol.id);
              } else {
                handleSymbolClick(symbol);
              }
            }
          }}
        >
          <div className="outline-item-left">
            {hasChildren ? (
              <button
                className="outline-expand-button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleExpand(symbol.id);
                }}
                aria-label={isExpanded ? 'Collapse' : 'Expand'}
              >
                {isExpanded ? (
                  <ChevronDown className="outline-expand-icon" />
                ) : (
                  <ChevronRight className="outline-expand-icon" />
                )}
              </button>
            ) : (
              <span className="outline-expand-spacer" />
            )}
            {getTypeIcon(symbol.type)}
            <span className="outline-name">{symbol.name}</span>
          </div>
          <div className="outline-item-right">
            {symbol.semanticScore !== undefined && viewMode === 'semantic' && (
              <span className="outline-semantic-score">
                {(symbol.semanticScore * 100).toFixed(0)}%
              </span>
            )}
            {symbol.confidence !== undefined && (
              <ConfidenceIndicator confidence={symbol.confidence} size="sm" variant="inline" />
            )}
            <span className="outline-line">{symbol.line}</span>
          </div>
        </div>
        {hasChildren && isExpanded && (
          <div className="outline-children">
            {symbol.children!.map((child) => renderTreeSymbol(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderFlatSymbol = (symbol: OutlineSymbol): React.ReactNode => {
    const isSelected = selectedSymbol === symbol.id;
    return (
      <div
        key={symbol.id}
        className={`outline-item ${isSelected ? 'selected' : ''}`}
        onClick={() => handleSymbolClick(symbol)}
        role="button"
        tabIndex={0}
      >
        <div className="outline-item-left">
          {getTypeIcon(symbol.type)}
          <span className="outline-name">{symbol.name}</span>
          {symbol.file && (
            <span className="outline-file">{symbol.file}</span>
          )}
        </div>
        <div className="outline-item-right">
          {symbol.confidence !== undefined && (
            <ConfidenceIndicator confidence={symbol.confidence} size="sm" variant="inline" />
          )}
          <span className="outline-line">{symbol.line}</span>
        </div>
      </div>
    );
  };

  if (loading.hhni || loading.vif) {
    return <PanelLoading message="Loading Outline..." />;
  }

  if (errors.hhni || errors.vif) {
    return (
      <div className="outline-error" role="alert">
        <p>Error loading Outline: {errors.hhni?.message || errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="outline-panel" role="region" aria-label="Outline Panel">
      {/* Header */}
      <div className="outline-header">
        <div className="outline-header-left">
          <Code className="outline-header-icon" />
          <div>
            <h3 className="outline-header-title">Outline</h3>
            <p className="outline-header-subtitle">
              Code Structure • HHNI Navigation • VIF Confidence
            </p>
          </div>
        </div>
        <div className="outline-header-right">
          <button className="outline-refresh-button" aria-label="Refresh outline">
            <Refresh className="outline-refresh-icon" />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="outline-controls">
        <div className="outline-search">
          <Search className="outline-search-icon" />
          <input
            type="text"
            className="outline-search-input"
            placeholder="Search symbols..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search symbols"
          />
        </div>
        <div className="outline-view-modes">
          <button
            className={`outline-view-mode ${viewMode === 'tree' ? 'active' : ''}`}
            onClick={() => setViewMode('tree')}
            aria-label="Tree view"
            title="Tree View"
          >
            <Network className="outline-view-mode-icon" />
          </button>
          <button
            className={`outline-view-mode ${viewMode === 'flat' ? 'active' : ''}`}
            onClick={() => setViewMode('flat')}
            aria-label="Flat view"
            title="Flat View"
          >
            <FileText className="outline-view-mode-icon" />
          </button>
          <button
            className={`outline-view-mode ${viewMode === 'semantic' ? 'active' : ''}`}
            onClick={() => setViewMode('semantic')}
            aria-label="Semantic view"
            title="Semantic View"
          >
            <Network className="outline-view-mode-icon" />
          </button>
        </div>
      </div>

      {/* Symbol List */}
      <div className="outline-list">
        {viewMode === 'tree' && (
          <div className="outline-tree">
            {filteredSymbols.length === 0 ? (
              <div className="outline-empty">
                <p>No symbols found</p>
                {searchQuery && <p className="outline-empty-hint">Try a different search query</p>}
              </div>
            ) : (
              filteredSymbols.map((symbol) => renderTreeSymbol(symbol))
            )}
          </div>
        )}

        {viewMode === 'flat' && (
          <div className="outline-flat">
            {flatSymbols.length === 0 ? (
              <div className="outline-empty">
                <p>No symbols found</p>
                {searchQuery && <p className="outline-empty-hint">Try a different search query</p>}
              </div>
            ) : (
              flatSymbols.map((symbol) => renderFlatSymbol(symbol))
            )}
          </div>
        )}

        {viewMode === 'semantic' && (
          <div className="outline-semantic">
            {filteredSymbols.length === 0 ? (
              <div className="outline-empty">
                <p>No symbols found</p>
                {searchQuery && <p className="outline-empty-hint">Try a different search query</p>}
              </div>
            ) : (
              filteredSymbols
                .sort((a, b) => (b.semanticScore || 0) - (a.semanticScore || 0))
                .map((symbol) => renderTreeSymbol(symbol))
            )}
          </div>
        )}
      </div>
    </div>
  );
};
