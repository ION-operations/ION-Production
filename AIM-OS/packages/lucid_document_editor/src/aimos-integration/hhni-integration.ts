/**
 * LUCID Document Editor - HHNI Integration
 * 
 * Integration with Hierarchical Hypergraph Neural Index for semantic search
 */

import { DocumentModel } from '../models';

export interface HHNIConfig {
  endpoint?: string;
  mcpServer?: boolean;
}

export interface HHNISearchResult {
  node_id: string;
  score: number;
  confidence: number;
  content: string;
  level: number;
}

export class HHNIIntegration {
  private config: HHNIConfig;

  constructor(config: HHNIConfig = {}) {
    this.config = config;
  }

  /**
   * Index document in HHNI
   */
  async indexDocument(document: DocumentModel): Promise<void> {
    if (this.config.mcpServer) {
      // Use MCP tools (would call mcp_lucid-mcp_store_memory)
      // Document indexing happens automatically via CMC
      return;
    } else if (this.config.endpoint) {
      await fetch(`${this.config.endpoint}/index`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: document.id,
          content: document.sections.map(s => s.content).join('\n'),
          metadata: document.metadata,
        }),
      });
    }
  }

  /**
   * Semantic search
   */
  async search(params: {
    query: string;
    limit?: number;
    level?: number;
  }): Promise<HHNISearchResult[]> {
    if (this.config.mcpServer) {
      // Use MCP tools (would call mcp_lucid-mcp_retrieve_memory)
      return [];
    } else if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: params.query,
          limit: params.limit || 10,
          level: params.level,
        }),
      });
      const data = await response.json();
      return data.results || [];
    } else {
      return [];
    }
  }

  /**
   * Get hierarchical context
   */
  async getContext(params: {
    documentId: string;
    depth: number;
  }): Promise<HHNISearchResult[]> {
    if (this.config.endpoint) {
      const response = await fetch(`${this.config.endpoint}/context`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: params.documentId,
          depth: params.depth,
        }),
      });
      const data = await response.json();
      return data.context || [];
    } else {
      return [];
    }
  }
}

