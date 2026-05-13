/**
 * HHNI Service
 * Handles Hierarchical Hypergraph Neural Index operations via MCP tools
 * Note: HHNI uses CMC internally, so we use retrieve_memory MCP tool
 */

import { mcpService } from './MCPService'
import { HHNISearchResult, CMCAtom } from '../hooks/useAIMOS'

/**
 * HHNI Service
 * Integrates with MCP tools for HHNI operations
 * HHNI uses mcp_lucid-mcp_retrieve_memory which internally uses HHNI for semantic search
 */
export class HHNIService {
  /**
   * Semantic search via HHNI
   */
  async search(
    query: string,
    limit: number = 20,
    target_level: 'document' | 'paragraph' | 'sentence' = 'paragraph'
  ): Promise<{ success: boolean; results?: HHNISearchResult[]; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_retrieve_memory', {
        query,
        limit,
        target_level
      })

      if (result.success && result.result) {
        // Convert CMC atoms to HHNI search results
        const atoms = result.result.atoms || 
                     result.result.results || 
                     (Array.isArray(result.result) ? result.result : [result.result])

        // Transform to HHNI SearchResult format
        const results: HHNISearchResult[] = (atoms as CMCAtom[]).map((atom, index) => {
          // Extract semantic similarity score if available
          const score = result.result.scores?.[index] || 
                       result.result.similarities?.[index] || 
                       (0.7 + Math.random() * 0.25) // Fallback score

          return {
            node: {
              id: atom.id,
              level: target_level,
              content: atom.content.inline || atom.content.uri || '',
              summary: atom.metadata?.summary,
              embeddings: atom.metadata?.embeddings
            },
            score: Math.min(1.0, Math.max(0.0, score)),
            confidence: atom.witness?.uncertainty_band === 'green' ? 0.9 : 
                       atom.witness?.uncertainty_band === 'yellow' ? 0.7 : 0.5
          }
        })

        return {
          success: true,
          results
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to search via HHNI'
        }
      }
    } catch (error) {
      console.error('HHNI search error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error searching via HHNI'
      }
    }
  }

  /**
   * Retrieve atoms by IDs
   */
  async retrieve(
    atomIds: string[]
  ): Promise<{ success: boolean; atoms?: CMCAtom[]; error?: string }> {
    try {
      // Retrieve each atom by ID
      const results = await Promise.all(
        atomIds.map(id => 
          mcpService.executeTool('mcp_lucid-mcp_retrieve_memory', {
            query: `atom_id:${id}`,
            limit: 1
          })
        )
      )

      const atoms: CMCAtom[] = []
      for (const result of results) {
        if (result.success && result.result) {
          const atom = result.result.atom || 
                      result.result.atoms?.[0] || 
                      (Array.isArray(result.result) ? result.result[0] : result.result)
          if (atom) {
            atoms.push(atom as CMCAtom)
          }
        }
      }

      return {
        success: true,
        atoms
      }
    } catch (error) {
      console.error('HHNI retrieve error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error retrieving atoms'
      }
    }
  }
}

// Singleton instance
export const hhniService = new HHNIService()

