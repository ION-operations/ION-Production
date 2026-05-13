/**
 * LUCID Document Editor - Version History Panel
 * 
 * UI component for viewing section version history
 */

import React, { useState } from 'react';
import { SectionVersionManager, SectionVersion } from '../versioning/section-versioning';
import { MonacoDiffViewer } from '../diff-viewer/MonacoDiffViewer';
import { Clock, RotateCcw, Eye } from 'lucide-react';

export interface VersionHistoryPanelProps {
  sectionId: string;
  versionManager: SectionVersionManager;
  currentContent: string;
  onRollback?: (version: SectionVersion) => void;
}

export const VersionHistoryPanel: React.FC<VersionHistoryPanelProps> = ({
  sectionId,
  versionManager,
  currentContent,
  onRollback,
}) => {
  const [selectedVersion, setSelectedVersion] = useState<SectionVersion | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'diff'>('list');
  const versions = versionManager.getVersions(sectionId);

  const handleViewDiff = (version: SectionVersion) => {
    setSelectedVersion(version);
    setViewMode('diff');
  };

  const handleRollback = (version: SectionVersion) => {
    if (onRollback) {
      onRollback(version);
    }
  };

  if (viewMode === 'diff' && selectedVersion) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ padding: '8px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 'bold' }}>Version {selectedVersion.version}</span>
          <button onClick={() => setViewMode('list')}>Back to List</button>
        </div>
        <MonacoDiffViewer
          original={selectedVersion.content}
          modified={currentContent}
          language="markdown"
        />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '8px', borderBottom: '1px solid #ccc' }}>
        <h3>Version History</h3>
        <div style={{ fontSize: '12px', color: '#666' }}>
          {versions.length} version{versions.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {versions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '16px', color: '#666' }}>
            No version history
          </div>
        ) : (
          versions
            .slice()
            .reverse()
            .map((version) => (
              <div
                key={version.id}
                style={{
                  padding: '8px',
                  marginBottom: '8px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '4px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>Version {version.version}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {new Date(version.timestamp).toLocaleString()}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      by {version.author}
                    </div>
                    {version.reason && (
                      <div style={{ fontSize: '11px', color: '#999', marginTop: '4px' }}>
                        {version.reason}
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      onClick={() => handleViewDiff(version)}
                      style={{
                        padding: '4px 8px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                      title="View Diff"
                    >
                      <Eye size={12} />
                    </button>
                    <button
                      onClick={() => handleRollback(version)}
                      style={{
                        padding: '4px 8px',
                        backgroundColor: '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                      title="Rollback"
                    >
                      <RotateCcw size={12} />
                    </button>
                  </div>
                </div>
                <div style={{ fontSize: '11px', color: '#999', marginTop: '4px' }}>
                  {version.content.substring(0, 100)}...
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
};

