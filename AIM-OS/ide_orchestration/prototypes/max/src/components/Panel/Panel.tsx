import React, { useEffect, useRef } from 'react';
import { X, GripVertical } from 'lucide-react';
import { usePanelStore } from '../../store/panelStore';
import { usePanel } from '../../hooks/usePanel';
import { useAccessibility } from '../../hooks/useAccessibility';
import type { Panel } from '../../types/Panel.types';
import { FileExplorerPanel } from '../panels/FileExplorerPanel';
import { OutlinePanel } from '../panels/OutlinePanel';
import { TerminalPanel } from '../panels/TerminalPanel';
import { GitPanel } from '../panels/GitPanel';
import { ComponentLibraryPanel } from '../panels/ComponentLibraryPanel';
import { AIMemoryPanel } from '../panels/AIMemoryPanel';
import { TemplatesPanel } from '../panels/TemplatesPanel';
import { OutputPanel } from '../panels/OutputPanel';
import { PropertiesPanel } from '../panels/PropertiesPanel';
import { SettingsPanel } from '../panels/SettingsPanel';
import { FileChangesViewerPanel } from '../panels/FileChangesViewerPanel';
import { ProblemsPanel } from '../panels/ProblemsPanel';
import { MainChatPanel } from '../panels/MainChatPanel';
import { DebugConsolePanel } from '../panels/DebugConsolePanel';
import {
  SuperIndexPanel,
  MasterIndexPanel,
  SystemMapPanel,
  NLTagsExplorerPanel,
  DocumentationExplorerPanel,
} from '../panels/AIMOSStructurePanels';
import { ContextWebPanel } from '../panels/ContextWebPanel';
import { EvolutionExplorerPanel } from '../panels/EvolutionExplorerPanel';
import { HierarchicalCodeExplorerPanel } from '../panels/HierarchicalCodeExplorerPanel';
import { FileVersionHistoryPanel } from '../panels/FileVersionHistoryPanel';
import './Panel.css';

interface PanelProps {
  panel: Panel;
}

const panelTitles: Record<string, string> = {
  'file-explorer': 'File Explorer',
  'component-library': 'Component Library',
  'ai-memory': 'AI Memory',
  'git': 'Git',
  'templates': 'Templates',
  'outline': 'Outline',
  'properties': 'Properties',
  'layers': 'Layers',
  'assets': 'Assets',
  'settings': 'Settings',
  'terminal': 'Terminal',
  'problems': 'Problems',
  'output': 'Output',
  'debug-console': 'Debug Console',
  'timeline': 'Timeline',
  'main-chat': 'Main Chat',
  'coding-agent': 'Coding Agent',
  'planning-agent': 'Planning Agent',
  'context-chat': 'Context Chat',
  'super-index': 'Super Index',
  'master-index': 'Master Index',
  'system-map': 'System Map',
  'nl-tags': 'NL Tags Explorer',
  'documentation': 'Documentation Explorer',
  'context-web': 'Context Web',
  'evolution-explorer': 'Evolution Explorer',
  'hierarchical-code-explorer': 'Hierarchical Code Explorer',
  'file-version-history': 'File Version History',
};

export const Panel: React.FC<PanelProps> = ({ panel }) => {
  const { updatePanel, setSelectedPanel } = usePanelStore();
  const { isSelected, toggleVisibility, select } = usePanel(panel.id);
  const { announce, getPanelAriaLabel, focusElement } = useAccessibility();
  const panelRef = useRef<HTMLDivElement>(null);

  // Focus panel when selected
  useEffect(() => {
    if (isSelected && panelRef.current) {
      focusElement(panelRef.current);
      announce(`Selected ${panelTitles[panel.type] || panel.type} panel`);
    }
  }, [isSelected, panel.type, focusElement, announce]);

  const handleClose = () => {
    updatePanel(panel.id, { visible: false });
    announce(`${panelTitles[panel.type] || panel.type} panel closed`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleClose();
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      select();
    }
  };

  const renderPanelContent = () => {
    switch (panel.type) {
      case 'file-explorer':
        return <FileExplorerPanel />;
      case 'outline':
        return <OutlinePanel />;
      case 'terminal':
        return <TerminalPanel />;
      case 'git':
        return <GitPanel />;
      case 'component-library':
        return <ComponentLibraryPanel />;
      case 'ai-memory':
        return <AIMemoryPanel />;
      case 'templates':
        return <TemplatesPanel />;
      case 'output':
        return <OutputPanel />;
      case 'properties':
        return <PropertiesPanel />;
      case 'settings':
        return <SettingsPanel />;
      case 'file-changes-viewer':
        return <FileChangesViewerPanel />;
      case 'problems':
        return <ProblemsPanel />;
      case 'main-chat':
        return <MainChatPanel />;
      case 'debug-console':
        return <DebugConsolePanel />;
      case 'super-index':
        return <SuperIndexPanel />;
      case 'master-index':
        return <MasterIndexPanel />;
      case 'system-map':
        return <SystemMapPanel />;
      case 'nl-tags':
        return <NLTagsExplorerPanel />;
      case 'documentation':
        return <DocumentationExplorerPanel />;
      case 'context-web':
        return <ContextWebPanel />;
      case 'evolution-explorer':
        return <EvolutionExplorerPanel />;
      case 'hierarchical-code-explorer':
        return <HierarchicalCodeExplorerPanel />;
      case 'file-version-history':
        return <FileVersionHistoryPanel />;
      default:
        return (
          <div className="panel-placeholder">
            <p>{panelTitles[panel.type] || panel.type} Panel</p>
            <p className="panel-placeholder-hint">Panel implementation coming soon</p>
          </div>
        );
    }
  };

  if (!panel.visible) return null;

  const panelTitle = panelTitles[panel.type] || panel.type;
  const ariaLabel = getPanelAriaLabel(panel.type, panelTitle);

  return (
    <div
      ref={panelRef}
      className={`panel ${isSelected ? 'panel-selected' : ''}`}
      data-panel-id={panel.id}
      data-panel-type={panel.type}
      role="region"
      aria-label={ariaLabel}
      aria-selected={isSelected}
      tabIndex={isSelected ? 0 : -1}
      onKeyDown={handleKeyDown}
      onClick={select}
    >
      <div className="panel-header">
        <div className="panel-header-left">
          <GripVertical
            className="panel-drag-handle"
            size={16}
            aria-label="Drag handle"
            role="button"
            tabIndex={-1}
          />
          <span className="panel-title">{panelTitle}</span>
        </div>
        <div className="panel-header-right">
          <button
            className="panel-close-button"
            onClick={handleClose}
            aria-label={`Close ${panelTitle} panel`}
            title={`Close ${panelTitle} panel (Escape)`}
          >
            <X size={14} aria-hidden="true" />
          </button>
        </div>
      </div>
      <div className="panel-content" role="region" aria-label={`${panelTitle} content`}>
        {renderPanelContent()}
      </div>
    </div>
  );
};

