/**
 * HHNI Client - Tag Resolution
 * 
 * TypeScript client for HHNI (Hierarchical Hypergraph Neural Index)
 * Phase 3: Real System Integration
 * 
 * Purpose: Resolve PLIX tags to QAddr using HHNI hierarchical index
 */

import type { QAddrLiteral } from '../models/quaternion-types';

/**
 * HHNI Query Result
 */
export interface HHNIQueryResult {
  nodeId: string;
  content: string;
  score: number;
  metadata?: Record<string, any>;
  qaddr?: QAddrLiteral;
}

/**
 * HHNI Client Interface
 */
export interface HHNIClient {
  /**
   * Query HHNI for tag → QAddr resolution
   */
  resolveTagToQAddr(tag: string): Promise<QAddrLiteral | null>;
  
  /**
   * Query HHNI for semantic search
   */
  query(query: string, maxResults?: number): Promise<HHNIQueryResult[]>;
  
  /**
   * Get node by ID
   */
  getNode(nodeId: string): Promise<HHNIQueryResult | null>;
}

/**
 * HHNI HTTP API Client
 * 
 * Communicates with HHNI service via HTTP API
 * 
 * Note: Assumes HHNI exposes HTTP API. If not, we'll need to:
 * 1. Create HTTP API wrapper for HHNI Python service, OR
 * 2. Use Node.js Python bridge
 */
export class HHNIHTTPClient implements HHNIClient {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:5001/api/hhni/v1') {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Resolve PLIX tag to QAddr using HHNI
   */
  async resolveTagToQAddr(tag: string): Promise<QAddrLiteral | null> {
    try {
      // Query HHNI for tag
      const results = await this.query(tag, 1);
      
      if (results.length === 0) {
        return null;
      }
      
      const topResult = results[0];
      
      // Extract QAddr from result metadata or content
      if (topResult.qaddr) {
        return topResult.qaddr;
      }
      
      // Try to extract QAddr from metadata
      if (topResult.metadata?.qaddr) {
        return this.normalizeQAddr(topResult.metadata.qaddr);
      }
      
      // Try to parse QAddr from content (if stored as JSON)
      try {
        const content = JSON.parse(topResult.content);
        if (content.qaddr) {
          return this.normalizeQAddr(content.qaddr);
        }
      } catch {
        // Content is not JSON, continue
      }
      
      return null;
    } catch (error: any) {
      throw new Error(`HHNI tag resolution failed: ${error.message}`);
    }
  }
  
  /**
   * Query HHNI for semantic search
   */
  async query(query: string, maxResults: number = 10): Promise<HHNIQueryResult[]> {
    try {
      const response = await fetch(`${this.baseUrl}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          max_results: maxResults,
          target_level: 'paragraph', // Query at paragraph level
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HHNI query failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const results = await response.json();
      
      // Transform HHNI results to our format
      return results.map((node: any) => ({
        nodeId: node.id || node.node_id,
        content: node.content || node.summary || '',
        score: node.score || node.similarity || 0.0,
        metadata: node.metadata || {},
        qaddr: node.qaddr ? this.normalizeQAddr(node.qaddr) : undefined,
      }));
    } catch (error: any) {
      throw new Error(`HHNI query failed: ${error.message}`);
    }
  }
  
  /**
   * Get node by ID
   */
  async getNode(nodeId: string): Promise<HHNIQueryResult | null> {
    try {
      const response = await fetch(`${this.baseUrl}/nodes/${nodeId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.status === 404) {
        return null;
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HHNI get node failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const node = await response.json();
      
      return {
        nodeId: node.id || node.node_id,
        content: node.content || node.summary || '',
        score: 1.0, // Full match
        metadata: node.metadata || {},
        qaddr: node.qaddr ? this.normalizeQAddr(node.qaddr) : undefined,
      };
    } catch (error: any) {
      throw new Error(`HHNI get node failed: ${error.message}`);
    }
  }
  
  /**
   * Helper: Normalize QAddr to QAddrLiteral format
   */
  private normalizeQAddr(qaddr: any): QAddrLiteral {
    return {
      type: 'qaddr',
      n: qaddr.n || qaddr.principal_shell || 1,
      l: qaddr.l || qaddr.orbital_class || 'memory',
      m: qaddr.m || qaddr.magnetic_channel || 0,
      s: qaddr.s || qaddr.spin || 'plan',
      morton_key: qaddr.morton_key || qaddr.morton4d || 0,
      s3_bin: qaddr.s3_bin || qaddr.s3bin || 0,
    };
  }
}

/**
 * Mock HHNI Client
 * 
 * In-memory implementation for testing
 */
export class MockHHNIClient implements HHNIClient {
  private tagToQAddr: Map<string, QAddrLiteral>;
  
  constructor() {
    this.tagToQAddr = new Map();
  }
  
  /**
   * Register a tag → QAddr mapping for testing
   */
  registerTag(tag: string, qaddr: QAddrLiteral): void {
    this.tagToQAddr.set(tag, qaddr);
  }
  
  async resolveTagToQAddr(tag: string): Promise<QAddrLiteral | null> {
    return this.tagToQAddr.get(tag) || null;
  }
  
  async query(query: string, maxResults: number = 10): Promise<HHNIQueryResult[]> {
    // Simple mock: return empty results
    return [];
  }
  
  async getNode(nodeId: string): Promise<HHNIQueryResult | null> {
    return null;
  }
}

