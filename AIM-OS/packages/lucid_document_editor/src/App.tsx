/**
 * LUCID Document Editor - Professional Launcher App
 * 
 * VS Code-style professional interface with comprehensive document editing
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { LucidDocumentEditor } from './components/LucidDocumentEditor';
import { DocumentModel } from './models';
import { FileParser } from './file-parser';
import { DocumentPersistence } from './persistence';
import { PaginationSettingsPanel, DEFAULT_PAGINATION, PaginationSettings } from './pagination';
import { FileText, Upload, FilePlus, Save, Settings, Eye, EyeOff, Code, Type, Search, MoreVertical } from 'lucide-react';
import './App.css';

export const App: React.FC = () => {
  const [documentId, setDocumentId] = useState<string>('demo-document');
  const [currentDocument, setCurrentDocument] = useState<DocumentModel | null>(null);
  const [aiEnabled, setAiEnabled] = useState(false);
  const [collaborationEnabled, setCollaborationEnabled] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [editorMode, setEditorMode] = useState<'rich-text' | 'monaco'>('rich-text');
  const [paginationSettings, setPaginationSettings] = useState<PaginationSettings>(DEFAULT_PAGINATION);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load document on mount or when documentId changes
  useEffect(() => {
    const loaded = DocumentPersistence.loadFromLocalStorage(documentId);
    if (loaded) {
      setCurrentDocument(loaded);
    } else {
      // Create default empty document
      const defaultDoc: DocumentModel = {
        id: documentId,
        title: 'Untitled Document',
        sections: [{
          id: `section-${Date.now()}`,
          title: 'Introduction',
          content: '',
          type: 'text',
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
      setCurrentDocument(defaultDoc);
      DocumentPersistence.saveToLocalStorage(defaultDoc, documentId);
    }
  }, [documentId]);

  const handleSave = (document: DocumentModel) => {
    DocumentPersistence.saveToLocalStorage(document, documentId);
    setCurrentDocument(document);
  };

  const handleLoad = (): DocumentModel | null => {
    return DocumentPersistence.loadFromLocalStorage(documentId);
  };

  const handleNewDocument = () => {
    const newId = `doc-${Date.now()}`;
    setDocumentId(newId);
    setCurrentDocument(null); // Will trigger useEffect to create new doc
  };

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const result = await FileParser.parseFile(file);
      const document = result.document;
      
      const newId = document.id;
      setDocumentId(newId);
      setCurrentDocument(document);
      DocumentPersistence.saveToLocalStorage(document, newId);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert(`Failed to upload file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, []);

  const handlePaste = useCallback(async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (!text.trim()) {
        alert('Clipboard is empty.');
        return;
      }

      const document = DocumentPersistence.importFromMarkdown(text);
      document.id = `doc-${Date.now()}`;
      document.title = 'Pasted Document';
      
      // If no sections, create one with the content
      if (document.sections.length === 0) {
        document.sections = [{
          id: `section-${Date.now()}`,
          title: 'Content',
          content: text,
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }];
      }
      
      const newId = document.id;
      setDocumentId(newId);
      setCurrentDocument(document);
      DocumentPersistence.saveToLocalStorage(document, newId);
    } catch (error) {
      console.error('Error pasting:', error);
      alert('Failed to paste from clipboard. Please ensure clipboard access is granted.');
    }
  }, []);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleExport = useCallback(() => {
    if (!currentDocument) return;
    
    const markdown = DocumentPersistence.exportToMarkdown(currentDocument);
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentDocument.title || 'document'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [currentDocument]);

  if (!currentDocument) {
    return (
      <div className="app-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading document...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Professional VS Code-style Title Bar */}
      <div className="title-bar">
        <div className="title-bar-content">
          <div className="title-bar-title">
            <FileText className="title-icon" size={16} />
            <span>LUCID Document Editor</span>
          </div>
          <div className="title-bar-controls">
            <span className="document-id">{currentDocument.title}</span>
          </div>
        </div>
      </div>

      {/* Professional Menu Bar */}
      <div className="menu-bar">
        <div className="menu-group">
          <button className="menu-button" onClick={handleNewDocument} title="New Document">
            <FilePlus size={14} />
            <span>New</span>
          </button>
          <button className="menu-button" onClick={handleUploadClick} title="Upload Document">
            <Upload size={14} />
            <span>Upload</span>
          </button>
          <button className="menu-button" onClick={handlePaste} title="Paste from Clipboard">
            <FileText size={14} />
            <span>Paste</span>
          </button>
          <button className="menu-button" onClick={handleExport} title="Export Document">
            <Save size={14} />
            <span>Export</span>
          </button>
        </div>
        <div className="menu-group">
          <button 
            className={`menu-button ${previewMode ? 'active' : ''}`}
            onClick={() => setPreviewMode(!previewMode)} 
            title="Toggle Preview Mode"
          >
            {previewMode ? <EyeOff size={14} /> : <Eye size={14} />}
            <span>Preview</span>
          </button>
          <button 
            className={`menu-button ${editorMode === 'monaco' ? 'active' : ''}`}
            onClick={() => setEditorMode(editorMode === 'monaco' ? 'rich-text' : 'monaco')} 
            title="Toggle Editor Mode"
          >
            {editorMode === 'monaco' ? <Type size={14} /> : <Code size={14} />}
            <span>{editorMode === 'monaco' ? 'Rich Text' : 'Code'}</span>
          </button>
          <label className="menu-toggle">
            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={(e) => setAiEnabled(e.target.checked)}
            />
            <span>AI</span>
          </label>
          <label className="menu-toggle">
            <input
              type="checkbox"
              checked={collaborationEnabled}
              onChange={(e) => setCollaborationEnabled(e.target.checked)}
            />
            <span>Collaborate</span>
          </label>
          <button className="menu-button" title="More Options">
            <MoreVertical size={14} />
          </button>
          <PaginationSettingsPanel
            settings={paginationSettings}
            onSettingsChange={setPaginationSettings}
          />
        </div>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".md,.txt,.markdown,.json,.pdf,.docx,.doc,.rtf,.html,.htm,.tex,.latex"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
      />

      {/* Editor Area */}
      <div className="editor-area">
        <LucidDocumentEditor
          key={documentId} // Force re-render when document changes
          documentId={documentId}
          onSave={handleSave}
          onLoad={handleLoad}
          autoSave={true}
          autoSaveInterval={30000}
          aiEnabled={aiEnabled}
          hhniEndpoint={aiEnabled ? 'http://localhost:8000' : undefined}
        />
      </div>

      {/* Professional Status Bar */}
      <div className="status-bar">
        <div className="status-left">
          <span className="status-item">Ready</span>
          <span className="status-divider">|</span>
          <span className="status-item">{currentDocument.sections.length} sections</span>
          <span className="status-divider">|</span>
          <span className="status-item">{currentDocument.metadata.totalWords} words</span>
          <span className="status-divider">|</span>
          <span className="status-item">Auto-save: ON</span>
        </div>
        <div className="status-right">
          <span className="status-item">v1.0.0</span>
        </div>
      </div>
    </div>
  );
};
