// Git Panel - Max V2
// Version control integration with AIM-OS (CMC, VIF, SEG, bitemporal)

import React, { useState, useMemo } from 'react';
import { GitBranch, GitCommit, GitMerge, Plus, Refresh, CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { ContradictionAlert } from '../ContradictionAlert/ContradictionAlert';
import { EvidenceTrailDisplay } from '../EvidenceTrailDisplay/EvidenceTrailDisplay';
import { BitemporalDisplay } from '../BitemporalDisplay/BitemporalDisplay';
import { PanelLoading } from '../Loading/Loading';
import { createEvidenceTrail, createCMCAtomLink, createVIFWitnessLink } from '../../utils/evidence';
import { createBitemporalMetadata } from '../../utils/bitemporal';
import './GitPanel.css';

export type GitTab = 'status' | 'commits' | 'branches' | 'history';

export interface GitFileChange {
  path: string;
  status: 'modified' | 'added' | 'deleted' | 'renamed';
  additions?: number;
  deletions?: number;
  confidence?: number;
  evidenceTrail?: any;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
}

export interface GitCommit {
  hash: string;
  shortHash: string;
  message: string;
  author: string;
  email: string;
  timestamp: string;
  files: GitFileChange[];
  confidence?: number;
  evidenceTrail?: any;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
  contradictions?: number;
}

export interface GitBranch {
  name: string;
  current: boolean;
  ahead: number;
  behind: number;
  lastCommit: string;
  confidence?: number;
}

export interface GitStatus {
  branch: string;
  ahead: number;
  behind: number;
  changes: {
    modified: GitFileChange[];
    added: GitFileChange[];
    deleted: GitFileChange[];
    renamed: GitFileChange[];
  };
  confidence?: number;
}

export const GitPanel: React.FC = () => {
  const { cmc, vif, seg, loading, errors } = useAIMOS();
  const [activeTab, setActiveTab] = useState<GitTab>('status');
  const [selectedCommit, setSelectedCommit] = useState<string | null>(null);

  // Mock Git status
  const gitStatus: GitStatus = useMemo(() => ({
    branch: 'main',
    ahead: 2,
    behind: 0,
    changes: {
      modified: [
        {
          path: 'src/components/panels/TerminalPanel.tsx',
          status: 'modified',
          additions: 45,
          deletions: 12,
          confidence: 0.92,
          bitemporal: createBitemporalMetadata(),
        },
        {
          path: 'src/store/panelStore.ts',
          status: 'modified',
          additions: 8,
          deletions: 3,
          confidence: 0.88,
          bitemporal: createBitemporalMetadata(),
        },
      ],
      added: [
        {
          path: 'src/components/panels/GitPanel.tsx',
          status: 'added',
          additions: 200,
          confidence: 0.90,
          bitemporal: createBitemporalMetadata(),
        },
      ],
      deleted: [],
      renamed: [],
    },
    confidence: 0.90,
  }), []);

  // Mock commits
  const commits: GitCommit[] = useMemo(() => [
    {
      hash: 'a1b2c3d4e5f6',
      shortHash: 'a1b2c3d',
      message: 'Add Terminal Panel with AIM-OS integration',
      author: 'max',
      email: 'max@aimos.dev',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      files: [
        {
          path: 'src/components/panels/TerminalPanel.tsx',
          status: 'added',
          additions: 300,
          confidence: 0.95,
          bitemporal: createBitemporalMetadata(),
        },
      ],
      confidence: 0.95,
      evidenceTrail: createEvidenceTrail('Commit: Add Terminal Panel', [
        createCMCAtomLink('atom_terminal_001', 0.95, 'Terminal panel stored in CMC'),
        createVIFWitnessLink('witness_terminal_001', 0.95, 'VIF witness for terminal implementation'),
      ]),
      bitemporal: createBitemporalMetadata(),
      contradictions: 0,
    },
    {
      hash: 'e4f5g6h7i8j9',
      shortHash: 'e4f5g6h',
      message: 'Enhance Problems Panel with lifecycle tracking',
      author: 'max',
      email: 'max@aimos.dev',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      files: [
        {
          path: 'src/components/panels/ProblemsPanel.tsx',
          status: 'modified',
          additions: 150,
          deletions: 50,
          confidence: 0.92,
          bitemporal: createBitemporalMetadata(),
        },
      ],
      confidence: 0.92,
      evidenceTrail: createEvidenceTrail('Commit: Enhance Problems Panel', [
        createCMCAtomLink('atom_problems_001', 0.92, 'Problems panel enhancement stored in CMC'),
      ]),
      bitemporal: createBitemporalMetadata(),
      contradictions: 0,
    },
    {
      hash: 'k0l1m2n3o4p5',
      shortHash: 'k0l1m2n',
      message: 'Implement Context Web panel',
      author: 'max',
      email: 'max@aimos.dev',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      files: [
        {
          path: 'src/components/panels/ContextWebPanel.tsx',
          status: 'added',
          additions: 400,
          confidence: 0.90,
          bitemporal: createBitemporalMetadata(),
        },
      ],
      confidence: 0.90,
      evidenceTrail: createEvidenceTrail('Commit: Implement Context Web', [
        createCMCAtomLink('atom_context_web_001', 0.90, 'Context Web panel stored in CMC'),
      ]),
      bitemporal: createBitemporalMetadata(),
      contradictions: 0,
    },
  ], []);

  // Mock branches
  const branches: GitBranch[] = useMemo(() => [
    {
      name: 'main',
      current: true,
      ahead: 2,
      behind: 0,
      lastCommit: 'a1b2c3d',
      confidence: 0.95,
    },
    {
      name: 'feature/bitemporal-support',
      current: false,
      ahead: 5,
      behind: 2,
      lastCommit: 'x9y8z7w',
      confidence: 0.88,
    },
    {
      name: 'feature/evidence-trails',
      current: false,
      ahead: 3,
      behind: 1,
      lastCommit: 'v6u5t4s',
      confidence: 0.90,
    },
  ], []);

  const totalChanges = useMemo(() => {
    return (
      gitStatus.changes.modified.length +
      gitStatus.changes.added.length +
      gitStatus.changes.deleted.length +
      gitStatus.changes.renamed.length
    );
  }, [gitStatus]);

  const selectedCommitData = useMemo(() => {
    return selectedCommit ? commits.find(c => c.hash === selectedCommit || c.shortHash === selectedCommit) : null;
  }, [selectedCommit, commits]);

  const totalContradictions = useMemo(() => {
    return commits.reduce((sum, commit) => sum + (commit.contradictions || 0), 0);
  }, [commits]);

  if (loading.cmc || loading.vif || loading.seg) {
    return <PanelLoading message="Loading Git..." />;
  }

  if (errors.cmc || errors.vif || errors.seg) {
    return (
      <div className="git-error" role="alert">
        <p>Error loading Git: {errors.cmc?.message || errors.vif?.message || errors.seg?.message}</p>
      </div>
    );
  }

  return (
    <div className="git-panel" role="region" aria-label="Git Panel">
      {/* Header */}
      <div className="git-header">
        <div className="git-header-left">
          <GitBranch className="git-header-icon" />
          <div>
            <h3 className="git-header-title">Git</h3>
            <p className="git-header-subtitle">
              Version Control • CMC-Backed • VIF Confidence • Evidence Trails
            </p>
          </div>
        </div>
        <div className="git-header-right">
          {totalContradictions > 0 && (
            <ContradictionAlert count={totalContradictions} />
          )}
          {gitStatus.confidence !== undefined && (
            <ConfidenceIndicator confidence={gitStatus.confidence} size="sm" variant="inline" />
          )}
          <button className="git-refresh-button" aria-label="Refresh Git status">
            <Refresh className="git-refresh-icon" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="git-tabs" role="tablist">
        {(['status', 'commits', 'branches', 'history'] as GitTab[]).map((tab) => (
          <button
            key={tab}
            className={`git-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
            role="tab"
            aria-selected={activeTab === tab}
            aria-controls={`git-tabpanel-${tab}`}
          >
            {tab === 'status' && <GitBranch className="git-tab-icon" />}
            {tab === 'commits' && <GitCommit className="git-tab-icon" />}
            {tab === 'branches' && <GitMerge className="git-tab-icon" />}
            {tab === 'history' && <Clock className="git-tab-icon" />}
            <span className="git-tab-label">{tab.charAt(0).toUpperCase() + tab.slice(1)}</span>
            {tab === 'status' && totalChanges > 0 && (
              <span className="git-tab-badge">{totalChanges}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="git-content">
        {/* Status Tab */}
        {activeTab === 'status' && (
          <div className="git-tabpanel" id="git-tabpanel-status" role="tabpanel">
            <div className="git-status-section">
              <div className="git-status-header">
                <GitBranch className="git-status-icon" />
                <div className="git-status-info">
                  <div className="git-status-branch">{gitStatus.branch}</div>
                  <div className="git-status-meta">
                    {gitStatus.ahead > 0 && (
                      <span className="git-status-ahead">
                        {gitStatus.ahead} ahead
                      </span>
                    )}
                    {gitStatus.behind > 0 && (
                      <span className="git-status-behind">
                        {gitStatus.behind} behind
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Changes */}
              <div className="git-changes">
                {gitStatus.changes.modified.length > 0 && (
                  <div className="git-change-group">
                    <div className="git-change-group-header">
                      <span className="git-change-group-title">Modified ({gitStatus.changes.modified.length})</span>
                    </div>
                    {gitStatus.changes.modified.map((file, index) => (
                      <div key={index} className="git-change-item">
                        <div className="git-change-item-left">
                          <XCircle className="git-change-icon git-change-modified" />
                          <span className="git-change-path">{file.path}</span>
                        </div>
                        <div className="git-change-item-right">
                          {file.additions && file.deletions && (
                            <span className="git-change-stats">
                              +{file.additions} -{file.deletions}
                            </span>
                          )}
                          {file.confidence !== undefined && (
                            <ConfidenceIndicator confidence={file.confidence} size="sm" variant="inline" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {gitStatus.changes.added.length > 0 && (
                  <div className="git-change-group">
                    <div className="git-change-group-header">
                      <span className="git-change-group-title">Added ({gitStatus.changes.added.length})</span>
                    </div>
                    {gitStatus.changes.added.map((file, index) => (
                      <div key={index} className="git-change-item">
                        <div className="git-change-item-left">
                          <CheckCircle className="git-change-icon git-change-added" />
                          <span className="git-change-path">{file.path}</span>
                        </div>
                        <div className="git-change-item-right">
                          {file.additions && (
                            <span className="git-change-stats">+{file.additions}</span>
                          )}
                          {file.confidence !== undefined && (
                            <ConfidenceIndicator confidence={file.confidence} size="sm" variant="inline" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {gitStatus.changes.deleted.length > 0 && (
                  <div className="git-change-group">
                    <div className="git-change-group-header">
                      <span className="git-change-group-title">Deleted ({gitStatus.changes.deleted.length})</span>
                    </div>
                    {gitStatus.changes.deleted.map((file, index) => (
                      <div key={index} className="git-change-item">
                        <div className="git-change-item-left">
                          <XCircle className="git-change-icon git-change-deleted" />
                          <span className="git-change-path">{file.path}</span>
                        </div>
                        <div className="git-change-item-right">
                          {file.confidence !== undefined && (
                            <ConfidenceIndicator confidence={file.confidence} size="sm" variant="inline" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {totalChanges === 0 && (
                  <div className="git-empty">
                    <CheckCircle className="git-empty-icon" />
                    <p>Working tree clean</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Commits Tab */}
        {activeTab === 'commits' && (
          <div className="git-tabpanel" id="git-tabpanel-commits" role="tabpanel">
            <div className="git-commits">
              {commits.map((commit) => (
                <div
                  key={commit.hash}
                  className={`git-commit-item ${selectedCommit === commit.hash || selectedCommit === commit.shortHash ? 'selected' : ''}`}
                  onClick={() => setSelectedCommit(selectedCommit === commit.hash ? null : commit.hash)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setSelectedCommit(selectedCommit === commit.hash ? null : commit.hash);
                    }
                  }}
                >
                  <div className="git-commit-header">
                    <div className="git-commit-header-left">
                      <GitCommit className="git-commit-icon" />
                      <div className="git-commit-info">
                        <div className="git-commit-message">{commit.message}</div>
                        <div className="git-commit-meta">
                          <span className="git-commit-hash">{commit.shortHash}</span>
                          <span className="git-commit-author">{commit.author}</span>
                          <span className="git-commit-time">
                            {new Date(commit.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="git-commit-header-right">
                      {commit.contradictions && commit.contradictions > 0 && (
                        <ContradictionAlert count={commit.contradictions} severity="high" />
                      )}
                      {commit.confidence !== undefined && (
                        <ConfidenceIndicator confidence={commit.confidence} size="sm" variant="inline" />
                      )}
                    </div>
                  </div>

                  {selectedCommit === commit.hash && (
                    <div className="git-commit-details">
                      {/* Files */}
                      <div className="git-commit-section">
                        <div className="git-commit-section-header">Files Changed ({commit.files.length})</div>
                        {commit.files.map((file, index) => (
                          <div key={index} className="git-commit-file">
                            <span className="git-commit-file-status">{file.status}</span>
                            <span className="git-commit-file-path">{file.path}</span>
                            {file.additions && file.deletions && (
                              <span className="git-commit-file-stats">
                                +{file.additions} -{file.deletions}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* AIM-OS Integration */}
                      <div className="git-commit-section">
                        <div className="git-commit-section-header">AIM-OS Integration</div>
                        {commit.evidenceTrail && (
                          <EvidenceTrailDisplay trail={commit.evidenceTrail} compact={true} />
                        )}
                        {commit.bitemporal && (
                          <BitemporalDisplay bitemporal={commit.bitemporal} compact={true} />
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Branches Tab */}
        {activeTab === 'branches' && (
          <div className="git-tabpanel" id="git-tabpanel-branches" role="tabpanel">
            <div className="git-branches-header">
              <button className="git-branch-new-button">
                <Plus className="git-branch-new-icon" />
                <span>New Branch</span>
              </button>
            </div>
            <div className="git-branches">
              {branches.map((branch) => (
                <div
                  key={branch.name}
                  className={`git-branch-item ${branch.current ? 'current' : ''}`}
                >
                  <div className="git-branch-item-left">
                    <GitBranch className="git-branch-icon" />
                    <div className="git-branch-info">
                      <div className="git-branch-name">{branch.name}</div>
                      <div className="git-branch-meta">
                        {branch.ahead > 0 && (
                          <span className="git-branch-ahead">{branch.ahead} ahead</span>
                        )}
                        {branch.behind > 0 && (
                          <span className="git-branch-behind">{branch.behind} behind</span>
                        )}
                        <span className="git-branch-commit">Last: {branch.lastCommit}</span>
                      </div>
                    </div>
                  </div>
                  <div className="git-branch-item-right">
                    {branch.current && (
                      <span className="git-branch-current-badge">Current</span>
                    )}
                    {branch.confidence !== undefined && (
                      <ConfidenceIndicator confidence={branch.confidence} size="sm" variant="inline" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="git-tabpanel" id="git-tabpanel-history" role="tabpanel">
            <div className="git-history">
              <p className="git-history-placeholder">
                File history and diff view will be displayed here
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

