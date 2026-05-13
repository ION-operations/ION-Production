/**
 * LUCID Document Editor - Monaco Diff Viewer
 * 
 * Visual diff viewer using Monaco Editor
 */

import React, { useMemo } from 'react';
import { DiffEditor } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

export interface MonacoDiffViewerProps {
  original: string;
  modified: string;
  language?: string;
  theme?: string;
  readOnly?: boolean;
  renderSideBySide?: boolean;
  onDiffCalculated?: (diff: { added: number; removed: number; changed: boolean }) => void;
}

export const MonacoDiffViewer: React.FC<MonacoDiffViewerProps> = ({
  original,
  modified,
  language = 'markdown',
  theme = 'vs-dark',
  readOnly = true,
  renderSideBySide = true,
  onDiffCalculated,
}) => {
  const diffStats = useMemo(() => {
    const originalLines = original.split('\n');
    const modifiedLines = modified.split('\n');
    
    let added = 0;
    let removed = 0;
    let changed = false;

    const maxLen = Math.max(originalLines.length, modifiedLines.length);
    for (let i = 0; i < maxLen; i++) {
      if (i >= originalLines.length) {
        added++;
        changed = true;
      } else if (i >= modifiedLines.length) {
        removed++;
        changed = true;
      } else if (originalLines[i] !== modifiedLines[i]) {
        added++;
        removed++;
        changed = true;
      }
    }

    const stats = { added, removed, changed };
    if (onDiffCalculated) {
      onDiffCalculated(stats);
    }
    return stats;
  }, [original, modified, onDiffCalculated]);

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Diff Stats */}
      <div style={{ padding: '8px', borderBottom: '1px solid #ccc', fontSize: '12px', display: 'flex', gap: '16px' }}>
        <span style={{ color: '#4caf50' }}>+{diffStats.added} added</span>
        <span style={{ color: '#f44336' }}>-{diffStats.removed} removed</span>
        {diffStats.changed && <span style={{ color: '#ff9800' }}>Modified</span>}
      </div>

      {/* Diff Editor */}
      <div style={{ flex: 1 }}>
        <DiffEditor
          height="100%"
          language={language}
          theme={theme}
          original={original}
          modified={modified}
          options={{
            readOnly,
            renderSideBySide,
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            automaticLayout: true,
            diffWordWrap: 'on',
            enableSplitViewResizing: true,
            renderOverviewRuler: true,
            ignoreTrimWhitespace: false,
            renderIndicators: true,
            originalEditable: false,
            modifiedEditable: !readOnly,
          }}
        />
      </div>
    </div>
  );
};

