// AI Memory Panel - Max V2
// AIM-OS memory browser with CMC, HHNI, VIF integration

import React, { useState, useMemo, useEffect } from 'react';
import { Brain, Search, Filter, FileText, Code, Zap, Settings, Clock, Refresh, Database, Network } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { EvidenceTrailDisplay } from '../EvidenceTrailDisplay/EvidenceTrailDisplay';
import { BitemporalDisplay } from '../BitemporalDisplay/BitemporalDisplay';
import { PanelLoading } from '../Loading/Loading';
import { createBitemporalMetadata } from '../../utils/bitemporal';
import './AIMemoryPanel.css';

export type MemoryModality = 'all' | 'text' | 'code' | 'event' | 'tool';
export type MemorySortBy = 'recent' | 'confidence' | 'relevance';

export interface Memory {
  id: string;
  content: string;
  modality: 'text' | 'code' | 'event' | 'tool';
  tags: Record<string, number>;
  created_at: string;
  confidence?: number;
  hhniPath?: string[];
  semanticScore?: number;
  evidenceTrail?: any;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
}

export const AIMemoryPanel: React.FC = () => {
  const { cmc, hhni, vif, loading, errors } = useAIMOS();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterModality, setFilterModality] = useState<MemoryModality>('all');
  const [sortBy, setSortBy] = useState<MemorySortBy>('recent');
  const [selectedMemory, setSelectedMemory] = useState<string | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);

  // Mock memories with AIM-OS integration
  const mockMemories: Memory[] = useMemo(() => [
    {
      id: 'mem_1',
      content: 'Phase 6.2 Feature Implementation Progress Report: 80% complete (12/15 tasks). All major foundations implemented: Bitemporal Support, Evidence Trails, Confidence Indicators, Contradiction Detection.',
      modality: 'text',
      tags: { 'phase': 0.99, 'progress': 0.43, 'foundations': 0.21 },
      created_at: new Date(Date.now() - 3600000).toISOString(),
      confidence: 0.90,
      hhniPath: ['IDE', 'Memory', 'Progress', 'Phase6.2'],
      semanticScore: 0.90,
      bitemporal: createBitemporalMetadata(),
    },
    {
      id: 'mem_2',
      content: 'Completed Terminal Panel and Git Panel implementations for Max V2 prototype. Terminal Panel: Multi-session terminal with command execution, AIM-OS integration (CMC, VIF, SEG), evidence trails, confidence indicators, bitemporal support.',
      modality: 'text',
      tags: { 'panels': 0.94, 'terminal': 0.88, 'git': 0.85 },
      created_at: new Date(Date.now() - 7200000).toISOString(),
      confidence: 0.92,
      hhniPath: ['IDE', 'Memory', 'Panels', 'TerminalPanel'],
      semanticScore: 0.92,
      bitemporal: createBitemporalMetadata(),
    },
    {
      id: 'mem_3',
      content: 'const useAIMOS = () => { const { cmc, vif, seg } = useAIMOS(); return { cmc, vif, seg }; };',
      modality: 'code',
      tags: { 'hook': 0.98, 'aimos': 0.95, 'cmc': 0.90 },
      created_at: new Date(Date.now() - 10800000).toISOString(),
      confidence: 0.98,
      hhniPath: ['IDE', 'Memory', 'Code', 'useAIMOS'],
      semanticScore: 0.98,
      bitemporal: createBitemporalMetadata(),
    },
    {
      id: 'mem_4',
      content: 'Command executed: npm install -g typescript',
      modality: 'event',
      tags: { 'command': 0.95, 'terminal': 0.90 },
      created_at: new Date(Date.now() - 14400000).toISOString(),
      confidence: 0.85,
      hhniPath: ['IDE', 'Memory', 'Events', 'Command'],
      semanticScore: 0.85,
      bitemporal: createBitemporalMetadata(),
    },
    {
      id: 'mem_5',
      content: 'Tool: mcp_lucid-mcp_store_memory called with content: "Panel implementation complete"',
      modality: 'tool',
      tags: { 'tool': 0.92, 'mcp': 0.88 },
      created_at: new Date(Date.now() - 18000000).toISOString(),
      confidence: 0.88,
      hhniPath: ['IDE', 'Memory', 'Tools', 'MCP'],
      semanticScore: 0.88,
      bitemporal: createBitemporalMetadata(),
    },
  ], []);

  // Load memories on mount
  useEffect(() => {
    // TODO: Replace with real CMC retrieval
    // const loadMemories = async () => {
    //   const results = await cmc.searchAtoms('', 50);
    //   setMemories(results);
    // };
    // loadMemories();
    setMemories(mockMemories);
  }, [cmc]);

  // Filter and sort memories
  const filteredMemories = useMemo(() => {
    let filtered = memories.filter((mem) => {
      const matchesModality = filterModality === 'all' || mem.modality === filterModality;
      const matchesSearch =
        !searchQuery.trim() ||
        mem.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        Object.keys(mem.tags).some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesModality && matchesSearch;
    });

    // Sort memories
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'confidence':
          return (b.confidence || 0) - (a.confidence || 0);
        case 'relevance':
          const aWeight = Math.max(...Object.values(a.tags));
          const bWeight = Math.max(...Object.values(b.tags));
          return bWeight - aWeight;
        default:
          return 0;
      }
    });

    return filtered;
  }, [memories, filterModality, searchQuery, sortBy]);

  const selectedMemoryData = useMemo(() => {
    return selectedMemory ? memories.find(m => m.id === selectedMemory) : null;
  }, [selectedMemory, memories]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setMemories(mockMemories);
      return;
    }

    try {
      // TODO: Use HHNI semantic search
      // const hhniResults = await hhni.search(searchQuery, 50);
      // const atomIds = hhniResults.map(r => r.node.id);
      // const results = await Promise.all(
      //   atomIds.map(async (id) => {
      //     const atoms = await cmc.searchAtoms(`atom_id:${id}`, 1);
      //     return atoms[0];
      //   })
      // );
      // setMemories(results.filter(Boolean));

      // For now, filter mock memories
      const filtered = mockMemories.filter((mem) =>
        mem.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        Object.keys(mem.tags).some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setMemories(filtered);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const getModalityIcon = (modality: Memory['modality']) => {
    switch (modality) {
      case 'text':
        return <FileText className="memory-modality-icon" />;
      case 'code':
        return <Code className="memory-modality-icon" />;
      case 'event':
        return <Zap className="memory-modality-icon" />;
      case 'tool':
        return <Settings className="memory-modality-icon" />;
      default:
        return <FileText className="memory-modality-icon" />;
    }
  };

  const getModalityColor = (modality: Memory['modality']) => {
    switch (modality) {
      case 'text':
        return '#60a5fa';
      case 'code':
        return '#4ade80';
      case 'event':
        return '#fbbf24';
      case 'tool':
        return '#a78bfa';
      default:
        return '#858585';
    }
  };

  if (loading.cmc || loading.hhni || loading.vif) {
    return <PanelLoading message="Loading AI Memory..." />;
  }

  if (errors.cmc || errors.hhni || errors.vif) {
    return (
      <div className="ai-memory-error" role="alert">
        <p>Error loading AI Memory: {errors.cmc?.message || errors.hhni?.message || errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="ai-memory-panel" role="region" aria-label="AI Memory Panel">
      {/* Header */}
      <div className="ai-memory-header">
        <div className="ai-memory-header-left">
          <Brain className="ai-memory-header-icon" />
          <div>
            <h3 className="ai-memory-header-title">AI Memory</h3>
            <p className="ai-memory-header-subtitle">
              CMC Exploration • HHNI Search • VIF Confidence • Evidence Trails
            </p>
          </div>
        </div>
        <div className="ai-memory-header-right">
          <button
            className="ai-memory-refresh-button"
            onClick={() => setMemories(mockMemories)}
            aria-label="Refresh memories"
          >
            <Refresh className="ai-memory-refresh-icon" />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="ai-memory-controls">
        <div className="ai-memory-search">
          <Search className="ai-memory-search-icon" />
          <input
            type="text"
            className="ai-memory-search-input"
            placeholder="Search memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
            aria-label="Search memories"
          />
          <button
            className="ai-memory-search-button"
            onClick={handleSearch}
            aria-label="Search"
          >
            Search
          </button>
        </div>
        <div className="ai-memory-filters">
          <div className="ai-memory-filter-group">
            <Filter className="ai-memory-filter-icon" />
            <span className="ai-memory-filter-label">Modality:</span>
            {(['all', 'text', 'code', 'event', 'tool'] as MemoryModality[]).map((modality) => (
              <button
                key={modality}
                className={`ai-memory-filter-button ${filterModality === modality ? 'active' : ''}`}
                onClick={() => setFilterModality(modality)}
                aria-label={`Filter by ${modality}`}
              >
                {modality.charAt(0).toUpperCase() + modality.slice(1)}
              </button>
            ))}
          </div>
          <div className="ai-memory-filter-group">
            <span className="ai-memory-filter-label">Sort:</span>
            {(['recent', 'confidence', 'relevance'] as MemorySortBy[]).map((sort) => (
              <button
                key={sort}
                className={`ai-memory-filter-button ${sortBy === sort ? 'active' : ''}`}
                onClick={() => setSortBy(sort)}
                aria-label={`Sort by ${sort}`}
              >
                {sort.charAt(0).toUpperCase() + sort.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Memory List */}
      <div className="ai-memory-list">
        {filteredMemories.length === 0 ? (
          <div className="ai-memory-empty">
            <Brain className="ai-memory-empty-icon" />
            <p>No memories found</p>
            {searchQuery && <p className="ai-memory-empty-hint">Try a different search query</p>}
          </div>
        ) : (
          filteredMemories.map((memory) => (
            <div
              key={memory.id}
              className={`ai-memory-item ${selectedMemory === memory.id ? 'selected' : ''}`}
              onClick={() => setSelectedMemory(selectedMemory === memory.id ? null : memory.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedMemory(selectedMemory === memory.id ? null : memory.id);
                }
              }}
            >
              <div className="ai-memory-item-header">
                <div className="ai-memory-item-left">
                  <div
                    className="ai-memory-modality-badge"
                    style={{ backgroundColor: getModalityColor(memory.modality) }}
                  >
                    {getModalityIcon(memory.modality)}
                  </div>
                  <div className="ai-memory-item-content">
                    <div className="ai-memory-item-text">
                      {memory.content.length > 100
                        ? `${memory.content.substring(0, 100)}...`
                        : memory.content}
                    </div>
                    <div className="ai-memory-item-meta">
                      <span className="ai-memory-item-time">
                        <Clock className="ai-memory-item-time-icon" />
                        {new Date(memory.created_at).toLocaleString()}
                      </span>
                      {memory.hhniPath && (
                        <span className="ai-memory-item-path">
                          <Network className="ai-memory-item-path-icon" />
                          {memory.hhniPath.join(' → ')}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="ai-memory-item-right">
                  {memory.semanticScore !== undefined && (
                    <span className="ai-memory-semantic-score">
                      {(memory.semanticScore * 100).toFixed(0)}%
                    </span>
                  )}
                  {memory.confidence !== undefined && (
                    <ConfidenceIndicator confidence={memory.confidence} size="sm" variant="inline" />
                  )}
                </div>
              </div>

              {selectedMemory === memory.id && (
                <div className="ai-memory-item-details">
                  {/* Full Content */}
                  <div className="ai-memory-detail-section">
                    <div className="ai-memory-detail-section-header">Content</div>
                    <div className="ai-memory-content-full">
                      {memory.modality === 'code' ? (
                        <pre className="ai-memory-code-content">
                          <code>{memory.content}</code>
                        </pre>
                      ) : (
                        <p className="ai-memory-text-content">{memory.content}</p>
                      )}
                    </div>
                  </div>

                  {/* Tags */}
                  {Object.keys(memory.tags).length > 0 && (
                    <div className="ai-memory-detail-section">
                      <div className="ai-memory-detail-section-header">Tags</div>
                      <div className="ai-memory-tags">
                        {Object.entries(memory.tags).map(([tag, weight]) => (
                          <span
                            key={tag}
                            className="ai-memory-tag"
                            style={{ opacity: Math.max(0.5, weight) }}
                          >
                            {tag} ({(weight * 100).toFixed(0)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* AIM-OS Integration */}
                  <div className="ai-memory-detail-section">
                    <div className="ai-memory-detail-section-header">AIM-OS Integration</div>
                    <div className="ai-memory-aimos">
                      {memory.hhniPath && (
                        <div className="ai-memory-aimos-item">
                          <Network className="ai-memory-aimos-icon" />
                          <span className="ai-memory-aimos-label">HHNI Path:</span>
                          <span className="ai-memory-aimos-value">{memory.hhniPath.join(' → ')}</span>
                        </div>
                      )}
                      {memory.bitemporal && (
                        <BitemporalDisplay bitemporal={memory.bitemporal} compact={true} />
                      )}
                      {memory.evidenceTrail && (
                        <EvidenceTrailDisplay trail={memory.evidenceTrail} compact={true} />
                      )}
                      <div className="ai-memory-aimos-item">
                        <Database className="ai-memory-aimos-icon" />
                        <span className="ai-memory-aimos-label">CMC Atom:</span>
                        <span className="ai-memory-aimos-value">{memory.id}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

