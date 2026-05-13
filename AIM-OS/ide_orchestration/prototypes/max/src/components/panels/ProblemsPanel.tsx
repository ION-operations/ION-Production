// Enhanced Problems Panel - Max V2
// Lifecycle tracking, solution details, AIM-OS integration

import React, { useState, useMemo } from 'react';
import { AlertCircle, AlertTriangle, Info, CheckCircle, Search, Filter, ChevronDown, ChevronRight, Clock, User, GitBranch } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { PanelLoading } from '../Loading/Loading';
import './ProblemsPanel.css';

export type ProblemStatus = 'new' | 'investigating' | 'solved';
export type ProblemSeverity = 'error' | 'warning' | 'info';

export interface EnhancedProblem {
  id: string;
  type: ProblemSeverity;
  status: ProblemStatus;
  message: string;
  file: string;
  line: number;
  column?: number;
  code?: string;
  confidence: number;
  detected: string;
  solved?: string | null;
  solvedBy?: string | null;
  solution?: string | null;
  evidence?: string[];
  cmcAtom?: string;
  vifConfidence?: number;
  segEvidence?: string[];
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
}

export const ProblemsPanel: React.FC = () => {
  const { vif, seg, loading, errors } = useAIMOS();
  const [expandedProblems, setExpandedProblems] = useState<Set<string>>(new Set());
  const [filterStatus, setFilterStatus] = useState<ProblemStatus | 'all'>('all');
  const [filterType, setFilterType] = useState<ProblemSeverity | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock enhanced problems (will be replaced with real VIF/SEG data)
  const problems: EnhancedProblem[] = useMemo(() => [
    {
      id: 'prob_1',
      type: 'error',
      status: 'solved',
      message: 'Type error in IDELayout.tsx',
      file: 'src/components/IDELayout.tsx',
      line: 42,
      column: 15,
      code: 'const panel = panels.find(p => p.id === panelId)',
      confidence: 0.95,
      detected: new Date(Date.now() - 3600000).toISOString(),
      solved: new Date(Date.now() - 3300000).toISOString(),
      solvedBy: 'max',
      solution: 'Fixed type mismatch in panel state management by adding null check',
      evidence: ['atom_600', 'atom_601'],
      cmcAtom: 'atom_600',
      vifConfidence: 0.95,
      segEvidence: ['evidence_node_11'],
      bitemporal: {
        valid_from: new Date(Date.now() - 3600000).toISOString(),
        valid_to: new Date(Date.now() - 3300000).toISOString(),
      },
    },
    {
      id: 'prob_2',
      type: 'warning',
      status: 'investigating',
      message: 'Unused import detected',
      file: 'src/components/CodeEditor.tsx',
      line: 15,
      column: 10,
      code: "import { useState } from 'react'",
      confidence: 0.88,
      detected: new Date(Date.now() - 1800000).toISOString(),
      solved: null,
      solvedBy: null,
      solution: null,
      evidence: ['atom_602'],
      cmcAtom: 'atom_602',
      vifConfidence: 0.88,
      segEvidence: ['evidence_node_12'],
      bitemporal: {
        valid_from: new Date(Date.now() - 1800000).toISOString(),
        valid_to: null,
      },
    },
    {
      id: 'prob_3',
      type: 'error',
      status: 'new',
      message: 'Missing dependency in package.json',
      file: 'package.json',
      line: 0,
      confidence: 0.92,
      detected: new Date(Date.now() - 600000).toISOString(),
      solved: null,
      solvedBy: null,
      solution: null,
      evidence: ['atom_603'],
      cmcAtom: 'atom_603',
      vifConfidence: 0.92,
      segEvidence: ['evidence_node_13'],
      bitemporal: {
        valid_from: new Date(Date.now() - 600000).toISOString(),
        valid_to: null,
      },
    },
    {
      id: 'prob_4',
      type: 'error',
      status: 'solved',
      message: 'Syntax error in HierarchicalCodeExplorer.tsx',
      file: 'src/components/panels/HierarchicalCodeExplorer.tsx',
      line: 73,
      column: 5,
      code: 'const renderTree = (node: FileNode, depth: number = 0)',
      confidence: 0.98,
      detected: new Date(Date.now() - 7200000).toISOString(),
      solved: new Date(Date.now() - 6900000).toISOString(),
      solvedBy: 'max',
      solution: 'Fixed missing import statement for ChevronRight icon',
      evidence: ['atom_604', 'atom_605'],
      cmcAtom: 'atom_604',
      vifConfidence: 0.98,
      segEvidence: ['evidence_node_14'],
      bitemporal: {
        valid_from: new Date(Date.now() - 7200000).toISOString(),
        valid_to: new Date(Date.now() - 6900000).toISOString(),
      },
    },
    {
      id: 'prob_5',
      type: 'warning',
      status: 'solved',
      message: 'Performance warning: Large component re-render',
      file: 'src/components/Layout.tsx',
      line: 85,
      column: 12,
      code: 'const panels = usePanelStore((state) => state.panels)',
      confidence: 0.85,
      detected: new Date(Date.now() - 10800000).toISOString(),
      solved: new Date(Date.now() - 9000000).toISOString(),
      solvedBy: 'max',
      solution: 'Optimized state management with useMemo hooks to prevent unnecessary re-renders',
      evidence: ['atom_606'],
      cmcAtom: 'atom_606',
      vifConfidence: 0.85,
      segEvidence: ['evidence_node_15'],
      bitemporal: {
        valid_from: new Date(Date.now() - 10800000).toISOString(),
        valid_to: new Date(Date.now() - 9000000).toISOString(),
      },
    },
  ], []);

  const toggleExpand = (problemId: string) => {
    const newExpanded = new Set(expandedProblems);
    if (newExpanded.has(problemId)) {
      newExpanded.delete(problemId);
    } else {
      newExpanded.add(problemId);
    }
    setExpandedProblems(newExpanded);
  };

  const filteredProblems = useMemo(() => {
    return problems.filter((prob) => {
      const matchesStatus = filterStatus === 'all' || prob.status === filterStatus;
      const matchesType = filterType === 'all' || prob.type === filterType;
      const matchesSearch = searchQuery === '' || 
        prob.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
        prob.file.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesType && matchesSearch;
    });
  }, [problems, filterStatus, filterType, searchQuery]);

  const stats = useMemo(() => ({
    total: problems.length,
    errors: problems.filter(p => p.type === 'error').length,
    warnings: problems.filter(p => p.type === 'warning').length,
    info: problems.filter(p => p.type === 'info').length,
    solved: problems.filter(p => p.status === 'solved').length,
    investigating: problems.filter(p => p.status === 'investigating').length,
    new: problems.filter(p => p.status === 'new').length,
  }), [problems]);

  const getStatusColor = (status: ProblemStatus) => {
    switch (status) {
      case 'solved':
        return 'status-solved';
      case 'investigating':
        return 'status-investigating';
      case 'new':
        return 'status-new';
      default:
        return 'status-unknown';
    }
  };

  const getStatusIcon = (status: ProblemStatus) => {
    switch (status) {
      case 'solved':
        return <CheckCircle className="status-icon" />;
      case 'investigating':
        return <Search className="status-icon" />;
      case 'new':
        return <AlertCircle className="status-icon" />;
      default:
        return <Info className="status-icon" />;
    }
  };

  const getTypeIcon = (type: ProblemSeverity) => {
    switch (type) {
      case 'error':
        return <AlertCircle className="problem-type-icon problem-type-error" />;
      case 'warning':
        return <AlertTriangle className="problem-type-icon problem-type-warning" />;
      case 'info':
        return <Info className="problem-type-icon problem-type-info" />;
      default:
        return <Info className="problem-type-icon" />;
    }
  };

  if (loading.vif || loading.seg) {
    return <PanelLoading message="Loading Problems..." />;
  }

  if (errors.vif || errors.seg) {
    return (
      <div className="problems-error" role="alert">
        <p>Error loading Problems: {errors.vif?.message || errors.seg?.message}</p>
      </div>
    );
  }

  return (
    <div className="problems-panel" role="region" aria-label="Problems Panel">
      {/* Header */}
      <div className="problems-header">
        <div className="problems-header-top">
          <div className="problems-title-section">
            <AlertCircle className="problems-title-icon" />
            <div>
              <h3 className="problems-title">Problems</h3>
              <p className="problems-subtitle">
                Error Tracking • VIF Confidence • Evidence Links • Lifecycle Tracking
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="problems-stats">
          <div className="stat-item">
            <span className="stat-label">Total:</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label stat-error">Errors:</span>
            <span className="stat-value">{stats.errors}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label stat-warning">Warnings:</span>
            <span className="stat-value">{stats.warnings}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label stat-solved">Solved:</span>
            <span className="stat-value">{stats.solved}</span>
          </div>
        </div>

        {/* Filters */}
        <div className="problems-filters">
          <div className="filter-group">
            <label htmlFor="status-filter" className="filter-label">Status:</label>
            <select
              id="status-filter"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as ProblemStatus | 'all')}
              className="filter-select"
              aria-label="Filter by status"
            >
              <option value="all">All</option>
              <option value="new">New</option>
              <option value="investigating">Investigating</option>
              <option value="solved">Solved</option>
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="type-filter" className="filter-label">Type:</label>
            <select
              id="type-filter"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as ProblemSeverity | 'all')}
              className="filter-select"
              aria-label="Filter by type"
            >
              <option value="all">All</option>
              <option value="error">Errors</option>
              <option value="warning">Warnings</option>
              <option value="info">Info</option>
            </select>
          </div>
          <div className="search-group">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search problems..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
              aria-label="Search problems"
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
      </div>

      {/* Problems List */}
      <div className="problems-list">
        {filteredProblems.length === 0 ? (
          <div className="problems-empty">
            <p>No problems found</p>
            <p className="problems-empty-hint">
              {searchQuery || filterStatus !== 'all' || filterType !== 'all'
                ? 'Try adjusting your filters'
                : 'All clear!'}
            </p>
          </div>
        ) : (
          filteredProblems.map((prob) => {
            const isExpanded = expandedProblems.has(prob.id);
            return (
              <div
                key={prob.id}
                className={`problem-item problem-item-${prob.type} problem-item-${prob.status}`}
                role="button"
                tabIndex={0}
                aria-label={`Problem: ${prob.message}`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleExpand(prob.id);
                  }
                }}
              >
                {/* Problem Header */}
                <div
                  className="problem-header"
                  onClick={() => toggleExpand(prob.id)}
                >
                  <div className="problem-header-left">
                    {isExpanded ? (
                      <ChevronDown className="expand-icon" />
                    ) : (
                      <ChevronRight className="expand-icon" />
                    )}
                    {getTypeIcon(prob.type)}
                    <div className="problem-main">
                      <div className="problem-message">{prob.message}</div>
                      <div className="problem-location">
                        {prob.file}:{prob.line}
                        {prob.column && `:${prob.column}`}
                      </div>
                    </div>
                  </div>
                  <div className="problem-header-right">
                    <span className={`status-badge ${getStatusColor(prob.status)}`}>
                      {getStatusIcon(prob.status)}
                      <span>{prob.status}</span>
                    </span>
                    <span className="problem-confidence">
                      Conf: {(prob.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="problem-details">
                    {prob.code && (
                      <div className="problem-code">
                        <div className="problem-code-label">Code:</div>
                        <pre className="problem-code-content">{prob.code}</pre>
                      </div>
                    )}

                    {/* Lifecycle Info */}
                    <div className="problem-lifecycle">
                      <div className="lifecycle-item">
                        <Clock className="lifecycle-icon" />
                        <div>
                          <div className="lifecycle-label">Detected:</div>
                          <div className="lifecycle-value">
                            {new Date(prob.detected).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      {prob.solved && (
                        <div className="lifecycle-item">
                          <CheckCircle className="lifecycle-icon lifecycle-icon-solved" />
                          <div>
                            <div className="lifecycle-label">Solved:</div>
                            <div className="lifecycle-value">
                              {new Date(prob.solved).toLocaleString()}
                            </div>
                          </div>
                        </div>
                      )}
                      {prob.solvedBy && (
                        <div className="lifecycle-item">
                          <User className="lifecycle-icon" />
                          <div>
                            <div className="lifecycle-label">Solved By:</div>
                            <div className="lifecycle-value">{prob.solvedBy}</div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Solution Details */}
                    {prob.solution && (
                      <div className="problem-solution">
                        <div className="solution-header">Solution:</div>
                        <div className="solution-content">{prob.solution}</div>
                      </div>
                    )}

                    {/* AIM-OS Integration */}
                    <div className="problem-aimos">
                      <div className="aimos-header">AIM-OS Integration</div>
                      <div className="aimos-items">
                        {prob.cmcAtom && (
                          <div className="aimos-item">
                            <span className="aimos-label">CMC Atom:</span>
                            <span className="aimos-value">{prob.cmcAtom}</span>
                          </div>
                        )}
                        {prob.vifConfidence !== undefined && (
                          <div className="aimos-item">
                            <span className="aimos-label">VIF Confidence:</span>
                            <span className="aimos-value">{(prob.vifConfidence * 100).toFixed(0)}%</span>
                          </div>
                        )}
                        {prob.segEvidence && prob.segEvidence.length > 0 && (
                          <div className="aimos-item">
                            <span className="aimos-label">SEG Evidence:</span>
                            <span className="aimos-value">{prob.segEvidence.join(', ')}</span>
                          </div>
                        )}
                        {prob.bitemporal && (
                          <div className="aimos-item">
                            <span className="aimos-label">Bitemporal:</span>
                            <span className="aimos-value">
                              {new Date(prob.bitemporal.valid_from).toLocaleString()}
                              {prob.bitemporal.valid_to && (
                                <> → {new Date(prob.bitemporal.valid_to).toLocaleString()}</>
                              )}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
