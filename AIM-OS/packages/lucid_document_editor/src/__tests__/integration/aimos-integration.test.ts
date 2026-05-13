/**
 * LUCID Document Editor - Integration Tests
 * 
 * Integration tests for AIM-OS systems and collaboration
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { DocumentModel } from '../models';
import { CMCIntegration } from '../aimos-integration/cmc-integration';
import { VIFIntegration } from '../aimos-integration/vif-integration';
import { SEGIntegration } from '../aimos-integration/seg-integration';
import { HHNIIntegration } from '../aimos-integration/hhni-integration';
import { APOEIntegration } from '../aimos-integration/apoe-integration';
import { AIMOSIntegrationManager } from '../aimos-integration/aimos-manager';
import { CollaborationEngine } from '../collaboration/collaboration-engine';
import { DocumentExporter } from '../aimos-integration/export-import';

// Mock fetch for HTTP API tests
global.fetch = vi.fn();

describe('CMC Integration', () => {
  let cmc: CMCIntegration;

  beforeEach(() => {
    cmc = new CMCIntegration({ endpoint: 'http://localhost:8000' });
    vi.clearAllMocks();
  });

  describe('HTTP API Integration', () => {
    it('should store document via HTTP API', async () => {
      const document: DocumentModel = {
        id: 'doc-001',
        title: 'Test Document',
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
        json: async () => ({ atom_id: 'atom-123' }),
      });

      const atomId = await cmc.storeDocument(document);
      expect(atomId).toBe('atom-123');
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/atoms',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    it('should load document via HTTP API', async () => {
      const document: DocumentModel = {
        id: 'doc-001',
        title: 'Test Document',
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

      const loaded = await cmc.loadDocument('atom-123');
      expect(loaded).toBeDefined();
      expect(loaded?.id).toBe('doc-001');
    });

    it('should query documents with bitemporal support', async () => {
      const documents: DocumentModel[] = [
        {
          id: 'doc-001',
          title: 'Document 1',
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
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          atoms: documents.map(doc => ({
            content: { inline: JSON.stringify(doc) },
          })),
        }),
      });

      const results = await cmc.queryDocuments({
        tags: { topic: 'mathematics' },
        asOfTime: new Date('2025-11-01'),
        limit: 10,
      });

      expect(results).toHaveLength(1);
      expect(results[0].id).toBe('doc-001');
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const atomId = await cmc.storeDocument({
        id: 'doc-001',
        title: 'Test',
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
      });

      // Should return mock ID on error
      expect(atomId).toBeDefined();
    });
  });

  describe('MCP Server Integration', () => {
    it('should use MCP server when configured', async () => {
      const mcpCMC = new CMCIntegration({ mcpServer: true });
      const document: DocumentModel = {
        id: 'doc-001',
        title: 'Test Document',
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

      const atomId = await mcpCMC.storeDocument(document);
      expect(atomId).toBeDefined();
      expect(atomId).toMatch(/^atom-/);
    });
  });
});

describe('VIF Integration', () => {
  let vif: VIFIntegration;

  beforeEach(() => {
    vif = new VIFIntegration({ endpoint: 'http://localhost:8000' });
    vi.clearAllMocks();
  });

  it('should create witness via HTTP API', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 'vif-123',
        operation: 'document_save',
        confidence: 0.95,
      }),
    });

    const witness = await vif.createWitness({
      operation: 'document_save',
      inputs: { documentId: 'doc-001' },
      outputs: { atomId: 'atom-123' },
      confidence: 0.95,
    });

    expect(witness.id).toBe('vif-123');
    expect(global.fetch).toHaveBeenCalled();
  });

  it('should verify witness', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ verified: true }),
    });

    const verified = await vif.verifyWitness('vif-123');
    expect(verified).toBe(true);
  });

  it('should get witness lineage', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        lineage: [
          { id: 'vif-001', operation: 'create' },
          { id: 'vif-002', operation: 'update' },
        ],
      }),
    });

    const lineage = await vif.getWitnessLineage('vif-123');
    expect(lineage).toHaveLength(2);
  });
});

describe('SEG Integration', () => {
  let seg: SEGIntegration;

  beforeEach(() => {
    seg = new SEGIntegration({ endpoint: 'http://localhost:8000' });
    vi.clearAllMocks();
  });

  it('should link document to SEG', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ entity_id: 'entity-123' }),
    });

    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
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

    const entityId = await seg.linkDocument(document);
    expect(entityId).toBe('entity-123');
  });

  it('should create relationships', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ relation_id: 'relation-123' }),
    });

    const relationId = await seg.createRelationship({
      sourceId: 'doc-001',
      targetId: 'doc-002',
      type: 'references',
      confidence: 0.9,
    });

    expect(relationId).toBe('relation-123');
  });

  it('should query relationships', async () => {
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
        ],
      }),
    });

    const relations = await seg.queryRelationships('doc-001');
    expect(relations).toHaveLength(1);
    expect(relations[0].relation_type).toBe('references');
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

    const related = await seg.findRelatedDocuments('doc-001');
    expect(related).toContain('doc-002');
    expect(related).toContain('doc-003');
  });
});

describe('HHNI Integration', () => {
  let hhni: HHNIIntegration;

  beforeEach(() => {
    hhni = new HHNIIntegration({ endpoint: 'http://localhost:8000' });
    vi.clearAllMocks();
  });

  it('should index document', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
    });

    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
      sections: [
        {
          id: 'section-001',
          title: 'Section 1',
          content: 'Content here',
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

    await hhni.indexDocument(document);
    expect(global.fetch).toHaveBeenCalled();
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
        ],
      }),
    });

    const results = await hhni.search({
      query: 'mathematical proof',
      limit: 10,
    });

    expect(results).toHaveLength(1);
    expect(results[0].node_id).toBe('node-001');
  });

  it('should get hierarchical context', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        context: [
          {
            node_id: 'node-001',
            score: 0.9,
            confidence: 0.85,
            content: 'Related content',
            level: 2,
          },
        ],
      }),
    });

    const context = await hhni.getContext({
      documentId: 'doc-001',
      depth: 3,
    });

    expect(context).toHaveLength(1);
  });
});

describe('APOE Integration', () => {
  let apoe: APOEIntegration;

  beforeEach(() => {
    apoe = new APOEIntegration({ endpoint: 'http://localhost:8000' });
    vi.clearAllMocks();
  });

  it('should create execution plan', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 'plan-123',
        goal: 'Process document',
        steps: [
          {
            id: 'step-001',
            action: 'analyze',
            parameters: {},
            confidence: 0.9,
          },
        ],
        confidence: 0.85,
      }),
    });

    const plan = await apoe.createPlan({
      goal: 'Process document',
      priority: 'high',
    });

    expect(plan.id).toBe('plan-123');
    expect(plan.steps).toHaveLength(1);
  });

  it('should execute workflow', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        result: { processed: true },
      }),
    });

    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
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

    const result = await apoe.executeWorkflow({
      workflow: 'process_document',
      document,
    });

    expect(result.success).toBe(true);
  });
});

describe('AIM-OS Integration Manager', () => {
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

  it('should save document with full integration', async () => {
    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
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
            content: 'Result',
            level: 1,
          },
        ],
      }),
    });

    const results = await manager.semanticSearch('query', 10);
    expect(results).toHaveLength(1);
  });

  it('should export document', async () => {
    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
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

    const exported = await manager.exportDocument(document, 'markdown');
    expect(exported).toBeDefined();
    expect(typeof exported).toBe('string');
  });
});

describe('Yjs Collaboration Integration', () => {
  it('should initialize collaboration engine', () => {
    const engine = new CollaborationEngine({
      documentId: 'doc-001',
      userId: 'user-001',
      userName: 'Test User',
      websocketUrl: 'ws://localhost:5001',
    });

    expect(engine).toBeDefined();
  });

  it('should handle document sync', async () => {
    const engine = new CollaborationEngine({
      documentId: 'doc-001',
      userId: 'user-001',
      userName: 'Test User',
      websocketUrl: 'ws://localhost:5001',
    });

    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
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

    engine.syncDocument(document);
    const synced = engine.getDocument();
    expect(synced.id).toBe('doc-001');
    expect(synced.sections).toHaveLength(1);
  });

  it('should handle section updates', () => {
    const engine = new CollaborationEngine({
      documentId: 'doc-001',
      userId: 'user-001',
      userName: 'Test User',
      websocketUrl: 'ws://localhost:5001',
    });

    engine.updateSection('section-001', 'New content');
    const document = engine.getDocument();
    const section = document.sections.find(s => s.id === 'section-001');
    expect(section?.content).toBe('New content');
  });

  it('should handle comments', () => {
    const engine = new CollaborationEngine({
      documentId: 'doc-001',
      userId: 'user-001',
      userName: 'Test User',
      websocketUrl: 'ws://localhost:5001',
    });

    const comment = engine.addComment({
      sectionId: 'section-001',
      position: { offset: 10 },
      content: 'This needs clarification',
      author: 'user-001',
      authorName: 'Test User',
    });

    expect(comment.id).toBeDefined();
    expect(comment.content).toBe('This needs clarification');

    const comments = engine.getComments('section-001');
    expect(comments).toHaveLength(1);
  });

  it('should track user presence', () => {
    const engine = new CollaborationEngine({
      documentId: 'doc-001',
      userId: 'user-001',
      userName: 'Test User',
      websocketUrl: 'ws://localhost:5001',
    });

    engine.updateCursor('section-001', 10);
    engine.updateSelection('section-001', 5, 15);

    const users = engine.getActiveUsers();
    // Initially empty until connected
    expect(Array.isArray(users)).toBe(true);
  });
});

describe('Export/Import Integration', () => {
  it('should export to LaTeX', async () => {
    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
      sections: [
        {
          id: 'section-001',
          title: 'Introduction',
          content: 'This is the introduction.',
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

    const latex = await DocumentExporter.exportDocument(document, {
      format: 'latex',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof latex).toBe('string');
    expect(latex).toContain('\\documentclass');
    expect(latex).toContain('Test Document');
    expect(latex).toContain('Introduction');
  });

  it('should export to HTML', async () => {
    const document: DocumentModel = {
      id: 'doc-001',
      title: 'Test Document',
      sections: [
        {
          id: 'section-001',
          title: 'Introduction',
          content: 'This is the introduction.',
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

    const html = await DocumentExporter.exportDocument(document, {
      format: 'html',
      includeMetadata: true,
      includeHistory: false,
      includeComments: false,
      compress: false,
    });

    expect(typeof html).toBe('string');
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('Test Document');
  });

  it('should import from LaTeX', async () => {
    const latex = `\\documentclass{article}
\\title{Test Document}
\\begin{document}
\\section{Introduction}
This is the introduction.
\\end{document}`;

    const document = await DocumentExporter.importDocument(latex, {
      format: 'latex',
      merge: false,
      preserveHistory: false,
    });

    expect(document.title).toBe('Test Document');
    expect(document.sections).toHaveLength(1);
    expect(document.sections[0].title).toBe('Introduction');
  });
});

