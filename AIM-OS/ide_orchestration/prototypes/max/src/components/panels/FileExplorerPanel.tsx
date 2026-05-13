// Enhanced File Explorer Panel - Max V2
// CMC-backed file operations with bitemporal history and VIF confidence tracking

import React, { useState, useMemo, useEffect } from 'react';
import { Folder, File, ChevronRight, ChevronDown, History, Clock, Shield, Refresh } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import { mockFileTree } from '../../mockData/mockData';
import type { FileNode } from '../../mockData/mockData';
import './FileExplorerPanel.css';

interface FileTreeState {
  [path: string]: boolean;
}

interface FileVersion {
  id: string;
  path: string;
  timestamp: string;
  valid_from: string;
  valid_to: string | null;
  cmcAtomId: string;
  confidence: number;
  witnessId?: string;
}

export const FileExplorerPanel: React.FC = () => {
  const { cmc, vif, loading, errors } = useAIMOS();
  const [expanded, setExpanded] = useState<FileTreeState>({
    'src/': true,
    'src/components/': true,
  });
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [fileVersions, setFileVersions] = useState<FileVersion[]>([]);

  // Fetch file versions from CMC when file is selected
  useEffect(() => {
    if (selectedPath) {
      // Fetch CMC atoms for this file path
      cmc.searchAtoms(`file_path:${selectedPath}`).then((atoms) => {
        const versions: FileVersion[] = atoms
          .filter((atom) => atom.modality === 'code' && atom.metadata?.file_path === selectedPath)
          .map((atom) => ({
            id: atom.id,
            path: selectedPath,
            timestamp: atom.created_at,
            valid_from: atom.valid_from,
            valid_to: atom.valid_to,
            cmcAtomId: atom.id,
            confidence: vif.witnesses.find((w) => w.id === atom.witness.snapshot_id)?.confidence_score || 0.85,
            witnessId: atom.witness.snapshot_id,
          }))
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        setFileVersions(versions);
      });
    }
  }, [selectedPath, cmc, vif]);

  const toggleExpand = (path: string) => {
    setExpanded((prev) => ({
      ...prev,
      [path]: !prev[path],
    }));
  };

  const handleFileClick = async (path: string) => {
    setSelectedPath(path);
    setShowHistory(false);
    
    // Store file access as CMC atom (for bitemporal tracking)
    try {
      await cmc.storeAtom({
        modality: 'event',
        content: {
          inline: `File accessed: ${path}`,
          media_type: 'text/plain',
        },
        metadata: {
          file_path: path,
          event_type: 'file_access',
          agent: 'max',
        },
        tags: { file_access: 1, path: 1 },
      });
    } catch (error) {
      console.error('[MAX] Failed to store file access atom:', error);
    }
  };

  const renderFileNode = (node: FileNode, path: string, level: number = 0): React.ReactNode => {
    const isExpanded = expanded[path] || false;
    const isSelected = selectedPath === path;
    const isDirectory = node.type === 'directory';
    const hasChildren = isDirectory && node.children && Object.keys(node.children).length > 0;

    return (
      <div key={path} className="file-tree-node">
        <div
          className={`file-tree-item ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => {
            if (isDirectory) {
              toggleExpand(path);
            } else {
              handleFileClick(path);
            }
          }}
        >
          <div className="file-tree-icon">
            {isDirectory ? (
              hasChildren ? (
                isExpanded ? (
                  <ChevronDown size={14} />
                ) : (
                  <ChevronRight size={14} />
                )
              ) : (
                <Folder size={14} />
              )
            ) : (
              <File size={14} />
            )}
          </div>
          <span className="file-tree-name">{node.name}</span>
          {node.gitStatus && (
            <span className={`file-tree-git-status git-${node.gitStatus.toLowerCase()}`}>
              {node.gitStatus}
            </span>
          )}
        </div>
        {isDirectory && hasChildren && isExpanded && (
          <div className="file-tree-children">
            {Object.entries(node.children!).map(([childName, childNode]) =>
              renderFileNode(childNode, `${path}${childName}`, level + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return <PanelLoading message="Loading file tree..." />;
  }

  if (errors.length > 0) {
    return (
      <div className="file-explorer-panel error">
        <div className="error-message">
          <p>Error loading file explorer:</p>
          <ul>
            {errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="file-explorer-panel">
      <div className="file-explorer-header">
        <div className="file-explorer-toolbar">
          <input
            type="text"
            placeholder="Search files..."
            className="file-explorer-search"
          />
          {selectedPath && (
            <button
              className="file-explorer-history-btn"
              onClick={() => setShowHistory(!showHistory)}
              title="Show file history"
            >
              <History size={16} />
            </button>
          )}
        </div>
      </div>
      
      {showHistory && selectedPath && fileVersions.length > 0 && (
        <div className="file-explorer-history">
          <div className="file-explorer-history-header">
            <h4>File History: {selectedPath}</h4>
            <button onClick={() => setShowHistory(false)}>×</button>
          </div>
          <div className="file-explorer-history-list">
            {fileVersions.map((version) => (
              <div key={version.id} className="file-version-item">
                <div className="file-version-header">
                  <Clock size={14} />
                  <span className="file-version-time">
                    {new Date(version.timestamp).toLocaleString()}
                  </span>
                  <ConfidenceIndicator confidence={version.confidence} size="sm" />
                </div>
                <div className="file-version-meta">
                  <span className="file-version-valid">
                    Valid: {new Date(version.valid_from).toLocaleDateString()}
                    {version.valid_to && ` → ${new Date(version.valid_to).toLocaleDateString()}`}
                  </span>
                  {version.witnessId && (
                    <span className="file-version-witness">
                      <Shield size={12} />
                      Witness: {version.witnessId.slice(0, 8)}...
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="file-explorer-tree">
        {Object.entries(mockFileTree).map(([name, node]) =>
          renderFileNode(node, name)
        )}
      </div>
    </div>
  );
};

