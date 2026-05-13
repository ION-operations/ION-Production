/**
 * CMC Service - Context Memory Core integration
 */

import { AIMOSClient } from '../client'
import {
  CMCStoreParams,
  CMCRetrieveParams,
  CMCRetrieveResult,
} from '../types'

/**
 * CMC Service for memory storage and retrieval
 */
export class CMCService {
  constructor(private client: AIMOSClient) {}

  /**
   * Store memory atom in CMC
   * 
   * @param params Store parameters
   * @returns Atom ID and creation timestamp
   */
  async store(params: CMCStoreParams): Promise<{ atom_id: string; created_at?: string }> {
    const result = await this.client.executeTool('store_memory', {
      content: params.content,
      modality: params.modality || 'text',
      tags: params.tags || {},
      metadata: params.metadata || {},
      ...(params.embedding && { embedding: params.embedding }),
    })

    return {
      atom_id: result.atom_id || result.id,
      created_at: result.created_at,
    }
  }

  /**
   * Retrieve memories via HHNI
   * 
   * @param params Retrieve parameters
   * @returns Search results with scores and confidence
   */
  async retrieve(params: CMCRetrieveParams): Promise<CMCRetrieveResult> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: params.query,
      limit: params.limit || 10,
      ...(params.modality && { modality: params.modality }),
      ...(params.tags && { tags: params.tags }),
    })

    return {
      results: result.results || result.nodes || [],
    }
  }

  /**
   * Get CMC statistics
   * 
   * @returns Memory statistics
   */
  async getStats(): Promise<any> {
    return this.client.executeTool('get_memory_stats', {})
  }
}

