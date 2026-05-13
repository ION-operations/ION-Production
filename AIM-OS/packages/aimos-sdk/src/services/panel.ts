/**
 * Panel Service - Panel registration and management
 */

import { AIMOSClient } from '../client'
import { PanelDefinition } from '../types'

/**
 * Panel Service for dynamic panel registration
 */
export class PanelService {
  constructor(private client: AIMOSClient) {}

  /**
   * Register a panel definition
   * 
   * @param panel Panel definition
   */
  async register(panel: PanelDefinition): Promise<void> {
    await this.client.executeTool('store_memory', {
      content: JSON.stringify(panel),
      modality: 'json',
      tags: {
        type: 'panel_definition',
        panel_id: panel.id,
        app_id: this.client.getAppId() || 'unknown',
      },
      metadata: { panel_definition: panel },
    })
  }

  /**
   * List all registered panels
   * 
   * @returns Array of panel definitions
   */
  async list(): Promise<PanelDefinition[]> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: 'panel definitions',
      tags: { type: 'panel_definition' },
      limit: 100,
    })

    const panels: PanelDefinition[] = []
    for (const item of result.results || []) {
      try {
        const panelDef = item.metadata?.panel_definition || JSON.parse(item.content || '{}')
        if (panelDef && panelDef.id) {
          panels.push(panelDef)
        }
      } catch (e) {
        // Skip invalid panel definitions
        console.warn('Skipping invalid panel definition:', e)
      }
    }

    return panels
  }

  /**
   * Get panel by ID
   * 
   * @param panelId Panel ID
   * @returns Panel definition or null if not found
   */
  async getById(panelId: string): Promise<PanelDefinition | null> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: `panel ${panelId}`,
      tags: { type: 'panel_definition', panel_id: panelId },
      limit: 1,
    })

    const items = result.results || []
    if (items.length === 0) {
      return null
    }

    try {
      const panelDef = items[0].metadata?.panel_definition || JSON.parse(items[0].content || '{}')
      if (panelDef && panelDef.id) {
        return panelDef
      }
    } catch (e) {
      console.warn('Failed to parse panel definition:', e)
    }

    return null
  }
}

