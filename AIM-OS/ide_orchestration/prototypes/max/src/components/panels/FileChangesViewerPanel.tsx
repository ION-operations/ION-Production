// File Changes Viewer Panel - Max V2
// File change tracking with AIM-OS integration

import React, { useState, useMemo } from 'react';
import { FileText, Plus, Minus, Edit, Refresh, GitBranch } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './FileChangesViewerPanel.css';

export interface FileChange {
  id: string;
  filePath: string;
  status: 'added' | 'modified' | 'deleted' | 'renamed';
  additions: number;
  deletions: number;
  timestamp: string;
  confidence?: number;
  diff?: string;
}

export const FileChangesViewerPanel: React.FC = () => {
  const { vif, loading, errors } = useAIMOS();
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  // Mock file changes
  const fileChanges: FileChange[] = useMemo(() => [
    {
      id: 'change_1',
      filePath: 'src/components/panels/TerminalPanel.tsx',
      status: 'modified',
      additions: 45,
      deletions: 12,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      confidence: 0.95,
      diff: `+ import { useAIMOS } from '../../hooks/useAIMOS';
+ import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
- import { mockTerminals } from '../../mockData/mockData';
+ // Enhanced terminal panel with AIM-OS integration`,
    },
    {
      id: 'change_2',
      filePath: 'src/components/panels/GitPanel.tsx',
      status: 'added',
      additions: 200,
      deletions: 0,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      confidence: 0.93,
      diff: `+ // Git Panel - Max V2
+ // Version control integration with AIM-OS`,
    },
    {
      id: 'change_3',
      filePath: 'src/components/panels/OutlinePanel.tsx',
      status: 'modified',
      additions: 80,
      deletions: 30,
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      confidence: 0.92,
      diff: `+ // Enhanced Outline Panel with AIM-OS integration
- // Basic outline panel`,
    },
  ], []);

  const selectedFileData = useMemo(() => {
    return selectedFile ? fileChanges.find(f => f.id === selectedFile) : null;
  }, [selectedFile, fileChanges]);

  const getStatusIcon = (status: FileChange['status']) => {
    switch (status) {
      case 'added':
        return <Plus className="file-change-icon file-change-added" />;
      case 'modified':
        return <Edit className="file-change-icon file-change-modified" />;
      case 'deleted':
        return <Minus className="file-change-icon file-change-deleted" />;
      case 'renamed':
        return <FileText className="file-change-icon file-change-renamed" />;
      default:
        return <FileText className="file-change-icon" />;
    }
  };

  const getStatusColor = (status: FileChange['status']) => {
    switch (status) {
      case 'added':
        return '#4ade80';
      case 'modified':
        return '#fbbf24';
      case 'deleted':
        return '#f87171';
      case 'renamed':
        return '#60a5fa';
      default:
        return '#858585';
    }
  };

  if (loading.vif) {
    return <PanelLoading message="Loading File Changes..." />;
  }

  if (errors.vif) {
    return (
      <div className="file-changes-error" role="alert">
        <p>Error loading File Changes: {errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="file-changes-panel" role="region" aria-label="File Changes Viewer Panel">
      {/* Header */}
      <div className="file-changes-header">
        <div className="file-changes-header-left">
          <GitBranch className="file-changes-header-icon" />
          <div>
            <h3 className="file-changes-header-title">File Changes</h3>
            <p className="file-changes-header-subtitle">
              Change Tracking • Diff View • VIF Confidence
            </p>
          </div>
        </div>
        <div className="file-changes-header-right">
          <button className="file-changes-refresh-button" aria-label="Refresh changes">
            <Refresh className="file-changes-icon" />
          </button>
        </div>
      </div>

      {/* File Changes List */}
      <div className="file-changes-list">
        {fileChanges.length === 0 ? (
          <div className="file-changes-empty">
            <FileText className="file-changes-empty-icon" />
            <p>No file changes</p>
          </div>
        ) : (
          fileChanges.map((change) => (
            <div
              key={change.id}
              className={`file-changes-item ${selectedFile === change.id ? 'selected' : ''}`}
              onClick={() => setSelectedFile(selectedFile === change.id ? null : change.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedFile(selectedFile === change.id ? null : change.id);
                }
              }}
            >
              <div className="file-changes-item-header">
                <div className="file-changes-item-left">
                  {getStatusIcon(change.status)}
                  <div className="file-changes-item-info">
                    <div className="file-changes-file-path">{change.filePath}</div>
                    <div className="file-changes-item-meta">
                      <span
                        className="file-changes-status"
                        style={{ color: getStatusColor(change.status) }}
                      >
                        {change.status}
                      </span>
                      <span className="file-changes-stats">
                        +{change.additions} -{change.deletions}
                      </span>
                      <span className="file-changes-time">
                        {new Date(change.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="file-changes-item-right">
                  {change.confidence !== undefined && (
                    <ConfidenceIndicator confidence={change.confidence} size="sm" variant="inline" />
                  )}
                </div>
              </div>

              {selectedFile === change.id && change.diff && (
                <div className="file-changes-diff">
                  <div className="file-changes-diff-header">Diff Preview</div>
                  <pre className="file-changes-diff-content">
                    <code>{change.diff}</code>
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

