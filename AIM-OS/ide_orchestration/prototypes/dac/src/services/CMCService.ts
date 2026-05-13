/**
 * CMC Service
 * Handles Context Memory Core operations via MCP tools
 * Replaces mock data with real backend API calls
 */

import { mcpService } from './MCPService'
import { CMCAtom } from '../hooks/useAIMOS'

export interface CMCStats {
  total_atoms: number
  total_size: number
  by_modality: {
    text: number
    code: number
    event: number
    tool: number
    cross_model: number
  }
  by_uncertainty_band: {
    green: number
    yellow: number
    red: number
  }
}

export interface StoreMemoryRequest {
  content: string
  tags?: Record<string, number>
  metadata?: Record<string, any>
  modality?: CMCAtom['modality']
}

export interface RetrieveMemoryRequest {
  query: string
  limit?: number
  tags?: Record<string, number>
}

/**
 * CMC Service
 * Integrates with MCP tools for CMC operations
 */
export class CMCService {
  /**
   * Store memory atom in CMC
   */
  async storeAtom(
    content: string,
    modality: CMCAtom['modality'] = 'text',
    tags: Record<string, number> = {},
    metadata: Record<string, any> = {}
  ): Promise<{ success: boolean; atom?: CMCAtom; atom_id?: string; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_store_memory', {
        content,
        tags,
        metadata,
        modality
      })

      if (result.success && result.result) {
        // Handle different response formats
        const atom = result.result.atom || result.result
        const atom_id = result.result.atom_id || atom?.id || result.result.id

        return {
          success: true,
          atom: atom as CMCAtom,
          atom_id
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to store memory'
        }
      }
    } catch (error) {
      console.error('CMC storeAtom error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error storing memory'
      }
    }
  }

  /**
   * Retrieve memory atoms from CMC/HHNI
   */
  async retrieveAtoms(
    query: string,
    limit: number = 10
  ): Promise<{ success: boolean; atoms?: CMCAtom[]; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_retrieve_memory', {
        query,
        limit
      })

      if (result.success && result.result) {
        // Handle different response formats
        const atoms = result.result.atoms || 
                     result.result.results || 
                     (Array.isArray(result.result) ? result.result : [result.result])

        return {
          success: true,
          atoms: atoms as CMCAtom[]
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to retrieve memory'
        }
      }
    } catch (error) {
      console.error('CMC retrieveAtoms error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error retrieving memory'
      }
    }
  }

  /**
   * Get CMC statistics
   */
  async getStats(): Promise<{ success: boolean; stats?: CMCStats; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_get_memory_stats', {})

      if (result.success && result.result) {
        return {
          success: true,
          stats: result.result as CMCStats
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to get memory stats'
        }
      }
    } catch (error) {
      console.error('CMC getStats error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error getting stats'
      }
    }
  }
}

// Singleton instance
export const cmcService = new CMCService()

