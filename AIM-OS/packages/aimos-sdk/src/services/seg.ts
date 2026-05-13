/**
 * SEG Service - Shared Evidence Graph integration
 */

import { AIMOSClient } from '../client'
import {
  SEGSynthesizeParams,
  SEGSynthesizeResult,
} from '../types'

/**
 * SEG Service for knowledge synthesis and graph queries
 */
export class SEGService {
  constructor(private client: AIMOSClient) {}

  /**
   * Synthesize knowledge from topics
   * 
   * @param params Synthesize parameters
   * @returns Synthesis with entities, relations, and contradictions
   */
  async synthesize(params: SEGSynthesizeParams): Promise<SEGSynthesizeResult> {
    const result = await this.client.executeTool('synthesize_knowledge', {
      topics: params.topics,
      ...(params.depth && { depth: params.depth }),
    })

    return {
      synthesis: result.synthesis || result,
    }
  }
}

