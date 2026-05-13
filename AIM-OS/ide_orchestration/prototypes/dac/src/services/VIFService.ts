/**
 * VIF Service
 * Handles Verifiable Intelligence Framework operations via MCP tools
 * Replaces mock data with real backend API calls
 */

import { mcpService } from './MCPService'
import { VIFWitness } from '../hooks/useAIMOS'

export interface TrackConfidenceRequest {
  model_id: string
  confidence_score: number
  task_criticality?: 'critical' | 'important' | 'routine' | 'low_stakes'
  context_snapshot_id?: string
  prompt_hash?: string
  prompt_tokens?: number
  output_hash?: string
  output_tokens?: number
}

/**
 * VIF Service
 * Integrates with MCP tools for VIF operations
 */
export class VIFService {
  /**
   * Track confidence via VIF
   */
  async trackConfidence(
    model_id: string,
    confidence_score: number,
    task_criticality: 'critical' | 'important' | 'routine' | 'low_stakes' = 'routine',
    context_snapshot_id?: string,
    prompt_hash?: string,
    prompt_tokens?: number,
    output_hash?: string,
    output_tokens?: number
  ): Promise<{ success: boolean; witness?: VIFWitness; witness_id?: string; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_track_confidence', {
        model_id,
        confidence_score,
        task_criticality,
        context_snapshot_id,
        prompt_hash,
        prompt_tokens,
        output_hash,
        output_tokens
      })

      if (result.success && result.result) {
        const witness = result.result.witness || result.result
        const witness_id = result.result.witness_id || witness?.id || result.result.id

        return {
          success: true,
          witness: witness as VIFWitness,
          witness_id
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to track confidence'
        }
      }
    } catch (error) {
      console.error('VIF trackConfidence error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error tracking confidence'
      }
    }
  }

  /**
   * Get witnesses (if available via MCP tool)
   * Note: This may need to be implemented differently based on available MCP tools
   */
  async getWitnesses(
    limit: number = 10
  ): Promise<{ success: boolean; witnesses?: VIFWitness[]; error?: string }> {
    try {
      // Try to get witnesses - this may need a different MCP tool
      // For now, return empty array as placeholder
      return {
        success: true,
        witnesses: []
      }
    } catch (error) {
      console.error('VIF getWitnesses error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error getting witnesses'
      }
    }
  }
}

// Singleton instance
export const vifService = new VIFService()

