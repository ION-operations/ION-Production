/**
 * SEG Client - Provenance Tracking
 * 
 * TypeScript client for SEG (Shared Evidence Graph)
 * Phase 3: Real System Integration
 * 
 * Purpose: Track entity lineage and syscall provenance
 */

import type { QAddrLiteral } from '../models/quaternion-types';

/**
 * SEG Entity
 */
export interface SEGEntity {
  id: string;
  type: string;
  name: string;
  attributes?: Record<string, any>;
}

/**
 * SEG Relation
 */
export interface SEGRelation {
  id: string;
  sourceId: string;
  targetId: string;
  relationType: string;
  confidence: number;
}

/**
 * SEG Evidence
 */
export interface SEGEvidence {
  id: string;
  content: string;
  source: string;
  confidence: number;
}

/**
 * SEG Client Interface
 */
export interface SEGClient {
  /**
   * Track entity creation
   */
  trackEntityCreation(
    entityId: string,
    qaddr: QAddrLiteral,
    sourceTag: string
  ): Promise<void>;
  
  /**
   * Track syscall execution
   */
  trackSyscall(
    entityId: string,
    syscallType: 'place' | 'move' | 'sense' | 'emit',
    result: { success: boolean; errors: string[] }
  ): Promise<void>;
  
  /**
   * Get entity lineage
   */
  getEntityLineage(entityId: string): Promise<SEGEntity[]>;
  
  /**
   * Get entity relations
   */
  getEntityRelations(entityId: string): Promise<SEGRelation[]>;
}

/**
 * SEG HTTP API Client
 * 
 * Communicates with SEG service via HTTP API
 * 
 * Note: Assumes SEG exposes HTTP API. If not, we'll need to:
 * 1. Create HTTP API wrapper for SEG Python service, OR
 * 2. Use Node.js Python bridge
 */
export class SEGHTTPClient implements SEGClient {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:5002/api/seg/v1') {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Track entity creation in SEG
   */
  async trackEntityCreation(
    entityId: string,
    qaddr: QAddrLiteral,
    sourceTag: string
  ): Promise<void> {
    try {
      // Create entity node
      const entity: SEGEntity = {
        id: entityId,
        type: 'quaternion_entity',
        name: entityId,
        attributes: {
          qaddr: qaddr,
          source_tag: sourceTag,
        },
      };
      
      const response = await fetch(`${this.baseUrl}/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entity),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`SEG entity creation failed: HTTP ${response.status}: ${errorText}`);
      }
      
      // Create relation to source if sourceTag exists
      if (sourceTag) {
        await this.createRelation(sourceTag, entityId, 'derives_from', 1.0);
      }
    } catch (error: any) {
      throw new Error(`Failed to track entity creation in SEG: ${error.message}`);
    }
  }
  
  /**
   * Track syscall execution in SEG
   */
  async trackSyscall(
    entityId: string,
    syscallType: 'place' | 'move' | 'sense' | 'emit',
    result: { success: boolean; errors: string[] }
  ): Promise<void> {
    try {
      // Create evidence node for syscall
      const evidence: SEGEvidence = {
        id: `${entityId}_${syscallType}_${Date.now()}`,
        content: `${syscallType} syscall on ${entityId}`,
        source: 'quaternion_kernel',
        confidence: result.success ? 1.0 : 0.0,
      };
      
      const response = await fetch(`${this.baseUrl}/evidence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(evidence),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`SEG evidence creation failed: HTTP ${response.status}: ${errorText}`);
      }
      
      // Create relation from entity to evidence
      await this.createRelation(entityId, evidence.id, 'has_evidence', 1.0);
    } catch (error: any) {
      // Non-fatal: log but don't throw
      console.warn(`Failed to track syscall in SEG: ${error.message}`);
    }
  }
  
  /**
   * Get entity lineage (provenance chain)
   */
  async getEntityLineage(entityId: string): Promise<SEGEntity[]> {
    try {
      const response = await fetch(`${this.baseUrl}/entities/${entityId}/lineage`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.status === 404) {
        return [];
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`SEG lineage query failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const lineage = await response.json();
      return lineage.entities || [];
    } catch (error: any) {
      throw new Error(`Failed to get entity lineage from SEG: ${error.message}`);
    }
  }
  
  /**
   * Get entity relations
   */
  async getEntityRelations(entityId: string): Promise<SEGRelation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/entities/${entityId}/relations`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.status === 404) {
        return [];
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`SEG relations query failed: HTTP ${response.status}: ${errorText}`);
      }
      
      const relations = await response.json();
      return relations.relations || [];
    } catch (error: any) {
      throw new Error(`Failed to get entity relations from SEG: ${error.message}`);
    }
  }
  
  /**
   * Helper: Create relation
   */
  private async createRelation(
    sourceId: string,
    targetId: string,
    relationType: string,
    confidence: number
  ): Promise<void> {
    const relation: SEGRelation = {
      id: `${sourceId}_${relationType}_${targetId}_${Date.now()}`,
      sourceId: sourceId,
      targetId: targetId,
      relationType: relationType,
      confidence: confidence,
    };
    
    const response = await fetch(`${this.baseUrl}/relations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(relation),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`SEG relation creation failed: HTTP ${response.status}: ${errorText}`);
    }
  }
}

/**
 * Mock SEG Client
 * 
 * In-memory implementation for testing
 */
export class MockSEGClient implements SEGClient {
  private entities: Map<string, SEGEntity>;
  private relations: Map<string, SEGRelation>;
  
  constructor() {
    this.entities = new Map();
    this.relations = new Map();
  }
  
  async trackEntityCreation(
    entityId: string,
    qaddr: QAddrLiteral,
    sourceTag: string
  ): Promise<void> {
    const entity: SEGEntity = {
      id: entityId,
      type: 'quaternion_entity',
      name: entityId,
      attributes: {
        qaddr: qaddr,
        source_tag: sourceTag,
      },
    };
    
    this.entities.set(entityId, entity);
    
    if (sourceTag) {
      const relation: SEGRelation = {
        id: `${sourceTag}_derives_from_${entityId}`,
        sourceId: sourceTag,
        targetId: entityId,
        relationType: 'derives_from',
        confidence: 1.0,
      };
      this.relations.set(relation.id, relation);
    }
  }
  
  async trackSyscall(
    entityId: string,
    syscallType: 'place' | 'move' | 'sense' | 'emit',
    result: { success: boolean; errors: string[] }
  ): Promise<void> {
    // Mock: just log
    console.log(`[Mock SEG] Tracked ${syscallType} syscall on ${entityId}: ${result.success ? 'success' : 'failed'}`);
  }
  
  async getEntityLineage(entityId: string): Promise<SEGEntity[]> {
    const lineage: SEGEntity[] = [];
    const entity = this.entities.get(entityId);
    if (entity) {
      lineage.push(entity);
    }
    return lineage;
  }
  
  async getEntityRelations(entityId: string): Promise<SEGRelation[]> {
    const relations: SEGRelation[] = [];
    for (const relation of this.relations.values()) {
      if (relation.sourceId === entityId || relation.targetId === entityId) {
        relations.push(relation);
      }
    }
    return relations;
  }
}

