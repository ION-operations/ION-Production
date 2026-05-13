/**
 * CMC Storage Client
 * 
 * TypeScript client for CMC (Context Memory Core) storage
 * Phase 2: Real System Integration
 * 
 * Note: This assumes CMC exposes an HTTP API. If not, we'll need to:
 * 1. Create HTTP API wrapper for CMC Python service, OR
 * 2. Use Node.js Python bridge (python-shell, child_process), OR
 * 3. Create direct TypeScript implementation
 */

import type { QAddrLiteral } from '../models/quaternion-types';
import type { CMCStorage } from './quaternion-runtime';

/**
 * Entity State stored in CMC
 */
export interface EntityState {
  qaddr: QAddrLiteral;
  pose: {
    rotation: { w: number; x: number; y: number; z: number };
    translation: { w: number; x: number; y: number; z: number };
  };
  fields?: {
    kappa: number;
    lambda: number;
    rho: number;
  };
  quantumContext?: any;
  metadata?: Record<string, any>;
}

/**
 * CMC HTTP API Client
 * 
 * Communicates with CMC service via HTTP API
 */
export class CMCStorageClient implements CMCStorage {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:5000/api/cmc/v1') {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Store entity with QAddr in CMC
   */
  async storeEntity(
    entityId: string,
    qaddr: QAddrLiteral,
    state: EntityState
  ): Promise<void> {
    try {
      const atomCreate = {
        modality: 'quaternion_entity',
        content: {
          inline: {
            entity_id: entityId,
            qaddr: qaddr,
            pose: state.pose,
            fields: state.fields || { kappa: 0.5, lambda: 0.0, rho: 0.5 },
            quantumContext: state.quantumContext,
            ...state.metadata,
          },
        },
        tags: {
          entity_id: entityId,
          qaddr_n: qaddr.n.toString(),
          qaddr_l: qaddr.l,
          qaddr_s: qaddr.s,
          morton_key: (qaddr.morton_key || 0).toString(),
          s3_bin: (qaddr.s3_bin || 0).toString(),
        },
        metadata: {
          created_at: new Date().toISOString(),
          valid_from: new Date().toISOString(),
          valid_to: null,
        },
      };
      
      const response = await fetch(`${this.baseUrl}/atoms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(atomCreate),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`CMC storage failed: HTTP ${response.status}: ${errorText}`);
      }
      
      // Atom created successfully
      const atom = await response.json();
      if (!atom.id) {
        throw new Error('CMC returned atom without ID');
      }
    } catch (error: any) {
      throw new Error(`Failed to store entity in CMC: ${error.message}`);
    }
  }
  
  /**
   * Retrieve entity state from CMC
   */
  async retrieveEntity(entityId: string): Promise<EntityState | null> {
    try {
      const response = await fetch(`${this.baseUrl}/atoms/${entityId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.status === 404) {
        return null;
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`CMC retrieval failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const atom = await response.json();
      
      if (atom.modality !== 'quaternion_entity') {
        return null;
      }
      
      const content = atom.content?.inline;
      if (!content) {
        return null;
      }
      
      return {
        qaddr: content.qaddr,
        pose: content.pose,
        fields: content.fields,
        quantumContext: content.quantumContext,
        metadata: atom.metadata,
      };
    } catch (error: any) {
      throw new Error(`Failed to retrieve entity from CMC: ${error.message}`);
    }
  }
  
  /**
   * Update entity state in CMC (bitemporal)
   */
  async updateEntity(
    entityId: string,
    qaddr: QAddrLiteral,
    state: EntityState
  ): Promise<void> {
    try {
      // CMC bitemporal update: create new atom version
      const atomCreate = {
        modality: 'quaternion_entity',
        content: {
          inline: {
            entity_id: entityId,
            qaddr: qaddr,
            pose: state.pose,
            fields: state.fields,
            quantumContext: state.quantumContext,
            ...state.metadata,
          },
        },
        tags: {
          entity_id: entityId,
          qaddr_n: qaddr.n.toString(),
          qaddr_l: qaddr.l,
          qaddr_s: qaddr.s,
          morton_key: (qaddr.morton_key || 0).toString(),
          s3_bin: (qaddr.s3_bin || 0).toString(),
        },
        metadata: {
          updated_at: new Date().toISOString(),
          valid_from: new Date().toISOString(),
          valid_to: null,
          previous_version: entityId, // Link to previous version
        },
      };
      
      const response = await fetch(`${this.baseUrl}/atoms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(atomCreate),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`CMC update failed: HTTP ${response.status}: ${errorText}`);
      }
    } catch (error: any) {
      throw new Error(`Failed to update entity in CMC: ${error.message}`);
    }
  }
  
  /**
   * Query entities by QAddr
   */
  async queryByQAddr(qaddr: QAddrLiteral): Promise<string[]> {
    try {
      const query = {
        tags: {
          qaddr_n: qaddr.n.toString(),
          qaddr_l: qaddr.l,
          morton_key: (qaddr.morton_key || 0).toString(),
        },
        limit: 100,
      };
      
      const response = await fetch(`${this.baseUrl}/atoms/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`CMC query failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const results = await response.json();
      
      // Extract entity IDs from results
      return results.map((atom: any) => {
        const content = atom.content?.inline;
        return content?.entity_id || atom.id;
      }).filter((id: string) => id);
    } catch (error: any) {
      throw new Error(`Failed to query entities by QAddr: ${error.message}`);
    }
  }
  
  /**
   * Query entities by spatial region
   */
  async queryByRegion(region: {
    center: { x: number; y: number; z: number; tau: number };
    radius: number;
  }): Promise<string[]> {
    try {
      // Query by morton_key range (simplified)
      // In production, would use proper spatial indexing
      const minMorton = this.calculateMortonKey(
        region.center.x - region.radius,
        region.center.y - region.radius,
        region.center.z - region.radius,
        region.center.tau
      );
      const maxMorton = this.calculateMortonKey(
        region.center.x + region.radius,
        region.center.y + region.radius,
        region.center.z + region.radius,
        region.center.tau
      );
      
      const query = {
        tags: {
          morton_key_min: minMorton.toString(),
          morton_key_max: maxMorton.toString(),
        },
        limit: 100,
      };
      
      const response = await fetch(`${this.baseUrl}/atoms/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`CMC region query failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const results = await response.json();
      
      // Filter by actual distance and extract entity IDs
      const entityIds: string[] = [];
      for (const atom of results) {
        const content = atom.content?.inline;
        if (!content || !content.pose) continue;
        
        const distance = this.calculateDistance(
          region.center,
          content.pose.translation
        );
        
        if (distance <= region.radius) {
          entityIds.push(content.entity_id || atom.id);
        }
      }
      
      return entityIds;
    } catch (error: any) {
      throw new Error(`Failed to query entities by region: ${error.message}`);
    }
  }
  
  /**
   * Helper: Calculate Morton4D key (simplified)
   */
  private calculateMortonKey(x: number, y: number, z: number, tau: number): number {
    // Simplified Morton encoding (should use actual morton4d_encode)
    // Scale coordinates to integers
    const scale = 1000;
    const ix = Math.floor(x * scale);
    const iy = Math.floor(y * scale);
    const iz = Math.floor(z * scale);
    const itau = Math.floor(tau * scale);
    
    // Interleave bits (simplified - should use proper Morton encoding)
    let key = 0;
    for (let i = 0; i < 16; i++) {
      key |= ((ix >> i) & 1) << (i * 4);
      key |= ((iy >> i) & 1) << (i * 4 + 1);
      key |= ((iz >> i) & 1) << (i * 4 + 2);
      key |= ((itau >> i) & 1) << (i * 4 + 3);
    }
    
    return key;
  }
  
  /**
   * Helper: Calculate distance between two points
   */
  private calculateDistance(
    center: { x: number; y: number; z: number },
    point: { x: number; y: number; z: number }
  ): number {
    const dx = point.x - center.x;
    const dy = point.y - center.y;
    const dz = point.z - center.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
}

/**
 * Mock CMC Storage Client
 * 
 * In-memory implementation for testing without CMC service
 */
export class MockCMCStorage implements CMCStorage {
  private entities: Map<string, EntityState>;
  
  constructor() {
    this.entities = new Map();
  }
  
  async storeEntity(
    entityId: string,
    qaddr: QAddrLiteral,
    state: EntityState
  ): Promise<void> {
    this.entities.set(entityId, { ...state, qaddr });
  }
  
  async retrieveEntity(entityId: string): Promise<EntityState | null> {
    return this.entities.get(entityId) || null;
  }
  
  async updateEntity(
    entityId: string,
    qaddr: QAddrLiteral,
    state: EntityState
  ): Promise<void> {
    this.entities.set(entityId, { ...state, qaddr });
  }
  
  async queryByQAddr(qaddr: QAddrLiteral): Promise<string[]> {
    const results: string[] = [];
    for (const [id, state] of this.entities.entries()) {
      if (
        state.qaddr.n === qaddr.n &&
        state.qaddr.l === qaddr.l &&
        state.qaddr.morton_key === qaddr.morton_key
      ) {
        results.push(id);
      }
    }
    return results;
  }
  
  async queryByRegion(region: {
    center: { x: number; y: number; z: number; tau: number };
    radius: number;
  }): Promise<string[]> {
    const results: string[] = [];
    for (const [id, state] of this.entities.entries()) {
      if (!state.pose || !state.pose.translation) continue;
      
      const distance = Math.sqrt(
        Math.pow(state.pose.translation.x - region.center.x, 2) +
        Math.pow(state.pose.translation.y - region.center.y, 2) +
        Math.pow(state.pose.translation.z - region.center.z, 2)
      );
      
      if (distance <= region.radius) {
        results.push(id);
      }
    }
    return results;
  }
}

