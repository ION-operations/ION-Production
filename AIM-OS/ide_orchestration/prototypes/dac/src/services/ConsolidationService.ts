/**
 * Consolidation Service
 * Loads consolidation documents, system maps, and organization data
 */

// Use relative path so Vite proxy can route to backend on port 8000
const API_BASE_URL = ''

export interface ConsolidationDocument {
  id: string
  title: string
  path: string
  category: 'status' | 'map' | 'phase' | 'index' | 'summary'
  description?: string
  status?: 'complete' | 'in-progress' | 'planned'
  phase?: number
  content?: string  // Full document content (optional, for preview)
}

export interface SystemMapEntry {
  id: string
  name: string
  type: 'core' | 'enhancement' | 'integration' | 'utility' | 'sub-layer' | 'new-major'
  status: 'complete' | 'partial' | 'missing'
  integrations: number
  totalIntegrations: number
  description?: string
  path?: string
}

export interface IntegrationEntry {
  from: string
  to: string
  status: 'complete' | 'partial' | 'missing'
  type: string
  description?: string
}

export interface PhaseStatus {
  phase: number
  name: string
  status: 'complete' | 'in-progress' | 'pending'
  completion: number
  description: string
  documents?: string[]  // Related document paths
}

export interface ConsolidationStats {
  totalSystems: number
  completeSystems: number
  coreSystems: number
  integrationPercentage: number
  totalIntegrations: number
  totalPossibleIntegrations: number
  completePhases: number
  totalPhases: number
  totalDocuments: number
}

class ConsolidationService {
  /**
   * Load all consolidation documents
   */
  async loadConsolidationDocuments(): Promise<{
    success: boolean
    documents?: ConsolidationDocument[]
    error?: string
  }> {
    try {
      // Try to load from CONSOLIDATION_INDEX.md
      const indexResponse = await fetch(`${API_BASE_URL}/ide_orchestration/prototypes/dac/docs/CONSOLIDATION_INDEX.md`)
      
      if (!indexResponse.ok) {
        // Fallback to mock data if file not found
        return {
          success: true,
          documents: this.getMockDocuments(),
        }
      }

      const indexContent = await indexResponse.text()
      
      // Parse the index to extract document references
      const documents = this.parseConsolidationIndex(indexContent)
      
      return {
        success: true,
        documents,
      }
    } catch (error) {
      console.error('Failed to load consolidation documents:', error)
      // Fallback to mock data
      return {
        success: true,
        documents: this.getMockDocuments(),
      }
    }
  }

  /**
   * Load a specific consolidation document
   */
  async loadDocument(path: string): Promise<{
    success: boolean
    content?: string
    error?: string
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/${path}`)
      
      if (!response.ok) {
        return {
          success: false,
          error: `Failed to load document: ${response.statusText}`,
        }
      }

      const content = await response.text()
      
      return {
        success: true,
        content,
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to load document',
      }
    }
  }

  /**
   * Load system map data
   */
  async loadSystemMap(): Promise<{
    success: boolean
    systems?: SystemMapEntry[]
    error?: string
  }> {
    try {
      // Try to load from MASTER_INTEGRATION_MAP.md or system map files
      // For now, return mock data
      return {
        success: true,
        systems: this.getMockSystemMap(),
      }
    } catch (error) {
      console.error('Failed to load system map:', error)
      return {
        success: true,
        systems: this.getMockSystemMap(),
      }
    }
  }

  /**
   * Load phase status
   */
  async loadPhaseStatus(): Promise<{
    success: boolean
    phases?: PhaseStatus[]
    error?: string
  }> {
    try {
      // Try to load from phase documents
      // For now, return mock data
      return {
        success: true,
        phases: this.getMockPhases(),
      }
    } catch (error) {
      console.error('Failed to load phase status:', error)
      return {
        success: true,
        phases: this.getMockPhases(),
      }
    }
  }

  /**
   * Get consolidation statistics
   */
  async getStats(): Promise<{
    success: boolean
    stats?: ConsolidationStats
    error?: string
  }> {
    try {
      const [systemsResult, phasesResult, docsResult] = await Promise.all([
        this.loadSystemMap(),
        this.loadPhaseStatus(),
        this.loadConsolidationDocuments(),
      ])

      if (!systemsResult.success || !phasesResult.success || !docsResult.success) {
        return {
          success: false,
          error: 'Failed to load data for statistics',
        }
      }

      const systems = systemsResult.systems || []
      const phases = phasesResult.phases || []
      const documents = docsResult.documents || []

      const totalSystems = systems.length
      const completeSystems = systems.filter(s => s.status === 'complete').length
      const coreSystems = systems.filter(s => s.type === 'core').length
      const totalIntegrations = systems.reduce((sum, s) => sum + s.integrations, 0)
      const totalPossibleIntegrations = systems.reduce((sum, s) => sum + s.totalIntegrations, 0)
      const integrationPercentage = totalPossibleIntegrations > 0
        ? Math.round((totalIntegrations / totalPossibleIntegrations) * 100)
        : 0

      const completePhases = phases.filter(p => p.status === 'complete').length
      const totalPhases = phases.length

      return {
        success: true,
        stats: {
          totalSystems,
          completeSystems,
          coreSystems,
          integrationPercentage,
          totalIntegrations,
          totalPossibleIntegrations,
          completePhases,
          totalPhases,
          totalDocuments: documents.length,
        },
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to calculate statistics',
      }
    }
  }

  /**
   * Parse CONSOLIDATION_INDEX.md to extract document references
   */
  private parseConsolidationIndex(content: string): ConsolidationDocument[] {
    const documents: ConsolidationDocument[] = []
    
    // Simple regex to find markdown links with paths
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g
    const lines = content.split('\n')
    
    let currentCategory: ConsolidationDocument['category'] | null = null
    let currentSection = ''
    
    for (const line of lines) {
      // Detect category sections
      if (line.includes('### **Status & Overview:**')) {
        currentCategory = 'status'
        currentSection = 'status'
      } else if (line.includes('### **System Maps:**')) {
        currentCategory = 'map'
        currentSection = 'map'
      } else if (line.includes('### **Planning:**')) {
        currentCategory = 'phase'
        currentSection = 'planning'
      } else if (line.includes('### **Team Coordination:**')) {
        currentCategory = 'index'
        currentSection = 'team'
      } else if (line.includes('### **Phase Documents:**')) {
        currentCategory = 'phase'
        currentSection = 'phase'
      }
      
      // Extract document links
      const matches = [...line.matchAll(linkRegex)]
      for (const match of matches) {
        const title = match[1].replace(/\*\*/g, '').replace(/⭐/g, '').trim()
        const path = match[2]
        
        if (path.endsWith('.md') && currentCategory) {
          // Extract ID from path
          const id = path.split('/').pop()?.replace('.md', '') || title.toLowerCase().replace(/\s+/g, '-')
          
          // Determine status from title or context
          let status: ConsolidationDocument['status'] = 'complete'
          if (title.toLowerCase().includes('complete')) {
            status = 'complete'
          } else if (title.toLowerCase().includes('status') || title.toLowerCase().includes('current')) {
            status = 'in-progress'
          }
          
          // Extract phase number if in phase section
          let phase: number | undefined
          const phaseMatch = title.match(/phase\s*(\d+)/i)
          if (phaseMatch) {
            phase = parseInt(phaseMatch[1], 10)
          }
          
          documents.push({
            id,
            title,
            path: `ide_orchestration/prototypes/dac/docs/${path}`,
            category: currentCategory,
            status,
            phase,
          })
        }
      }
    }
    
    return documents
  }

  /**
   * Mock data fallback
   */
  private getMockDocuments(): ConsolidationDocument[] {
    return [
      { id: 'achievements', title: 'Consolidation Achievements', path: 'docs/CONSOLIDATION_ACHIEVEMENTS.md', category: 'status', status: 'complete' },
      { id: 'complete-summary', title: 'Consolidation Complete Summary', path: 'docs/CONSOLIDATION_COMPLETE_SUMMARY.md', category: 'summary', status: 'complete' },
      { id: 'final-status', title: 'Final Consolidation Status', path: 'docs/FINAL_CONSOLIDATION_STATUS.md', category: 'status', status: 'complete' },
      { id: 'master-system-map', title: 'Master System Map', path: 'docs/MASTER_SYSTEM_MAP.md', category: 'map', status: 'complete' },
      { id: 'integration-map', title: 'Master Integration Map', path: 'docs/MASTER_INTEGRATION_MAP.md', category: 'map', status: 'complete' },
      { id: 'system-hierarchy', title: 'Final System Hierarchy', path: 'docs/FINAL_SYSTEM_HIERARCHY.md', category: 'map', status: 'complete' },
      { id: 'phase4-complete', title: 'Phase 4 Complete', path: 'docs/PHASE4_COMPLETE.md', category: 'phase', phase: 4, status: 'complete' },
      { id: 'phase5-complete', title: 'Phase 5 Complete', path: 'docs/PHASE5_COMPLETE.md', category: 'phase', phase: 5, status: 'complete' },
      { id: 'phase6-status', title: 'Phase 6 Status', path: 'docs/PHASE6_CURRENT_STATUS.md', category: 'phase', phase: 6, status: 'in-progress' },
      { id: 'consolidation-index', title: 'Consolidation Index', path: 'docs/CONSOLIDATION_INDEX.md', category: 'index', status: 'complete' },
    ]
  }

  private getMockSystemMap(): SystemMapEntry[] {
    return [
      { id: 'cmc', name: 'CMC', type: 'core', status: 'complete', integrations: 7, totalIntegrations: 7, description: 'Context Memory Core' },
      { id: 'hhni', name: 'HHNI', type: 'core', status: 'complete', integrations: 7, totalIntegrations: 7, description: 'Hierarchical Hypergraph Neural Index' },
      { id: 'vif', name: 'VIF', type: 'core', status: 'complete', integrations: 6, totalIntegrations: 7, description: 'Verifiable Intelligence Framework' },
      { id: 'apoe', name: 'APOE', type: 'core', status: 'complete', integrations: 6, totalIntegrations: 7, description: 'AI-Powered Orchestration Engine' },
      { id: 'seg', name: 'SEG', type: 'core', status: 'complete', integrations: 7, totalIntegrations: 7, description: 'Shared Evidence Graph' },
      { id: 'cas', name: 'CAS', type: 'core', status: 'complete', integrations: 5, totalIntegrations: 7, description: 'Cognitive Analysis System' },
      { id: 'tcs', name: 'TCS', type: 'core', status: 'complete', integrations: 7, totalIntegrations: 7, description: 'Timeline Context System' },
      { id: 'router', name: 'Router', type: 'enhancement', status: 'complete', integrations: 3, totalIntegrations: 5, description: 'Router system' },
      { id: 'prompt-chain', name: 'Prompt Chain Executor', type: 'enhancement', status: 'complete', integrations: 2, totalIntegrations: 3, description: 'Prompt chain execution' },
      { id: 'confidence-gated', name: 'Confidence Gated Controls', type: 'enhancement', status: 'complete', integrations: 3, totalIntegrations: 3, description: 'Confidence-gated controls' },
    ]
  }

  private getMockPhases(): PhaseStatus[] {
    return [
      { phase: 1, name: 'Mapping and Gap Analysis', status: 'complete', completion: 100, description: 'Mapped all packages, identified gaps' },
      { phase: 2, name: 'Document Missing Packages', status: 'complete', completion: 100, description: 'Created T0-T1 documentation' },
      { phase: 3, name: 'Team Coordination and Classification', status: 'complete', completion: 100, description: 'Classified all systems' },
      { phase: 4, name: 'Integration Verification (MVP)', status: 'complete', completion: 100, description: 'Verified all MVP systems' },
      { phase: 5, name: 'Integration Implementation', status: 'complete', completion: 100, description: 'Implemented all partial integrations' },
      { phase: 6, name: 'Integration Testing', status: 'in-progress', completion: 100, description: 'Test code complete, ready for execution' },
    ]
  }
}

// Export singleton instance
export const consolidationService = new ConsolidationService()

