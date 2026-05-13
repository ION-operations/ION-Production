// Debug Console Panel - Max V2
// AIM-OS Native Debugging Infrastructure
// Built in tandem with application - never an afterthought

import React, { useState, useMemo } from 'react';
import { Bug, Filter, Search, AlertCircle, Info, AlertTriangle, XCircle } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { useBitemporal } from '../../hooks/useBitemporal';
import { BitemporalDisplay } from '../BitemporalDisplay/BitemporalDisplay';
import { BitemporalTimeTravel } from '../BitemporalTimeTravel/BitemporalTimeTravel';
import { PanelLoading } from '../Loading/Loading';
import './DebugConsolePanel.css';

export interface DebugLogEntry {
  id: string;
  level: 'log' | 'info' | 'warn' | 'error' | 'debug';
  source: string;
  message: string;
  timestamp: string;
  confidence: number;
  evidence: string[];
  context?: Record<string, any>;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
}

export interface DebugInfrastructure {
  logging: {
    enabled: boolean;
    level: 'debug' | 'info' | 'warn' | 'error';
    destinations: string[];
    rotation: string;
    retention: string;
    confidence: number;
  };
  analysis: {
    enabled: boolean;
    real_time: boolean;
    pattern_detection: boolean;
    insight_generation: boolean;
    confidence: number;
  };
  integration: {
    cmc: { enabled: boolean; all_logs_stored: boolean; bitemporal: boolean };
    hhni: { enabled: boolean; semantic_analysis: boolean; pattern_detection: boolean };
    vif: { enabled: boolean; confidence_tracking: boolean; validation: boolean };
    seg: { enabled: boolean; evidence_trails: boolean; contradiction_detection: boolean };
    apoe: { enabled: boolean; task_debugging: boolean; orchestration_logs: boolean };
    sdfcvf: { enabled: boolean; quality_tracking: boolean; improvement_logs: boolean };
    cas: { enabled: boolean; consciousness_debugging: boolean; drift_logs: boolean };
    tcs: { enabled: boolean; timeline_debugging: boolean; context_logs: boolean };
  };
}

export interface DebugAnalysis {
  patterns: Array<{
    pattern: string;
    count: number;
    systems: string[];
    confidence: number;
    evidence: string[];
  }>;
  insights: Array<{
    insight: string;
    confidence: number;
    evidence: string[];
    recommendation?: string;
  }>;
}

export const DebugConsolePanel: React.FC = () => {
  const { cmc, loading, errors } = useAIMOS();
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  const [filterLevel, setFilterLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock debug logs (will be replaced with real AIM-OS data)
  const mockDebugLogs: DebugLogEntry[] = useMemo(() => [
    {
      id: 'debug_1',
      level: 'log',
      source: 'IDELayout',
      message: 'Component mounted successfully',
      timestamp: new Date().toISOString(),
      confidence: 0.95,
      evidence: ['atom_123'],
      context: { component: 'Layout', props: {} },
      bitemporal: { valid_from: new Date().toISOString(), valid_to: null },
    },
    {
      id: 'debug_2',
      level: 'info',
      source: 'CMC',
      message: 'Atom created: file_operation',
      timestamp: new Date(Date.now() - 5000).toISOString(),
      confidence: 0.98,
      evidence: ['atom_124'],
      context: { atom_id: 'atom_124', operation: 'file_read', file: 'Layout.tsx' },
      bitemporal: { valid_from: new Date(Date.now() - 5000).toISOString(), valid_to: null },
    },
    {
      id: 'debug_3',
      level: 'warn',
      source: 'VIF',
      message: 'Confidence below threshold: 0.65',
      timestamp: new Date(Date.now() - 10000).toISOString(),
      confidence: 0.65,
      evidence: ['atom_125'],
      context: { threshold: 0.70, system: 'HHNI', operation: 'semantic_search' },
      bitemporal: { valid_from: new Date(Date.now() - 10000).toISOString(), valid_to: null },
    },
    {
      id: 'debug_4',
      level: 'error',
      source: 'APOE',
      message: 'Task dependency resolution failed',
      timestamp: new Date(Date.now() - 15000).toISOString(),
      confidence: 0.88,
      evidence: ['atom_126'],
      context: { task_id: 'task_42', dependency: 'task_41', reason: 'circular_dependency' },
      bitemporal: { valid_from: new Date(Date.now() - 15000).toISOString(), valid_to: null },
    },
  ], []);

  // Group logs by system
  const logsBySystem = useMemo(() => {
    const grouped: Record<string, DebugLogEntry[]> = {};
    mockDebugLogs.forEach((log) => {
      if (!grouped[log.source]) {
        grouped[log.source] = [];
      }
      grouped[log.source].push(log);
    });
    return grouped;
  }, [mockDebugLogs]);

  // Mock infrastructure status
  const infrastructure: DebugInfrastructure = useMemo(() => ({
    logging: {
      enabled: true,
      level: 'debug',
      destinations: ['CMC', 'Console', 'File'],
      rotation: 'daily',
      retention: '30 days',
      confidence: 0.98,
    },
    analysis: {
      enabled: true,
      real_time: true,
      pattern_detection: true,
      insight_generation: true,
      confidence: 0.92,
    },
    integration: {
      cmc: { enabled: true, all_logs_stored: true, bitemporal: true },
      hhni: { enabled: true, semantic_analysis: true, pattern_detection: true },
      vif: { enabled: true, confidence_tracking: true, validation: true },
      seg: { enabled: true, evidence_trails: true, contradiction_detection: true },
      apoe: { enabled: true, task_debugging: true, orchestration_logs: true },
      sdfcvf: { enabled: true, quality_tracking: true, improvement_logs: true },
      cas: { enabled: true, consciousness_debugging: true, drift_logs: true },
      tcs: { enabled: true, timeline_debugging: true, context_logs: true },
    },
  }), []);

  // Mock analysis
  const analysis: DebugAnalysis = useMemo(() => ({
    patterns: [
      {
        pattern: 'High confidence operations',
        count: 2345,
        systems: ['CMC', 'TCS', 'CAS'],
        confidence: 0.94,
        evidence: ['atom_200', 'atom_201'],
      },
      {
        pattern: 'Low confidence warnings',
        count: 45,
        systems: ['VIF', 'HHNI'],
        confidence: 0.68,
        evidence: ['atom_202', 'atom_203'],
      },
    ],
    insights: [
      {
        insight: 'CMC operations have highest confidence',
        confidence: 0.95,
        evidence: ['atom_205'],
        recommendation: 'Continue CMC-first approach',
      },
      {
        insight: 'VIF warnings correlate with HHNI low confidence',
        confidence: 0.87,
        evidence: ['atom_206'],
        recommendation: 'Investigate HHNI confidence calibration',
      },
    ],
  }), []);

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'error':
        return <XCircle className="w-4 h-4" />;
      case 'warn':
        return <AlertTriangle className="w-4 h-4" />;
      case 'info':
        return <Info className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-400';
      case 'warn':
        return 'text-yellow-400';
      case 'info':
        return 'text-blue-400';
      case 'log':
        return 'text-gray-300';
      case 'debug':
        return 'text-purple-400';
      default:
        return 'text-gray-400';
    }
  };

  const getLevelBg = (level: string) => {
    switch (level) {
      case 'error':
        return 'bg-red-900/30 border-red-700';
      case 'warn':
        return 'bg-yellow-900/30 border-yellow-700';
      case 'info':
        return 'bg-blue-900/30 border-blue-700';
      case 'log':
        return 'bg-gray-800 border-gray-700';
      case 'debug':
        return 'bg-purple-900/30 border-purple-700';
      default:
        return 'bg-gray-800 border-gray-700';
    }
  };

  const filteredConsole = useMemo(() => {
    return mockDebugLogs.filter((entry) => {
      if (filterLevel !== 'all' && entry.level !== filterLevel) return false;
      if (searchQuery && !entry.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      if (selectedSystem && entry.source !== selectedSystem) return false;
      return true;
    });
  }, [mockDebugLogs, filterLevel, searchQuery, selectedSystem]);

  if (loading.cmc) {
    return <PanelLoading message="Loading debug console..." />;
  }

  if (errors.cmc) {
    return (
      <div className="debug-console-error" role="alert">
        <p>Error loading debug console: {errors.cmc.message}</p>
      </div>
    );
  }

  return (
    <div className="debug-console" role="region" aria-label="Debug Console">
      {/* Header */}
      <div className="debug-console-header">
        <div className="debug-console-header-top">
          <div className="debug-console-title">
            <Bug className="debug-console-icon" />
            <div>
              <h3 className="debug-console-title-text">Debug Console</h3>
              <p className="debug-console-subtitle">
                AIM-OS Native Debugging • CMC-Backed Logs • HHNI Analysis • VIF Validation
              </p>
            </div>
          </div>
          <div className="debug-console-status">
            <div className="status-indicator">
              <div className="status-dot status-dot-active" aria-label="Infrastructure active" />
              <span>Infrastructure: Active</span>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="debug-console-filters">
          <div className="filter-group">
            <Filter className="filter-icon" />
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="filter-select"
              aria-label="Filter by log level"
            >
              <option value="all">All Levels</option>
              <option value="log">Log</option>
              <option value="info">Info</option>
              <option value="warn">Warn</option>
              <option value="error">Error</option>
              <option value="debug">Debug</option>
            </select>
          </div>
          <div className="filter-group filter-search">
            <Search className="filter-icon" />
            <input
              type="search"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="filter-input"
              aria-label="Search debug logs"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="debug-console-content">
        <div className="debug-console-grid">
          {/* Console Logs */}
          <div className="debug-console-logs">
            <div className="debug-console-logs-header">
              <div className="logs-title">Console Logs ({filteredConsole.length})</div>
              <div className="logs-badges">
                <span>CMC-Backed</span>
                <span>•</span>
                <span>Bitemporal</span>
                <span>•</span>
                <span>Evidence-Linked</span>
              </div>
            </div>
            <div className="logs-list" role="log" aria-live="polite">
              {filteredConsole.length === 0 ? (
                <div className="logs-empty">No logs match the current filters</div>
              ) : (
                filteredConsole.map((entry) => (
                  <div
                    key={entry.id}
                    className={`log-entry ${getLevelBg(entry.level)}`}
                    role="listitem"
                  >
                    <div className="log-entry-header">
                      <div className="log-entry-meta">
                        <span className={`log-level ${getLevelColor(entry.level)}`}>
                          {getLevelIcon(entry.level)}
                          [{entry.level.toUpperCase()}]
                        </span>
                        <span className="log-source">{entry.source}</span>
                      </div>
                      <div className="log-entry-info">
                        <span className="log-confidence">
                          Conf: {(entry.confidence * 100).toFixed(0)}%
                        </span>
                        <span className="log-timestamp">
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    <div className="log-message">{entry.message}</div>
                    {entry.context && (
                      <details className="log-context">
                        <summary>Context</summary>
                        <pre className="log-context-content">
                          {JSON.stringify(entry.context, null, 2)}
                        </pre>
                      </details>
                    )}
                    {entry.evidence && entry.evidence.length > 0 && (
                      <div className="log-evidence">
                        <span className="log-evidence-label">Evidence:</span>
                        <span className="log-evidence-ids">{entry.evidence.join(', ')}</span>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="debug-console-sidebar">
            {/* System Logs */}
            <div className="sidebar-section">
              <h4 className="sidebar-title">By System</h4>
              <div className="system-list" role="list">
                {Object.entries(logsBySystem).map(([system, logs]) => (
                  <button
                    key={system}
                    onClick={() => setSelectedSystem(selectedSystem === system ? null : system)}
                    className={`system-button ${selectedSystem === system ? 'system-button-active' : ''}`}
                    aria-pressed={selectedSystem === system}
                    aria-label={`Filter by ${system} system`}
                  >
                    <span>{system}</span>
                    <span className="system-count">{logs.length}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Infrastructure Status */}
            <div className="sidebar-section">
              <h4 className="sidebar-title">Infrastructure</h4>
              <div className="infrastructure-list">
                <div className="infrastructure-item">
                  <span>Logging</span>
                  <span className={infrastructure.logging.enabled ? 'status-enabled' : 'status-disabled'}>
                    {infrastructure.logging.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="infrastructure-item">
                  <span>Analysis</span>
                  <span className={infrastructure.analysis.enabled ? 'status-enabled' : 'status-disabled'}>
                    {infrastructure.analysis.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="infrastructure-item">
                  <span>CMC Integration</span>
                  <span className={infrastructure.integration.cmc.enabled ? 'status-enabled' : 'status-disabled'}>
                    {infrastructure.integration.cmc.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="infrastructure-item">
                  <span>HHNI Analysis</span>
                  <span className={infrastructure.integration.hhni.enabled ? 'status-enabled' : 'status-disabled'}>
                    {infrastructure.integration.hhni.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="infrastructure-item">
                  <span>VIF Tracking</span>
                  <span className={infrastructure.integration.vif.enabled ? 'status-enabled' : 'status-disabled'}>
                    {infrastructure.integration.vif.enabled ? '✓' : '✗'}
                  </span>
                </div>
                <div className="infrastructure-item">
                  <span>SEG Evidence</span>
                  <span className={infrastructure.integration.seg.enabled ? 'status-enabled' : 'status-disabled'}>
                    {infrastructure.integration.seg.enabled ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            </div>

            {/* Analysis Insights */}
            <div className="sidebar-section">
              <h4 className="sidebar-title">Insights</h4>
              <div className="insights-list">
                {analysis.insights.slice(0, 3).map((insight, idx) => (
                  <div key={idx} className="insight-item">
                    <div className="insight-text">{insight.insight}</div>
                    <div className="insight-meta">
                      Conf: {(insight.confidence * 100).toFixed(0)}%
                    </div>
                    {insight.recommendation && (
                      <div className="insight-recommendation">{insight.recommendation}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

