/**
 * TCS Service
 * Handles Timeline Context System operations via MCP tools
 * Replaces mock data with real backend API calls
 */

import { mcpService } from './MCPService'
import { TCSTimelineEntry } from '../hooks/useAIMOS'

export interface AddTimelineEntryRequest {
  entry_type: string
  content: string
  metadata?: Record<string, any>
  context_index?: Record<string, any>
  summary?: string
}

/**
 * TCS Service
 * Integrates with MCP tools for TCS operations
 */
export class TCSService {
  /**
   * Add timeline entry
   */
  async addEntry(
    entry_type: string,
    content: string,
    metadata: Record<string, any> = {},
    context_index?: Record<string, any>,
    summary?: string
  ): Promise<{ success: boolean; entry?: TCSTimelineEntry; entry_id?: string; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_add_timeline_entry', {
        entry_type,
        content,
        metadata,
        context_index,
        summary
      })

      if (result.success && result.result) {
        const entry = result.result.entry || result.result
        const entry_id = result.result.entry_id || entry?.prompt_id || result.result.id

        return {
          success: true,
          entry: entry as TCSTimelineEntry,
          entry_id
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to add timeline entry'
        }
      }
    } catch (error) {
      console.error('TCS addEntry error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error adding timeline entry'
      }
    }
  }

  /**
   * Get timeline summary
   */
  async getSummary(
    limit: number = 10
  ): Promise<{ success: boolean; entries?: TCSTimelineEntry[]; error?: string }> {
    try {
      const result = await mcpService.executeTool('mcp_lucid-mcp_get_timeline_summary', {
        limit
      })

      if (result.success && result.result) {
        const entries = result.result.entries || 
                       result.result.summary || 
                       (Array.isArray(result.result) ? result.result : [result.result])

        return {
          success: true,
          entries: entries as TCSTimelineEntry[]
        }
      } else {
        return {
          success: false,
          error: result.error || 'Failed to get timeline summary'
        }
      }
    } catch (error) {
      console.error('TCS getSummary error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error getting timeline summary'
      }
    }
  }

  /**
   * Get timeline graph (if available)
   */
  async getTimelineGraph(): Promise<{ success: boolean; graph?: any; error?: string }> {
    try {
      // This may need a different MCP tool or implementation
      // For now, return empty graph as placeholder
      return {
        success: true,
        graph: { nodes: [], edges: [] }
      }
    } catch (error) {
      console.error('TCS getTimelineGraph error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error getting timeline graph'
      }
    }
  }
}

// Singleton instance
export const tcsService = new TCSService()

