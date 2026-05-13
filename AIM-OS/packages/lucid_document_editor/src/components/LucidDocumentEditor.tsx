/**
 * LUCID Document Editor - Professional Main Component
 * 
 * Complete document editing interface with VS Code-style professional UI
 */

import React, { useState, useEffect } from 'react';
import { useDocumentStore } from '../store';
import { MonacoSectionEditor } from '../monaco-editor';
import { RichTextEditor } from '../rich-text-editor';
import { AIPanel } from '../ai-intelligence/AIPanel';
import { renderContentWithMath } from '../math-renderer';
import { DocumentPersistence } from '../persistence';
import './LucidDocumentEditor.css';
import { 
  FileText, Plus, Trash2, Edit2, Lock, Unlock, 
  Eye, EyeOff, Code, Type, ChevronRight, ChevronDown,
  Search, Tag, MoreVertical
} from 'lucide-react';
import './LucidDocumentEditor.css';

export interface LucidDocumentEditorProps {
  documentId?: string;
  initialContent?: string;
  onSave?: (document: any) => void;
  onLoad?: () => any;
  autoSave?: boolean;
  autoSaveInterval?: number;
  aiEnabled?: boolean;
  hhniEndpoint?: string;
  apiKey?: string;
}

export const LucidDocumentEditor: React.FC<LucidDocumentEditorProps> = ({
  documentId,
  initialContent,
  onSave,
  onLoad,
  autoSave = false,
  autoSaveInterval = 30000,
  aiEnabled = false,
  hhniEndpoint,
  apiKey,
}) => {
  const {
    document,
    activeSectionId,
    setDocument,
    setActiveSection,
    updateSection,
    addSection,
    deleteSection,
    getActiveSection,
    unsavedChanges,
    setUnsavedChanges,
  } = useDocumentStore();

  const [previewMode, setPreviewMode] = useState(false);
  const [editorMode, setEditorMode] = useState<'monaco' | 'rich-text'>('rich-text');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Load document on mount or when documentId changes
  useEffect(() => {
    if (onLoad) {
      const loadedDoc = onLoad();
      if (loadedDoc) {
        setDocument(loadedDoc);
        // Set first section as active if none selected
        if (loadedDoc.sections.length > 0 && !activeSectionId) {
          setActiveSection(loadedDoc.sections[0].id);
        }
      }
    } else if (initialContent) {
      const loadedDoc = DocumentPersistence.importFromMarkdown(initialContent);
      setDocument(loadedDoc);
      if (loadedDoc.sections.length > 0) {
        setActiveSection(loadedDoc.sections[0].id);
      }
    } else if (documentId) {
      const loadedDoc = DocumentPersistence.loadFromLocalStorage(documentId);
      if (loadedDoc) {
        setDocument(loadedDoc);
        if (loadedDoc.sections.length > 0 && !activeSectionId) {
          setActiveSection(loadedDoc.sections[0].id);
        }
      } else {
        // Create default document if none exists
        const defaultDoc = {
          id: documentId,
          title: 'Untitled Document',
          sections: [{
            id: `section-${Date.now()}`,
            title: 'Introduction',
            content: '',
            type: 'text' as const,
            tags: [],
            metadata: {},
            version: 1,
            locked: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }],
          tags: [],
          metadata: {
            totalWords: 0,
            totalSections: 1,
            totalMathBlocks: 0,
            totalCodeBlocks: 0,
            estimatedReadingTime: 0,
            language: 'en',
            aiManaged: false,
          },
          version: 1,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          createdBy: 'user',
        };
        setDocument(defaultDoc);
        setActiveSection(defaultDoc.sections[0].id);
      }
    }
  }, [documentId, initialContent, onLoad, setDocument, setActiveSection, activeSectionId]);

  // Auto-save
  useEffect(() => {
    if (!autoSave || !unsavedChanges) return;

    const interval = setInterval(() => {
      if (onSave) {
        onSave(document);
      } else if (documentId) {
        DocumentPersistence.saveToLocalStorage(document, documentId);
      }
      setUnsavedChanges(false);
    }, autoSaveInterval);

    return () => clearInterval(interval);
  }, [autoSave, autoSaveInterval, unsavedChanges, document, documentId, onSave, setUnsavedChanges]);

  const handleSave = () => {
    if (onSave) {
      onSave(document);
    } else if (documentId) {
      DocumentPersistence.saveToLocalStorage(document, documentId);
    }
    setUnsavedChanges(false);
  };

  const handleSectionChange = (sectionId: string, content: string) => {
    updateSection(sectionId, { content });
  };

  const handleAddSection = () => {
    const newSection: DocumentSection = {
      id: `section-${Date.now()}`,
      title: 'New Section',
      content: '',
      type: 'text',
      tags: [],
      metadata: {},
      version: 1,
      locked: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    addSection(newSection);
    setActiveSection(newSection.id);
  };

  const handleDeleteSection = (sectionId: string) => {
    if (document.sections.length <= 1) {
      alert('Cannot delete the last section.');
      return;
    }
    if (confirm('Are you sure you want to delete this section?')) {
      deleteSection(sectionId);
      // Set first remaining section as active
      const remaining = document.sections.filter(s => s.id !== sectionId);
      if (remaining.length > 0) {
        setActiveSection(remaining[0].id);
      }
    }
  };

  const handleRenameSection = (sectionId: string, newTitle: string) => {
    updateSection(sectionId, { title: newTitle });
  };

  const activeSection = getActiveSection();
  const filteredSections = searchQuery
    ? document.sections.filter(s => 
        s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : document.sections;

  return (
    <div className="lucid-editor-container">
      {/* Sidebar - Document Structure */}
      {!sidebarCollapsed && (
        <div className="editor-sidebar">
          <div className="sidebar-header">
            <div className="sidebar-title">
              <FileText size={14} />
              <span>Document Structure</span>
            </div>
            <button 
              className="sidebar-toggle-btn"
              onClick={() => setSidebarCollapsed(true)}
              title="Collapse Sidebar"
            >
              <ChevronRight size={14} />
            </button>
          </div>

          {/* Search */}
          <div className="sidebar-search">
            <Search size={14} />
            <input
              type="text"
              placeholder="Search sections..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="sidebar-search-input"
            />
          </div>

          {/* Sections List */}
          <div className="sections-list">
            {filteredSections.length === 0 ? (
              <div className="sections-empty">
                {searchQuery ? 'No sections found' : 'No sections'}
              </div>
            ) : (
              filteredSections.map((section) => (
                <div
                  key={section.id}
                  className={`section-item ${activeSectionId === section.id ? 'active' : ''}`}
                  onClick={() => setActiveSection(section.id)}
                >
                  <div className="section-item-content">
                    <FileText size={12} className="section-icon" />
                    <div className="section-item-info">
                      <div className="section-item-title">{section.title}</div>
                      <div className="section-item-preview">
                        {section.content.substring(0, 40) || 'Empty section'}...
                      </div>
                    </div>
                  </div>
                  <div className="section-item-actions">
                    {section.locked && <Lock size={12} className="section-locked" />}
                    <button
                      className="section-action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        const newTitle = prompt('Rename section:', section.title);
                        if (newTitle) handleRenameSection(section.id, newTitle);
                      }}
                      title="Rename"
                    >
                      <Edit2 size={12} />
                    </button>
                    <button
                      className="section-action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteSection(section.id);
                      }}
                      title="Delete"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Add Section Button */}
          <button className="add-section-btn" onClick={handleAddSection}>
            <Plus size={14} />
            <span>Add Section</span>
          </button>
        </div>
      )}

      {/* Collapsed Sidebar Toggle */}
      {sidebarCollapsed && (
        <button 
          className="sidebar-collapsed-toggle"
          onClick={() => setSidebarCollapsed(false)}
          title="Expand Sidebar"
        >
          <ChevronRight size={16} />
        </button>
      )}

      {/* Main Editor Area */}
      <div className="editor-main">
        {/* Editor Toolbar */}
        <div className="editor-toolbar">
          <div className="toolbar-left">
            {unsavedChanges && (
              <span className="unsaved-indicator" title="Unsaved changes">
                ●
              </span>
            )}
            <span className="document-title">{document.title}</span>
          </div>
          <div className="toolbar-right">
            <button
              className={`toolbar-btn ${previewMode ? 'active' : ''}`}
              onClick={() => setPreviewMode(!previewMode)}
              title={previewMode ? 'Exit Preview' : 'Preview'}
            >
              {previewMode ? <EyeOff size={14} /> : <Eye size={14} />}
              <span>{previewMode ? 'Edit' : 'Preview'}</span>
            </button>
            <button
              className={`toolbar-btn ${editorMode === 'monaco' ? 'active' : ''}`}
              onClick={() => setEditorMode(editorMode === 'monaco' ? 'rich-text' : 'monaco')}
              title={`Switch to ${editorMode === 'monaco' ? 'Rich Text' : 'Code'} Editor`}
            >
              {editorMode === 'monaco' ? <Type size={14} /> : <Code size={14} />}
              <span>{editorMode === 'monaco' ? 'Rich' : 'Code'}</span>
            </button>
            <button
              className="toolbar-btn"
              onClick={handleSave}
              disabled={!unsavedChanges}
              title="Save Document"
            >
              <FileText size={14} />
              <span>Save</span>
            </button>
          </div>
        </div>

        {/* Editor Content */}
        <div className="editor-content">
          {activeSection ? (
            previewMode ? (
              <div className="preview-container">
                <div className="preview-header">
                  <h2 className="preview-title">{activeSection.title}</h2>
                </div>
                <div className="preview-body">
                  {renderContentWithMath(activeSection.content)}
                </div>
              </div>
            ) : editorMode === 'rich-text' ? (
              <div className="rich-text-container">
                <RichTextEditor
                  content={activeSection.content}
                  onChange={(value) => handleSectionChange(activeSection.id, value)}
                  placeholder={`Edit ${activeSection.title}...`}
                />
              </div>
            ) : (
              <div className="monaco-container">
                <MonacoSectionEditor
                  content={activeSection.content}
                  onChange={(value) => handleSectionChange(activeSection.id, value)}
                  language="markdown"
                  theme="vs-dark"
                />
              </div>
            )
          ) : (
            <div className="editor-empty">
              <FileText size={48} className="empty-icon" />
              <h3>No Section Selected</h3>
              <p>Select a section from the sidebar to start editing, or create a new section.</p>
              <button className="empty-action-btn" onClick={handleAddSection}>
                <Plus size={16} />
                <span>Create First Section</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* AI Panel */}
      {aiEnabled && documentId && (
        <div className="ai-panel-container">
          <AIPanel documentId={documentId} hhniEndpoint={hhniEndpoint} apiKey={apiKey} />
        </div>
      )}
    </div>
  );
};
