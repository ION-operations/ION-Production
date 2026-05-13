/**
 * LUCID Document Editor - E2E Tests
 * 
 * End-to-end tests for complete workflows, collaboration, and export/import
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { DocumentModel } from '../models';
import { useDocumentStore } from '../store';
import { AIMOSIntegrationManager } from '../aimos-integration/aimos-manager';
import { CollaborationEngine } from '../collaboration/collaboration-engine';
import { DocumentExporter } from '../aimos-integration/export-import';
import { DocumentPersistence } from '../persistence';

// Mock fetch for API calls
global.fetch = vi.fn();

describe('Complete Document Workflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should create, edit, and save a document', async () => {
    // Create new document
    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
      sections: [
        {
          id: 'section-001',
          title: 'Introduction',
          content: 'Initial content',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
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

    // Save to localStorage
    DocumentPersistence.saveToLocalStorage(document);
    
    // Load from localStorage
    const loaded = DocumentPersistence.loadFromLocalStorage('doc-001');
    expect(loaded).toBeDefined();
    expect(loaded?.id).toBe('doc-001');
    expect(loaded?.sections).toHaveLength(1);

    // Update section
    if (loaded) {
      loaded.sections[0].content = 'Updated content';
      loaded.sections[0].version = 2;
      DocumentPersistence.saveToLocalStorage(loaded);
      
      const updated = DocumentPersistence.loadFromLocalStorage('doc-001');
      expect(updated?.sections[0].content).toBe('Updated content');
      expect(updated?.sections[0].version).toBe(2);
    }
  });

  it('should handle document with math equations', async () => {
    const document: DocumentModel = {
      id: 'doc-math',
      title: 'Math Document',
      sections: [
        {
          id: 'section-math',
          title: 'Equations',
          content: 'The formula $E = mc^2$ is famous. Also: $$\\int_0^1 x dx = \\frac{1}{2}$$',
          type: 'math',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
      tags: [],
      metadata: {
        totalWords: 0,
        totalSections: 1,
        totalMathBlocks: 2,
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

    // Save and load
    DocumentPersistence.saveToLocalStorage(document);
    const loaded = DocumentPersistence.loadFromLocalStorage('doc-math');
    
    expect(loaded?.sections[0].type).toBe('math');
    expect(loaded?.sections[0].content).toContain('$E = mc^2$');
    expect(loaded?.sections[0].content).toContain('$$\\int_0^1 x dx = \\frac{1}{2}$$');
  });

  it('should handle multiple sections with different types', async () => {
    const document: DocumentModel = {
      id: 'doc-mixed',
      title: 'Mixed Document',
      sections: [
        {
          id: 'section-text',
          title: 'Text Section',
          content: 'Plain text content',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: 'section-code',
          title: 'Code Section',
          content: '```python\ndef hello():\n    print("Hello")\n```',
          type: 'code',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: 'section-math',
          title: 'Math Section',
          content: 'Formula: $x^2 + y^2 = r^2$',
          type: 'math',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
      tags: [],
      metadata: {
        totalWords: 0,
        totalSections: 3,
        totalMathBlocks: 1,
        totalCodeBlocks: 1,
        estimatedReadingTime: 0,
        language: 'en',
        aiManaged: false,
      },
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy: 'user',
    };

    DocumentPersistence.saveToLocalStorage(document);
    const loaded = DocumentPersistence.loadFromLocalStorage('doc-mixed');
    
    expect(loaded?.sections).toHaveLength(3);
    expect(loaded?.sections.find(s => s.type === 'text')).toBeDefined();
    expect(loaded?.sections.find(s => s.type === 'code')).toBeDefined();
    expect(loaded?.sections.find(s => s.type === 'math')).toBeDefined();
  });
});

describe('Collaboration Workflow', () => {
  it('should handle multi-user collaboration', async () => {
    // User 1 creates document
    const engine1 = new CollaborationEngine({
      documentId: 'doc-collab',
      userId: 'user-001',
      userName: 'Alice',
      websocketUrl: 'ws://localhost:5001',
    });

    const document: DocumentModel = {
      id: 'doc-collab',
      title: 'Collaborative Document',
      sections: [
        {
          id: 'section-001',
          title: 'Section 1',
          content: 'Initial content',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
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
      createdBy: 'user-001',
    };

    engine1.syncDocument(document);

    // User 2 joins
    const engine2 = new CollaborationEngine({
      documentId: 'doc-collab',
      userId: 'user-002',
      userName: 'Bob',
      websocketUrl: 'ws://localhost:5001',
    });

    // User 1 updates section
    engine1.updateSection('section-001', 'Updated by Alice');

    // User 2 updates section (simulating concurrent edit)
    engine2.updateSection('section-001', 'Updated by Bob');

    // Both should see changes (CRDT handles merging)
    const doc1 = engine1.getDocument();
    const doc2 = engine2.getDocument();
    
    expect(doc1.sections.length).toBeGreaterThan(0);
    expect(doc2.sections.length).toBeGreaterThan(0);
  });

  it('should handle comments workflow', async () => {
    const engine = new CollaborationEngine({
      documentId: 'doc-comments',
      userId: 'user-001',
      userName: 'Alice',
      websocketUrl: 'ws://localhost:5001',
    });

    // Add comment
    const comment = engine.addComment({
      sectionId: 'section-001',
      position: { offset: 10 },
      content: 'This needs clarification',
      author: 'user-001',
      authorName: 'Alice',
    });

    expect(comment.id).toBeDefined();
    expect(comment.content).toBe('This needs clarification');

    // Get comments
    const comments = engine.getComments('section-001');
    expect(comments).toHaveLength(1);

    // Resolve comment
    engine.resolveComment(comment.id, 'user-001');
    const resolvedComments = engine.getComments('section-001');
    const resolved = resolvedComments.find(c => c.id === comment.id);
    expect(resolved?.resolved).toBe(true);
  });

  it('should track user presence', async () => {
    const engine1 = new CollaborationEngine({
      documentId: 'doc-presence',
      userId: 'user-001',
      userName: 'Alice',
      websocketUrl: 'ws://localhost:5001',
    });

    const engine2 = new CollaborationEngine({
      documentId: 'doc-presence',
      userId: 'user-002',
      userName: 'Bob',
      websocketUrl: 'ws://localhost:5001',
    });

    // Update cursors
    engine1.updateCursor('section-001', 10);
    engine2.updateCursor('section-001', 20);

    // Update selections
    engine1.updateSelection('section-001', 5, 15);
    engine2.updateSelection('section-001', 18, 25);

    // Get active users (would be populated after connection)
    const users1 = engine1.getActiveUsers();
    const users2 = engine2.getActiveUsers();
    
    expect(Array.isArray(users1)).toBe(true);
    expect(Array.isArray(users2)).toBe(true);
  });
});

describe('AIM-OS Integration Workflow', () => {
  let manager: AIMOSIntegrationManager;

  beforeEach(() => {
    manager = new AIMOSIntegrationManager({
      cmc: { endpoint: 'http://localhost:8000' },
      vif: { endpoint: 'http://localhost:8000' },
      seg: { endpoint: 'http://localhost:8000' },
      hhni: { endpoint: 'http://localhost:8000' },
      apoe: { endpoint: 'http://localhost:8000' },
    });
    vi.clearAllMocks();
  });

  it('should complete full save workflow with AIM-OS', async () => {
    const document: DocumentModel = {
      id: 'doc-aimos',
      title: 'AIM-OS Document',
      sections: [
        {
          id: 'section-001',
          title: 'Section 1',
          content: 'Content',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
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

    // Mock all API calls
    (global.fetch as any)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ atom_id: 'atom-123' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'vif-123' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ entity_id: 'entity-123' }) })
      .mockResolvedValueOnce({ ok: true });

    const result = await manager.saveDocument(document);

    expect(result.atomId).toBe('atom-123');
    expect(result.witnessId).toBe('vif-123');
    expect(result.entityId).toBe('entity-123');
    expect(global.fetch).toHaveBeenCalledTimes(4);
  });

  it('should load document from AIM-OS', async () => {
    const document: DocumentModel = {
      id: 'doc-loaded',
      title: 'Loaded Document',
      sections: [],
      tags: [],
      metadata: {
        totalWords: 0,
        totalSections: 0,
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

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        atom: {
          content: {
            inline: JSON.stringify(document),
          },
        },
      }),
    });

    const loaded = await manager.loadDocument('atom-123');
    expect(loaded).toBeDefined();
    expect(loaded?.id).toBe('doc-loaded');
  });

  it('should perform semantic search', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        results: [
          {
            node_id: 'node-001',
            score: 0.95,
            confidence: 0.9,
            content: 'Mathematical proof',
            level: 1,
          },
          {
            node_id: 'node-002',
            score: 0.85,
            confidence: 0.8,
            content: 'Algebraic equation',
            level: 1,
          },
        ],
      }),
    });

    const results = await manager.semanticSearch('mathematical proof', 10);
    expect(results).toHaveLength(2);
    expect(results[0].node_id).toBe('node-001');
  });

  it('should find related documents', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        relations: [
          {
            id: 'rel-001',
            source_id: 'doc-001',
            target_id: 'doc-002',
            relation_type: 'references',
            confidence: 0.9,
          },
          {
            id: 'rel-002',
            source_id: 'doc-003',
            target_id: 'doc-001',
            relation_type: 'references',
            confidence: 0.8,
          },
        ],
      }),
    });

    const related = await manager.getRelatedDocuments('doc-001');
    expect(related).toContain('doc-002');
    expect(related).toContain('doc-003');
  });
});

describe('Export/Import Workflow', () => {
  const createTestDocument = (): DocumentModel => ({
    id: 'doc-export',
    title: 'Export Test Document',
    description: 'A test document for export',
    sections: [
      {
        id: 'section-001',
        title: 'Introduction',
        content: 'This is the introduction section.',
        type: 'text',
        tags: [],
        metadata: {},
        version: 1,
        locked: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'section-002',
        title: 'Math Section',
        content: 'The formula $E = mc^2$ is famous.',
        type: 'math',
        tags: [],
        metadata: {},
        version: 1,
        locked: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ],
    tags: [
      {
        id: 'tag-001',
        name: 'mathematics',
        category: 'topic',
        color: '#FF6B6B',
        aiGenerated: false,
      },
    ],
    metadata: {
      totalWords: 10,
      totalSections: 2,
      totalMathBlocks: 1,
      totalCodeBlocks: 0,
      estimatedReadingTime: 1,
      language: 'en',
      aiManaged: false,
    },
    version: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'user',
  });

  it('should export to JSON and import back', async () => {
    const document = createTestDocument();
    
    const json = await DocumentExporter.exportDocument(document, {
      format: 'json',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof json).toBe('string');
    const parsed = JSON.parse(json as string);
    expect(parsed.id).toBe('doc-export');
    expect(parsed.sections).toHaveLength(2);

    // Import back
    const imported = await DocumentExporter.importDocument(json as string, {
      format: 'json',
      merge: false,
      preserveHistory: false,
    });

    expect(imported.id).toBe('doc-export');
    expect(imported.sections).toHaveLength(2);
  });

  it('should export to Markdown', async () => {
    const document = createTestDocument();
    
    const markdown = await DocumentExporter.exportDocument(document, {
      format: 'markdown',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof markdown).toBe('string');
    expect(markdown).toContain('Export Test Document');
    expect(markdown).toContain('Introduction');
    expect(markdown).toContain('Math Section');
  });

  it('should export to LaTeX', async () => {
    const document = createTestDocument();
    
    const latex = await DocumentExporter.exportDocument(document, {
      format: 'latex',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof latex).toBe('string');
    expect(latex).toContain('\\documentclass');
    expect(latex).toContain('Export Test Document');
    expect(latex).toContain('\\section{Introduction}');
    expect(latex).toContain('\\section{Math Section}');
  });

  it('should export to HTML', async () => {
    const document = createTestDocument();
    
    const html = await DocumentExporter.exportDocument(document, {
      format: 'html',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof html).toBe('string');
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('Export Test Document');
    expect(html).toContain('<h1>');
    expect(html).toContain('katex');
  });

  it('should import from LaTeX', async () => {
    const latex = `\\documentclass{article}
\\usepackage{amsmath}
\\title{Imported Document}
\\author{Test User}
\\begin{document}
\\maketitle
\\begin{abstract}
This is the abstract.
\\end{abstract}
\\section{Introduction}
This is the introduction.
\\section{Conclusion}
This is the conclusion.
\\end{document}`;

    const document = await DocumentExporter.importDocument(latex, {
      format: 'latex',
      merge: false,
      preserveHistory: false,
    });

    expect(document.title).toBe('Imported Document');
    expect(document.sections.length).toBeGreaterThanOrEqual(2);
    expect(document.sections.find(s => s.title === 'Introduction')).toBeDefined();
    expect(document.sections.find(s => s.title === 'Conclusion')).toBeDefined();
  });

  it('should import from Markdown', async () => {
    const markdown = `# Imported Document

This is the description.

## Section 1

Content of section 1.

## Section 2

Content of section 2 with math: $x^2 + y^2 = r^2$
`;

    const document = await DocumentExporter.importDocument(markdown, {
      format: 'markdown',
      merge: false,
      preserveHistory: false,
    });

    expect(document.title).toBe('Imported Document');
    expect(document.sections.length).toBeGreaterThanOrEqual(2);
  });
});

describe('Version Control Workflow', () => {
  it('should track document versions', async () => {
    const document: DocumentModel = {
      id: 'doc-versions',
      title: 'Versioned Document',
      sections: [
        {
          id: 'section-001',
          title: 'Section 1',
          content: 'Version 1',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
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

    // Save initial version
    DocumentPersistence.saveToLocalStorage(document);

    // Update to version 2
    document.sections[0].content = 'Version 2';
    document.sections[0].version = 2;
    document.version = 2;
    DocumentPersistence.saveToLocalStorage(document);

    const loaded = DocumentPersistence.loadFromLocalStorage('doc-versions');
    expect(loaded?.version).toBe(2);
    expect(loaded?.sections[0].version).toBe(2);
    expect(loaded?.sections[0].content).toBe('Version 2');
  });
});

describe('Section Locking Workflow', () => {
  it('should lock and unlock sections', async () => {
    const document: DocumentModel = {
      id: 'doc-locking',
      title: 'Locked Document',
      sections: [
        {
          id: 'section-001',
          title: 'Section 1',
          content: 'Content',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
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

    // Lock section
    document.sections[0].locked = true;
    document.sections[0].lockedBy = 'user-001';
    DocumentPersistence.saveToLocalStorage(document);

    const loaded = DocumentPersistence.loadFromLocalStorage('doc-locking');
    expect(loaded?.sections[0].locked).toBe(true);
    expect(loaded?.sections[0].lockedBy).toBe('user-001');

    // Unlock section
    loaded!.sections[0].locked = false;
    loaded!.sections[0].lockedBy = undefined;
    DocumentPersistence.saveToLocalStorage(loaded!);

    const unlocked = DocumentPersistence.loadFromLocalStorage('doc-locking');
    expect(unlocked?.sections[0].locked).toBe(false);
  });
});

describe('Tag Management Workflow', () => {
  it('should add and manage tags', async () => {
    const document: DocumentModel = {
      id: 'doc-tags',
      title: 'Tagged Document',
      sections: [],
      tags: [
        {
          id: 'tag-001',
          name: 'mathematics',
          category: 'topic',
          color: '#FF6B6B',
          aiGenerated: false,
        },
        {
          id: 'tag-002',
          name: 'physics',
          category: 'topic',
          color: '#4ECDC4',
          aiGenerated: false,
        },
      ],
      metadata: {
        totalWords: 0,
        totalSections: 0,
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

    DocumentPersistence.saveToLocalStorage(document);
    const loaded = DocumentPersistence.loadFromLocalStorage('doc-tags');

    expect(loaded?.tags).toHaveLength(2);
    expect(loaded?.tags.find(t => t.name === 'mathematics')).toBeDefined();
    expect(loaded?.tags.find(t => t.name === 'physics')).toBeDefined();

    // Add new tag
    loaded!.tags.push({
      id: 'tag-003',
      name: 'chemistry',
      category: 'topic',
      color: '#45B7D1',
      aiGenerated: false,
    });

    DocumentPersistence.saveToLocalStorage(loaded!);
    const updated = DocumentPersistence.loadFromLocalStorage('doc-tags');
    expect(updated?.tags).toHaveLength(3);
  });
});

describe('Complete User Journey', () => {
  it('should complete full document lifecycle', async () => {
    // 1. Create document
    const document: DocumentModel = {
      id: 'doc-lifecycle',
      title: 'Lifecycle Document',
      sections: [
        {
          id: 'section-001',
          title: 'Introduction',
          content: 'Initial content',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
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

    // 2. Save locally
    DocumentPersistence.saveToLocalStorage(document);

    // 3. Add section
    document.sections.push({
      id: 'section-002',
      title: 'Body',
      content: 'Body content',
      type: 'text',
      tags: [],
      metadata: {},
      version: 1,
      locked: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    document.metadata.totalSections = 2;
    DocumentPersistence.saveToLocalStorage(document);

    // 4. Add tags
    document.tags.push({
      id: 'tag-001',
      name: 'test',
      category: 'topic',
      color: '#FF6B6B',
      aiGenerated: false,
    });
    DocumentPersistence.saveToLocalStorage(document);

    // 5. Export to Markdown
    const markdown = await DocumentExporter.exportDocument(document, {
      format: 'markdown',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof markdown).toBe('string');
    expect(markdown).toContain('Lifecycle Document');
    expect(markdown).toContain('Introduction');
    expect(markdown).toContain('Body');

    // 6. Load and verify
    const loaded = DocumentPersistence.loadFromLocalStorage('doc-lifecycle');
    expect(loaded?.sections).toHaveLength(2);
    expect(loaded?.tags).toHaveLength(1);
    expect(loaded?.version).toBe(1);
  });
});

