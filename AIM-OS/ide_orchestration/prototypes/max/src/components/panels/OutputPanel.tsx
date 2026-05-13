// Output Panel - Max V2
// Build output and logs with AIM-OS integration

import React, { useState, useMemo } from 'react';
import { Terminal, AlertCircle, CheckCircle, XCircle, Info, Filter, Refresh } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './OutputPanel.css';

export type OutputLevel = 'all' | 'error' | 'warning' | 'info' | 'success';

export interface OutputEntry {
  id: string;
  level: 'error' | 'warning' | 'info' | 'success';
  message: string;
  timestamp: string;
  source?: string;
  line?: number;
  column?: number;
  confidence?: number;
}

export const OutputPanel: React.FC = () => {
  const { vif, loading, errors } = useAIMOS();
  const [filterLevel, setFilterLevel] = useState<OutputLevel>('all');
  const [autoScroll, setAutoScroll] = useState(true);

  // Mock output entries
  const outputEntries: OutputEntry[] = useMemo(() => [
    {
      id: 'out_1',
      level: 'success',
      message: 'Build completed successfully in 2.3s',
      timestamp: new Date(Date.now() - 5000).toISOString(),
      source: 'build',
      confidence: 0.95,
    },
    {
      id: 'out_2',
      level: 'info',
      message: 'Compiling TypeScript files...',
      timestamp: new Date(Date.now() - 10000).toISOString(),
      source: 'typescript',
      confidence: 0.90,
    },
    {
      id: 'out_3',
      level: 'warning',
      message: 'Unused variable "unusedVar" in src/components/Panel.tsx:45',
      timestamp: new Date(Date.now() - 15000).toISOString(),
      source: 'linter',
      line: 45,
      column: 10,
      confidence: 0.85,
    },
    {
      id: 'out_4',
      level: 'error',
      message: 'Type error: Property "prop" does not exist on type "Props"',
      timestamp: new Date(Date.now() - 20000).toISOString(),
      source: 'typescript',
      line: 12,
      column: 5,
      confidence: 0.95,
    },
    {
      id: 'out_5',
      level: 'info',
      message: 'Starting development server on http://localhost:3000',
      timestamp: new Date(Date.now() - 25000).toISOString(),
      source: 'dev-server',
      confidence: 0.88,
    },
  ], []);

  // Filter output entries
  const filteredEntries = useMemo(() => {
    return outputEntries.filter((entry) => {
      return filterLevel === 'all' || entry.level === filterLevel;
    });
  }, [outputEntries, filterLevel]);

  const getLevelIcon = (level: OutputEntry['level']) => {
    switch (level) {
      case 'error':
        return <XCircle className="output-icon output-icon-error" />;
      case 'warning':
        return <AlertCircle className="output-icon output-icon-warning" />;
      case 'info':
        return <Info className="output-icon output-icon-info" />;
      case 'success':
        return <CheckCircle className="output-icon output-icon-success" />;
      default:
        return <Info className="output-icon" />;
    }
  };

  const getLevelColor = (level: OutputEntry['level']) => {
    switch (level) {
      case 'error':
        return '#f87171';
      case 'warning':
        return '#fbbf24';
      case 'info':
        return '#60a5fa';
      case 'success':
        return '#4ade80';
      default:
        return '#858585';
    }
  };

  if (loading.vif) {
    return <PanelLoading message="Loading Output..." />;
  }

  if (errors.vif) {
    return (
      <div className="output-error" role="alert">
        <p>Error loading Output: {errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="output-panel" role="region" aria-label="Output Panel">
      {/* Header */}
      <div className="output-header">
        <div className="output-header-left">
          <Terminal className="output-header-icon" />
          <div>
            <h3 className="output-header-title">Output</h3>
            <p className="output-header-subtitle">
              Build Output • Logs • Errors • Warnings
            </p>
          </div>
        </div>
        <div className="output-header-right">
          <label className="output-autoscroll">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            <span>Auto-scroll</span>
          </label>
          <button className="output-clear-button" aria-label="Clear output">
            Clear
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="output-filters">
        <div className="output-filter-group">
          <Filter className="output-filter-icon" />
          <span className="output-filter-label">Level:</span>
          {(['all', 'error', 'warning', 'info', 'success'] as OutputLevel[]).map((level) => (
            <button
              key={level}
              className={`output-filter-button ${filterLevel === level ? 'active' : ''}`}
              onClick={() => setFilterLevel(level)}
              aria-label={`Filter by ${level}`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Output List */}
      <div className="output-list" id="output-list">
        {filteredEntries.length === 0 ? (
          <div className="output-empty">
            <Terminal className="output-empty-icon" />
            <p>No output entries</p>
          </div>
        ) : (
          filteredEntries.map((entry) => (
            <div
              key={entry.id}
              className={`output-entry output-entry-${entry.level}`}
              role="log"
            >
              <div className="output-entry-left">
                {getLevelIcon(entry.level)}
                <div className="output-entry-content">
                  <div className="output-entry-message">{entry.message}</div>
                  <div className="output-entry-meta">
                    {entry.source && (
                      <span className="output-entry-source">{entry.source}</span>
                    )}
                    {entry.line !== undefined && entry.column !== undefined && (
                      <span className="output-entry-location">
                        {entry.line}:{entry.column}
                      </span>
                    )}
                    <span className="output-entry-time">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="output-entry-right">
                {entry.confidence !== undefined && (
                  <ConfidenceIndicator confidence={entry.confidence} size="sm" variant="inline" />
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

