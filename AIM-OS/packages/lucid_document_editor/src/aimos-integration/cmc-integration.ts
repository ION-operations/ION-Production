/**
 * LUCID Document Editor - CMC Integration
 * 
 * Integration with Context Memory Core for document storage
 */

import { DocumentModel } from '../models';

export interface CMCConfig {
  endpoint?: string; // HTTP endpoint for CMC API
  mcpServer?: boolean; // Use MCP tools instead
}

export interface AtomCreate {
  modality: string;
  content: {
    inline?: string;
    external?: string;
    media_type?: string;
  };
  tags?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface Atom {
  id: string;
  modality: string;
  content: {
    inline?: string;
    external?: string;
    media_type?: string;
  };
  tags: Record<string, any>;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export class CMCIntegration {
  private config: CMCConfig;

  constructor(config: CMCConfig = {}) {
    this.config = config;
  }

  /**
   * Store document in CMC
   */
  async storeDocument(document: DocumentModel, correlationId?: string): Promise<string> {
    // Convert document to atom
    const atom: AtomCreate = {
      modality: 'document',
      content: {
        inline: JSON.stringify(document),
        media_type: 'application/json',
      },
      tags: {
        type: 'document',
        documentId: document.id,
        title: document.title,
        ...document.tags.reduce((acc, tag) => {
          acc[tag.category] = tag.name;
          return acc;
        }, {} as Record<string, string>),
      },
      metadata: {
        ...document.metadata,
        totalSections: document.sections.length,
        version: document.version,
      },
    };

    if (this.config.mcpServer) {
      // Use MCP tools (would call mcp_lucid-mcp_store_memory)
      // For now, return mock atom ID
      return `atom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    } else if (this.config.endpoint) {
      // Call HTTP API
      const response = await fetch(`${this.config.endpoint}/atoms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ atom, correlation_id: correlationId }),
      });
      const data = await response.json();
      return data.atom_id;
    } else {
      // Fallback: return mock ID
      console.warn('CMC endpoint not configured, returning mock atom ID');
      return `atom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
  }

  /**
   * Load document from CMC
   */
  async loadDocument(atomId: string): Promise<DocumentModel | null> {
    if (this.config.mcpServer) {
      // Use MCP tools (would call mcp_lucid-mcp_retrieve_memory)
      // For now, return null
      return null;
    } else if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/atoms/${atomId}`);
      if (!response.ok) return null;
      const data = await response.json();
      return JSON.parse(data.atom.content.inline || '{}');
    } else {
      console.warn('CMC endpoint not configured');
      return null;
    }
  }

  /**
   * Query documents with bitemporal support
   */
  async queryDocuments(query: {
    tags?: Record<string, any>;
    asOfTime?: Date;
    limit?: number;
  }): Promise<DocumentModel[]> {
    if (this.config.mcpServer) {
      // Use MCP tools
      return [];
    } else if (this.config.endpoint) {
      const params = new URLSearchParams();
      if (query.tags) {
        params.append('tags', JSON.stringify(query.tags));
      }
      if (query.asOfTime) {
        params.append('as_of_time', query.asOfTime.toISOString());
      }
      if (query.limit) {
        params.append('limit', query.limit.toString());
      }

      const response = await fetch(`${this.config.endpoint}/atoms?${params}`);
      if (!response.ok) return [];
      const data = await response.json();
      return data.atoms.map((atom: Atom) => JSON.parse(atom.content.inline || '{}'));
    } else {
      return [];
    }
  }

  /**
   * Create snapshot
   */
  async createSnapshot(note?: string): Promise<string> {
    if (this.config.mcpServer) {
      // Use MCP tools (would call mcp_lucid-mcp_create_snapshot)
      return `snapshot-${Date.now()}`;
    } else if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/snapshots`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note }),
      });
      const data = await response.json();
      return data.snapshot_id;
    } else {
      return `snapshot-${Date.now()}`;
    }
  }
}

