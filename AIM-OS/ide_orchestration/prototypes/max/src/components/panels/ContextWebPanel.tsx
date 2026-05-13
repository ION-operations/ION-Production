// Context Web Panel - Max V2
// Revolutionary UX - Interactive Knowledge Graph Visualization
// Shows interconnected knowledge, code, decisions, and evidence as a living web

import React, { useState, useMemo } from 'react';
import { Network, Search, Filter, Layers, Zap, HelpCircle } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { PanelLoading } from '../Loading/Loading';
import './ContextWebPanel.css';

export interface ContextNode {
  id: string;
  label: string;
  type: 'component' | 'concept' | 'architecture' | 'decision' | 'evidence' | 'code' | 'document';
  confidence: number;
  evidence: string[];
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
  metadata?: Record<string, any>;
}

export interface ContextEdge {
  source: string;
  target: string;
  type: 'uses' | 'integrates' | 'depends_on' | 'references' | 'implements' | 'validates' | 'supports';
  confidence: number;
  evidence: string[];
  description?: string;
}

export interface ContextWebData {
  nodes: ContextNode[];
  edges: ContextEdge[];
}

export const ContextWebPanel: React.FC = () => {
  const { hhni, seg, cmc, vif, loading, errors } = useAIMOS();
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [queryMode, setQueryMode] = useState<'what' | 'why' | 'how' | null>(null);

  // Mock Context Web data (will be replaced with real AIM-OS data)
  const contextWebData: ContextWebData = useMemo(() => ({
    nodes: [
      {
        id: 'node_1',
        label: 'IDELayout Component',
        type: 'component',
        confidence: 0.92,
        evidence: ['atom_123'],
        bitemporal: { valid_from: new Date().toISOString(), valid_to: null },
        metadata: { file: 'Layout.tsx', lines: '1-100' },
      },
      {
        id: 'node_2',
        label: 'Panel System',
        type: 'concept',
        confidence: 0.88,
        evidence: ['atom_456'],
        bitemporal: { valid_from: new Date(Date.now() - 3600000).toISOString(), valid_to: null },
        metadata: { description: 'Panel-first architecture' },
      },
      {
        id: 'node_3',
        label: 'AIM-OS Integration',
        type: 'architecture',
        confidence: 0.95,
        evidence: ['atom_789'],
        bitemporal: { valid_from: new Date(Date.now() - 7200000).toISOString(), valid_to: null },
        metadata: { systems: ['CMC', 'HHNI', 'VIF', 'SEG'] },
      },
      {
        id: 'node_4',
        label: 'useAIMOS Hook',
        type: 'code',
        confidence: 0.94,
        evidence: ['atom_101'],
        bitemporal: { valid_from: new Date(Date.now() - 10800000).toISOString(), valid_to: null },
        metadata: { file: 'useAIMOS.ts', function: 'useAIMOS' },
      },
      {
        id: 'node_5',
        label: 'Debug Console',
        type: 'component',
        confidence: 0.90,
        evidence: ['atom_202'],
        bitemporal: { valid_from: new Date(Date.now() - 14400000).toISOString(), valid_to: null },
        metadata: { file: 'DebugConsolePanel.tsx' },
      },
      {
        id: 'node_6',
        label: 'Panel Customization',
        type: 'decision',
        confidence: 0.87,
        evidence: ['atom_303'],
        bitemporal: { valid_from: new Date(Date.now() - 18000000).toISOString(), valid_to: null },
        metadata: { rationale: 'Enable user customization' },
      },
    ],
    edges: [
      {
        source: 'node_1',
        target: 'node_2',
        type: 'uses',
        confidence: 0.90,
        evidence: ['atom_123'],
        description: 'IDELayout uses Panel System',
      },
      {
        source: 'node_1',
        target: 'node_3',
        type: 'integrates',
        confidence: 0.94,
        evidence: ['atom_456'],
        description: 'IDELayout integrates AIM-OS systems',
      },
      {
        source: 'node_1',
        target: 'node_4',
        type: 'uses',
        confidence: 0.92,
        evidence: ['atom_789'],
        description: 'IDELayout uses useAIMOS hook',
      },
      {
        source: 'node_4',
        target: 'node_3',
        type: 'implements',
        confidence: 0.95,
        evidence: ['atom_101'],
        description: 'useAIMOS implements AIM-OS integration',
      },
      {
        source: 'node_5',
        target: 'node_3',
        type: 'integrates',
        confidence: 0.91,
        evidence: ['atom_202'],
        description: 'Debug Console integrates AIM-OS systems',
      },
      {
        source: 'node_6',
        target: 'node_2',
        type: 'supports',
        confidence: 0.88,
        evidence: ['atom_303'],
        description: 'Panel Customization supports Panel System',
      },
    ],
  }), []);

  const filteredNodes = useMemo(() => {
    return contextWebData.nodes.filter((node) => {
      if (filterType !== 'all' && node.type !== filterType) return false;
      if (searchQuery && !node.label.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [contextWebData.nodes, filterType, searchQuery]);

  const filteredEdges = useMemo(() => {
    const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));
    return contextWebData.edges.filter((edge) => {
      return filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target);
    });
  }, [contextWebData.edges, filteredNodes]);

  const selectedNodeData = useMemo(() => {
    if (!selectedNode) return null;
    return contextWebData.nodes.find((n) => n.id === selectedNode);
  }, [selectedNode, contextWebData.nodes]);

  const selectedNodeEdges = useMemo(() => {
    if (!selectedNode) return [];
    return contextWebData.edges.filter((e) => e.source === selectedNode || e.target === selectedNode);
  }, [selectedNode, contextWebData.edges]);

  const getNodeTypeColor = (type: string) => {
    switch (type) {
      case 'component':
        return '#60a5fa'; // blue
      case 'concept':
        return '#a78bfa'; // purple
      case 'architecture':
        return '#4ade80'; // green
      case 'decision':
        return '#fbbf24'; // yellow
      case 'evidence':
        return '#f87171'; // red
      case 'code':
        return '#34d399'; // teal
      case 'document':
        return '#fb7185'; // pink
      default:
        return '#858585'; // gray
    }
  };

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'component':
        return '⚛️';
      case 'concept':
        return '💡';
      case 'architecture':
        return '🏗️';
      case 'decision':
        return '🎯';
      case 'evidence':
        return '📋';
      case 'code':
        return '💻';
      case 'document':
        return '📄';
      default:
        return '🔷';
    }
  };

  if (loading.hhni || loading.seg) {
    return <PanelLoading message="Loading Context Web..." />;
  }

  if (errors.hhni || errors.seg) {
    return (
      <div className="context-web-error" role="alert">
        <p>Error loading Context Web: {errors.hhni?.message || errors.seg?.message}</p>
      </div>
    );
  }

  return (
    <div className="context-web" role="region" aria-label="Context Web">
      {/* Header */}
      <div className="context-web-header">
        <div className="context-web-header-top">
          <div className="context-web-title">
            <Network className="context-web-icon" />
            <div>
              <h3 className="context-web-title-text">Context Web</h3>
              <p className="context-web-subtitle">
                Revolutionary UX • Interactive Knowledge Graph • Semantic Clustering • HHNI + SEG Powered
              </p>
            </div>
          </div>
        </div>

        {/* Query Interface */}
        <div className="context-web-queries">
          <button
            className={`query-button ${queryMode === 'what' ? 'query-button-active' : ''}`}
            onClick={() => setQueryMode(queryMode === 'what' ? null : 'what')}
            aria-label="What query mode"
          >
            <HelpCircle className="query-icon" />
            What?
          </button>
          <button
            className={`query-button ${queryMode === 'why' ? 'query-button-active' : ''}`}
            onClick={() => setQueryMode(queryMode === 'why' ? null : 'why')}
            aria-label="Why query mode"
          >
            <Zap className="query-icon" />
            Why?
          </button>
          <button
            className={`query-button ${queryMode === 'how' ? 'query-button-active' : ''}`}
            onClick={() => setQueryMode(queryMode === 'how' ? null : 'how')}
            aria-label="How query mode"
          >
            <Layers className="query-icon" />
            How?
          </button>
        </div>

        {/* Filters */}
        <div className="context-web-filters">
          <div className="filter-group">
            <Filter className="filter-icon" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="filter-select"
              aria-label="Filter by node type"
            >
              <option value="all">All Types</option>
              <option value="component">Components</option>
              <option value="concept">Concepts</option>
              <option value="architecture">Architecture</option>
              <option value="decision">Decisions</option>
              <option value="evidence">Evidence</option>
              <option value="code">Code</option>
              <option value="document">Documents</option>
            </select>
          </div>
          <div className="filter-group filter-search">
            <Search className="filter-icon" />
            <input
              type="search"
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="filter-input"
              aria-label="Search context web nodes"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="context-web-content">
        <div className="context-web-grid">
          {/* Graph Visualization */}
          <div className="context-web-graph">
            <div className="graph-header">
              <div className="graph-title">
                Knowledge Graph ({filteredNodes.length} nodes, {filteredEdges.length} connections)
              </div>
              <div className="graph-badges">
                <span>HHNI-Powered</span>
                <span>•</span>
                <span>SEG-Enhanced</span>
                <span>•</span>
                <span>Bitemporal</span>
              </div>
            </div>
            <div className="graph-visualization" role="img" aria-label="Context web graph visualization">
              {/* Simple graph visualization using CSS */}
              <div className="graph-nodes">
                {filteredNodes.map((node) => (
                  <div
                    key={node.id}
                    className={`graph-node ${selectedNode === node.id ? 'graph-node-selected' : ''}`}
                    style={{
                      backgroundColor: getNodeTypeColor(node.type),
                      borderColor: selectedNode === node.id ? '#007acc' : getNodeTypeColor(node.type),
                    }}
                    onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
                    role="button"
                    tabIndex={0}
                    aria-label={`${node.label} node, ${node.type} type, ${(node.confidence * 100).toFixed(0)}% confidence`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedNode(selectedNode === node.id ? null : node.id);
                      }
                    }}
                  >
                    <div className="graph-node-icon">{getNodeTypeIcon(node.type)}</div>
                    <div className="graph-node-label">{node.label}</div>
                    <div className="graph-node-confidence">{(node.confidence * 100).toFixed(0)}%</div>
                  </div>
                ))}
              </div>
              {/* Edge visualization */}
              <svg className="graph-edges" width="100%" height="100%">
                {filteredEdges.map((edge, idx) => {
                  const sourceNode = filteredNodes.find((n) => n.id === edge.source);
                  const targetNode = filteredNodes.find((n) => n.id === edge.target);
                  if (!sourceNode || !targetNode) return null;
                  // Simple line visualization (would be enhanced with ReactFlow in production)
                  return (
                    <line
                      key={idx}
                      x1="50"
                      y1="50"
                      x2="150"
                      y2="150"
                      stroke={getNodeTypeColor(sourceNode.type)}
                      strokeWidth="2"
                      opacity="0.5"
                      strokeDasharray={edge.type === 'depends_on' ? '5,5' : '0'}
                    />
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Sidebar */}
          <div className="context-web-sidebar">
            {/* Selected Node Details */}
            {selectedNodeData ? (
              <div className="sidebar-section">
                <h4 className="sidebar-title">Node Details</h4>
                <div className="node-details">
                  <div className="node-detail-header">
                    <span className="node-detail-label">{selectedNodeData.label}</span>
                    <span className="node-detail-confidence">
                      Conf: {(selectedNodeData.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="node-detail-type">
                    <span className="node-type-badge" style={{ backgroundColor: getNodeTypeColor(selectedNodeData.type) }}>
                      {getNodeTypeIcon(selectedNodeData.type)} {selectedNodeData.type}
                    </span>
                  </div>
                  {selectedNodeData.metadata && (
                    <div className="node-detail-metadata">
                      <details>
                        <summary>Metadata</summary>
                        <pre className="metadata-content">
                          {JSON.stringify(selectedNodeData.metadata, null, 2)}
                        </pre>
                      </details>
                    </div>
                  )}
                  {selectedNodeData.evidence && selectedNodeData.evidence.length > 0 && (
                    <div className="node-detail-evidence">
                      <span className="evidence-label">Evidence:</span>
                      <div className="evidence-list">
                        {selectedNodeData.evidence.map((ev, idx) => (
                          <span key={idx} className="evidence-badge">{ev}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="sidebar-section">
                <h4 className="sidebar-title">Select a Node</h4>
                <p className="sidebar-hint">Click on a node in the graph to see details</p>
              </div>
            )}

            {/* Connections */}
            {selectedNodeEdges.length > 0 && (
              <div className="sidebar-section">
                <h4 className="sidebar-title">Connections ({selectedNodeEdges.length})</h4>
                <div className="connections-list">
                  {selectedNodeEdges.map((edge, idx) => {
                    const connectedNode = contextWebData.nodes.find(
                      (n) => n.id === (edge.source === selectedNode ? edge.target : edge.source)
                    );
                    return (
                      <div key={idx} className="connection-item">
                        <div className="connection-header">
                          <span className="connection-type">{edge.type}</span>
                          <span className="connection-confidence">
                            Conf: {(edge.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        {connectedNode && (
                          <div className="connection-target">{connectedNode.label}</div>
                        )}
                        {edge.description && (
                          <div className="connection-description">{edge.description}</div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Query Results */}
            {queryMode && (
              <div className="sidebar-section">
                <h4 className="sidebar-title">
                  {queryMode === 'what' && 'What?'}
                  {queryMode === 'why' && 'Why?'}
                  {queryMode === 'how' && 'How?'}
                </h4>
                <div className="query-results">
                  <p className="query-hint">
                    {queryMode === 'what' && 'Showing what this node represents and its relationships'}
                    {queryMode === 'why' && 'Showing why this node exists and its purpose'}
                    {queryMode === 'how' && 'Showing how this node is implemented and used'}
                  </p>
                  {/* Query results would be populated with HHNI semantic search */}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

