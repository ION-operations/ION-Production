/**
 * LUCID Document Editor - SEG Integration
 * 
 * Integration with Shared Evidence Graph for knowledge relationships
 */

import { DocumentModel } from '../models';

export interface SEGConfig {
  endpoint?: string;
  mcpServer?: boolean;
}

export interface SEGEntity {
  id: string;
  type: string;
  name: string;
  attributes: Record<string, any>;
}

export interface SEGRelation {
  id: string;
  source_id: string;
  target_id: string;
  relation_type: string;
  confidence: number;
}

export class SEGIntegration {
  private config: SEGConfig;

  constructor(config: SEGConfig = {}) {
    this.config = config;
  }

  /**
   * Link document to SEG
   */
  async linkDocument(document: DocumentModel): Promise<string> {
    const entity: SEGEntity = {
      id: `entity-${document.id}`,
      type: 'document',
      name: document.title,
      attributes: {
        documentId: document.id,
        description: document.description,
        totalSections: document.sections.length,
        tags: document.tags.map(t => t.name),
        ...document.metadata,
      },
    };

    if (this.config.mcpServer) {
      // Use MCP tools
      return entity.id;
    } else if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entity),
      });
      const data = await response.json();
      return data.entity_id;
    } else {
      return entity.id;
    }
  }

  /**
   * Create relationship between documents
   */
  async createRelationship(params: {
    sourceId: string;
    targetId: string;
    type: string;
    confidence?: number;
  }): Promise<string> {
    const relation: SEGRelation = {
      id: `relation-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      source_id: params.sourceId,
      target_id: params.targetId,
      relation_type: params.type,
      confidence: params.confidence || 0.8,
    };

    if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/relations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(relation),
      });
      const data = await response.json();
      return data.relation_id;
    } else {
      return relation.id;
    }
  }

  /**
   * Query document relationships
   */
  async queryRelationships(documentId: string): Promise<SEGRelation[]> {
    if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/entities/${documentId}/relations`);
      const data = await response.json();
      return data.relations || [];
    } else {
      return [];
    }
  }

  /**
   * Find related documents
   */
  async findRelatedDocuments(documentId: string, limit: number = 10): Promise<string[]> {
    const relations = await this.queryRelationships(documentId);
    const relatedIds = new Set<string>();

    relations.forEach(rel => {
      if (rel.source_id === documentId) {
        relatedIds.add(rel.target_id);
      } else if (rel.target_id === documentId) {
        relatedIds.add(rel.source_id);
      }
    });

    return Array.from(relatedIds).slice(0, limit);
  }
}

