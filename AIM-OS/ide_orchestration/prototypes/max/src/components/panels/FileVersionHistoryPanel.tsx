// File Version History Panel - Max V2
// 2 Variants: Simple Dropdown, Scrollable Timeline
// Bitemporal versioning with AIM-OS integration

import React, { useState, useMemo } from 'react';
import { ChevronDown, Clock, User, GitBranch, Eye, FileText, History } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { PanelLoading } from '../Loading/Loading';
import './FileVersionHistoryPanel.css';

export type VersionHistoryVariant = 'dropdown' | 'timeline';

export interface FileVersion {
  version: number;
  timestamp: string;
  agent: string;
  confidence: number;
  changes: {
    added: number;
    removed: number;
    modified: number;
  };
  description: string;
  evidence: string[];
  cmcAtom?: string;
  vifConfidence?: number;
  segEvidence?: string[];
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
  diff?: {
    added: string[];
    removed: string[];
    modified: string[];
  };
}

export interface FileVersionHistoryPanelProps {
  filePath?: string;
}

export const FileVersionHistoryPanel: React.FC<FileVersionHistoryPanelProps> = ({ 
  filePath = 'src/components/IDELayout.tsx' 
}) => {
  const { cmc, loading, errors } = useAIMOS();
  const [variant, setVariant] = useState<VersionHistoryVariant>('dropdown');
  const [selectedVersion, setSelectedVersion] = useState<number>(0);
  const [showDiff, setShowDiff] = useState(false);

  // Mock version history (will be replaced with real CMC bitemporal data)
  const versionHistory: FileVersion[] = useMemo(() => [
    {
      version: 5,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      agent: 'max',
      confidence: 0.95,
      changes: { added: 45, removed: 12, modified: 8 },
      description: 'Added AIM-OS structure panels and hierarchical code explorer',
      evidence: ['atom_500', 'atom_501'],
      cmcAtom: 'atom_500',
      vifConfidence: 0.95,
      segEvidence: ['evidence_node_10'],
      bitemporal: {
        valid_from: new Date(Date.now() - 3600000).toISOString(),
        valid_to: null,
      },
      diff: {
        added: ['+ SuperIndexPanel', '+ MasterIndexPanel', '+ SystemMapPanel', '+ HierarchicalCodeExplorerPanel'],
        removed: ['- Old panel system'],
        modified: ['~ Updated layout structure'],
      },
    },
    {
      version: 4,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      agent: 'max',
      confidence: 0.92,
      changes: { added: 23, removed: 5, modified: 3 },
      description: 'Added debug console panel with AIM-OS integration',
      evidence: ['atom_450', 'atom_451'],
      cmcAtom: 'atom_450',
      vifConfidence: 0.92,
      segEvidence: ['evidence_node_9'],
      bitemporal: {
        valid_from: new Date(Date.now() - 7200000).toISOString(),
        valid_to: new Date(Date.now() - 3600000).toISOString(),
      },
      diff: {
        added: ['+ DebugConsolePanel', '+ Debug infrastructure'],
        removed: [],
        modified: ['~ Enhanced terminal panel'],
      },
    },
    {
      version: 3,
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      agent: 'max',
      confidence: 0.88,
      changes: { added: 15, removed: 2, modified: 1 },
      description: 'Enhanced panels with detailed implementations',
      evidence: ['atom_400'],
      cmcAtom: 'atom_400',
      vifConfidence: 0.88,
      segEvidence: ['evidence_node_8'],
      bitemporal: {
        valid_from: new Date(Date.now() - 10800000).toISOString(),
        valid_to: new Date(Date.now() - 7200000).toISOString(),
      },
      diff: {
        added: ['+ Enhanced panel UI', '+ Mock data integration'],
        removed: [],
        modified: ['~ Panel styling'],
      },
    },
    {
      version: 2,
      timestamp: new Date(Date.now() - 14400000).toISOString(),
      agent: 'max',
      confidence: 0.90,
      changes: { added: 8, removed: 1, modified: 0 },
      description: 'Initial panel implementations',
      evidence: ['atom_350'],
      cmcAtom: 'atom_350',
      vifConfidence: 0.90,
      segEvidence: ['evidence_node_7'],
      bitemporal: {
        valid_from: new Date(Date.now() - 14400000).toISOString(),
        valid_to: new Date(Date.now() - 10800000).toISOString(),
      },
      diff: {
        added: ['+ FileExplorerPanel', '+ ComponentLibraryPanel'],
        removed: [],
        modified: [],
      },
    },
    {
      version: 1,
      timestamp: new Date(Date.now() - 18000000).toISOString(),
      agent: 'max',
      confidence: 0.95,
      changes: { added: 42, removed: 0, modified: 0 },
      description: 'Initial file creation',
      evidence: ['atom_300'],
      cmcAtom: 'atom_300',
      vifConfidence: 0.95,
      segEvidence: ['evidence_node_6'],
      bitemporal: {
        valid_from: new Date(Date.now() - 18000000).toISOString(),
        valid_to: new Date(Date.now() - 14400000).toISOString(),
      },
      diff: {
        added: ['+ Created IDELayout.tsx', '+ Basic structure'],
        removed: [],
        modified: [],
      },
    },
  ], []);

  const currentVersion = versionHistory[selectedVersion];

  if (loading.cmc) {
    return <PanelLoading message="Loading File Version History..." />;
  }

  if (errors.cmc) {
    return (
      <div className="version-history-error" role="alert">
        <p>Error loading File Version History: {errors.cmc.message}</p>
      </div>
    );
  }

  return (
    <div className="file-version-history" role="region" aria-label="File Version History">
      {/* Header */}
      <div className="version-history-header">
        <div className="version-history-header-top">
          <div className="version-history-title">
            <FileText className="version-history-icon" />
            <div>
              <h3 className="version-history-title-text">File Version History</h3>
              <p className="version-history-subtitle">
                {filePath}
              </p>
            </div>
          </div>
        </div>

        {/* Variant Selector */}
        <div className="variant-selector">
          <button
            onClick={() => setVariant('dropdown')}
            className={`variant-button ${variant === 'dropdown' ? 'variant-button-active' : ''}`}
            aria-pressed={variant === 'dropdown'}
            aria-label="Dropdown variant"
          >
            <ChevronDown className="variant-icon" />
            <span>Dropdown</span>
          </button>
          <button
            onClick={() => setVariant('timeline')}
            className={`variant-button ${variant === 'timeline' ? 'variant-button-active' : ''}`}
            aria-pressed={variant === 'timeline'}
            aria-label="Timeline variant"
          >
            <History className="variant-icon" />
            <span>Timeline</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="version-history-content">
        {variant === 'dropdown' ? (
          <>
            {/* Version Dropdown */}
            <div className="version-dropdown-container">
              <select
                value={selectedVersion}
                onChange={(e) => setSelectedVersion(Number(e.target.value))}
                className="version-dropdown"
                aria-label="Select version"
              >
                {versionHistory.map((version, idx) => (
                  <option key={version.version} value={idx}>
                    Version {version.version} • {new Date(version.timestamp).toLocaleString()} • {version.description}
                  </option>
                ))}
              </select>
              <ChevronDown className="dropdown-chevron" />
            </div>

            {/* Version Details */}
            <div className="version-details">
              <div className="version-info-card">
                <div className="version-info-header">
                  <div className="version-info-title">
                    Version {currentVersion.version}
                    {selectedVersion === 0 && (
                      <span className="version-badge version-badge-current">Current</span>
                    )}
                  </div>
                  <div className="version-confidence">
                    Conf: {(currentVersion.confidence * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="version-meta">
                  <div className="version-meta-item">
                    <Clock className="version-meta-icon" />
                    <span>{new Date(currentVersion.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="version-meta-item">
                    <User className="version-meta-icon" />
                    <span>{currentVersion.agent}</span>
                  </div>
                  <div className="version-description">{currentVersion.description}</div>
                </div>
              </div>

              {/* Changes Summary */}
              <div className="changes-summary">
                <div className="changes-header">Changes</div>
                <div className="changes-stats">
                  <div className="change-stat change-stat-added">
                    <span className="change-count">+{currentVersion.changes.added}</span>
                    <span className="change-label">added</span>
                  </div>
                  <div className="change-stat change-stat-removed">
                    <span className="change-count">-{currentVersion.changes.removed}</span>
                    <span className="change-label">removed</span>
                  </div>
                  <div className="change-stat change-stat-modified">
                    <span className="change-count">~{currentVersion.changes.modified}</span>
                    <span className="change-label">modified</span>
                  </div>
                </div>
              </div>

              {/* Diff View Toggle */}
              <div className="diff-toggle">
                <button
                  onClick={() => setShowDiff(!showDiff)}
                  className={`diff-toggle-button ${showDiff ? 'diff-toggle-active' : ''}`}
                  aria-pressed={showDiff}
                  aria-label={showDiff ? 'Hide diff' : 'Show diff'}
                >
                  <Eye className="diff-toggle-icon" />
                  {showDiff ? 'Hide' : 'Show'} Diff
                </button>
              </div>

              {/* Diff View */}
              {showDiff && currentVersion.diff && (
                <div className="diff-view">
                  <div className="diff-header">Diff View</div>
                  <div className="diff-content">
                    {currentVersion.diff.added.map((line, idx) => (
                      <div key={`added-${idx}`} className="diff-line diff-line-added">
                        {line}
                      </div>
                    ))}
                    {currentVersion.diff.removed.map((line, idx) => (
                      <div key={`removed-${idx}`} className="diff-line diff-line-removed">
                        {line}
                      </div>
                    ))}
                    {currentVersion.diff.modified.map((line, idx) => (
                      <div key={`modified-${idx}`} className="diff-line diff-line-modified">
                        {line}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AIM-OS Integration */}
              <div className="aimos-integration">
                <div className="aimos-header">AIM-OS Integration</div>
                <div className="aimos-items">
                  {currentVersion.cmcAtom && (
                    <div className="aimos-item">
                      <span className="aimos-label">CMC Atom:</span>
                      <span className="aimos-value">{currentVersion.cmcAtom}</span>
                    </div>
                  )}
                  {currentVersion.vifConfidence !== undefined && (
                    <div className="aimos-item">
                      <span className="aimos-label">VIF Confidence:</span>
                      <span className="aimos-value">{(currentVersion.vifConfidence * 100).toFixed(0)}%</span>
                    </div>
                  )}
                  {currentVersion.segEvidence && currentVersion.segEvidence.length > 0 && (
                    <div className="aimos-item">
                      <span className="aimos-label">SEG Evidence:</span>
                      <span className="aimos-value">{currentVersion.segEvidence.join(', ')}</span>
                    </div>
                  )}
                  {currentVersion.bitemporal && (
                    <div className="aimos-item">
                      <span className="aimos-label">Bitemporal:</span>
                      <span className="aimos-value">
                        {new Date(currentVersion.bitemporal.valid_from).toLocaleString()}
                        {currentVersion.bitemporal.valid_to && (
                          <> → {new Date(currentVersion.bitemporal.valid_to).toLocaleString()}</>
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Version Timeline */}
              <div className="version-timeline">
                <div className="timeline-header">All Versions</div>
                <div className="timeline-list">
                  {versionHistory.map((version, idx) => (
                    <div
                      key={version.version}
                      className={`timeline-item ${idx === selectedVersion ? 'timeline-item-selected' : ''}`}
                      onClick={() => setSelectedVersion(idx)}
                      role="button"
                      tabIndex={0}
                      aria-label={`Version ${version.version}: ${version.description}`}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          setSelectedVersion(idx);
                        }
                      }}
                    >
                      <div className="timeline-item-header">
                        <div className="timeline-item-title">
                          Version {version.version}
                          {idx === 0 && (
                            <span className="version-badge version-badge-current">Current</span>
                          )}
                        </div>
                        <div className="timeline-item-time">
                          {new Date(version.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                      <div className="timeline-item-description">{version.description}</div>
                      <div className="timeline-item-changes">
                        <span className="change-added">+{version.changes.added}</span>
                        <span className="change-removed">-{version.changes.removed}</span>
                        <span className="change-modified">~{version.changes.modified}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Timeline Variant */}
            <div className="timeline-variant-grid">
              {/* Version Timeline (Scrollable) */}
              <div className="timeline-column">
                <div className="timeline-column-header">Timeline</div>
                <div className="timeline-scrollable">
                  {versionHistory.map((version, idx) => (
                    <div
                      key={version.version}
                      className={`timeline-card ${idx === selectedVersion ? 'timeline-card-selected' : ''}`}
                      onClick={() => setSelectedVersion(idx)}
                      role="button"
                      tabIndex={0}
                      aria-label={`Version ${version.version}: ${version.description}`}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          setSelectedVersion(idx);
                        }
                      }}
                    >
                      <div className="timeline-card-header">
                        <div className="timeline-card-version">v{version.version}</div>
                        {idx === 0 && (
                          <span className="version-badge version-badge-current">Current</span>
                        )}
                      </div>
                      <div className="timeline-card-time">
                        {new Date(version.timestamp).toLocaleTimeString()}
                      </div>
                      <div className="timeline-card-description">{version.description}</div>
                      <div className="timeline-card-changes">
                        <span className="change-added">+{version.changes.added}</span>
                        <span className="change-removed">-{version.changes.removed}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Version Details */}
              <div className="details-column">
                <div className="version-info-card">
                  <div className="version-info-header">
                    <div className="version-info-title">
                      Version {currentVersion.version}
                    </div>
                    <div className="version-confidence">
                      Conf: {(currentVersion.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="version-meta">
                    <div>{new Date(currentVersion.timestamp).toLocaleString()}</div>
                    <div>{currentVersion.agent}</div>
                    <div className="version-description">{currentVersion.description}</div>
                  </div>
                </div>

                {/* Diff View */}
                <div className="diff-view">
                  <div className="diff-header-row">
                    <div className="diff-header">Changes</div>
                    <button
                      onClick={() => setShowDiff(!showDiff)}
                      className="diff-toggle-link"
                      aria-pressed={showDiff}
                      aria-label={showDiff ? 'Hide diff' : 'Show diff'}
                    >
                      {showDiff ? 'Hide' : 'Show'} Diff
                    </button>
                  </div>
                  {showDiff && currentVersion.diff && (
                    <div className="diff-content">
                      {currentVersion.diff.added.map((line, idx) => (
                        <div key={`added-${idx}`} className="diff-line diff-line-added">
                          {line}
                        </div>
                      ))}
                      {currentVersion.diff.removed.map((line, idx) => (
                        <div key={`removed-${idx}`} className="diff-line diff-line-removed">
                          {line}
                        </div>
                      ))}
                      {currentVersion.diff.modified.map((line, idx) => (
                        <div key={`modified-${idx}`} className="diff-line diff-line-modified">
                          {line}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

