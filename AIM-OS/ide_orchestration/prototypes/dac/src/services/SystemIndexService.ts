/**
 * System Index Service
 * Loads system.index.lucid.json5 files from the backend
 */

// Use relative path so Vite proxy can route to backend on port 8000
const API_BASE_URL = ''

export interface SystemIndex {
  systemId: string
  humanName: string
  version: string
  status: 'production' | 'development' | 'testing' | 'deprecated' | 'planned'
  layer?: number
  
  intent: {
    purpose: string
    must_not_regress: string[]
    why_it_exists: string
  }
  
  classification: {
    security_level: 'critical' | 'high' | 'medium' | 'low'
    perf_sensitivity: 'high' | 'medium' | 'low'
    ownership: 'core' | 'support' | 'integration' | 'meta'
    sideEffects: string[]
  }
  
  internalNodes: Array<{
    id: string
    responsibility: string
    must_never: string[]
    perf_budget_ms: number
    status: string
  }>
  
  integration_points?: Array<{
    system: string
    protocol: string
    what_is_exchanged: string[]
  }>
  
  connections?: Array<{
    viaPort: string
    direction: string
    connectsToSystemId: string
    protocol: string
    data: string[]
    security_level: string
    governanceRequired: boolean
  }>
  
  performance_summary?: {
    avg_latency_ms?: number
    throughput?: number
    resource_usage?: Record<string, number>
  }
  
  documentation_status?: {
    l0_complete: boolean
    l1_complete: boolean
    l2_complete: boolean
    l3_complete: boolean
    l4_complete: boolean
  }
  
  dependencies?: string[]
  
  lineage?: {
    parentSystemId: string | null
    childSystems: string[]
    maturity: string
  }
  
  systemMap?: {
    mapFile: string
  }
  
  foresight?: {
    predictedRisks: Array<{
      risk_id: string
      description: string
      likelihood: string
      blast_radius_if_real: string
      mitigation: string
      watchpoint: string
    }>
    killSwitch?: string
    emergencyProcedures?: string[]
  }
  
  lastUpdated?: string
  atlasHealth?: {
    undeclaredConnections: string[]
    performanceAlerts: string[]
    securityAlerts: string[]
  }
}

/**
 * System Index Service
 * Loads system indexes from backend API
 */
export class SystemIndexService {
  private commandServerUrl: string
  private cache: Map<string, SystemIndex[]> = new Map()
  private cacheExpiry: Map<string, number> = new Map()
  private readonly CACHE_TTL = 5 * 60 * 1000 // 5 minutes

        constructor(apiBaseUrl: string = API_BASE_URL) {
          this.commandServerUrl = apiBaseUrl
        }

  /**
   * Load all system indexes from backend
   */
  async loadAllSystemIndexes(): Promise<{ success: boolean; indexes?: SystemIndex[]; error?: string }> {
    const cacheKey = 'all'
    const cached = this.getCached(cacheKey)
    if (cached) {
      return { success: true, indexes: cached }
    }

    try {
      // Try to load via command server API
      const response = await fetch(`${this.commandServerUrl}/api/system-indexes`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        // Fallback: Try to load via file system (if running in Node context)
        return await this.loadFromFileSystem()
      }

      const data = await response.json()
      
      if (data.success && Array.isArray(data.indexes)) {
        const indexes = data.indexes as SystemIndex[]
        this.setCached(cacheKey, indexes)
        return { success: true, indexes }
      } else if (Array.isArray(data)) {
        // Direct array response
        this.setCached(cacheKey, data as SystemIndex[])
        return { success: true, indexes: data as SystemIndex[] }
      } else {
        return {
          success: false,
          error: data.error || 'Invalid response format'
        }
      }
    } catch (error) {
      console.warn('API load failed, trying file system fallback:', error)
      return await this.loadFromFileSystem()
    }
  }

  /**
   * Load system index for a specific system
   */
  async loadSystemIndex(systemId: string): Promise<{ success: boolean; index?: SystemIndex; error?: string }> {
    const cacheKey = systemId
    const cached = this.getCached(cacheKey)
    if (cached && cached.length > 0) {
      return { success: true, index: cached[0] }
    }

    try {
      const response = await fetch(`${this.commandServerUrl}/api/system-indexes/${encodeURIComponent(systemId)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        return await this.loadFromFileSystem(systemId)
      }

      const data = await response.json()
      
      if (data.success && data.index) {
        const index = data.index as SystemIndex
        this.setCached(cacheKey, [index])
        return { success: true, index }
      } else if (data.systemId) {
        // Direct object response
        const index = data as SystemIndex
        this.setCached(cacheKey, [index])
        return { success: true, index }
      } else {
        return {
          success: false,
          error: data.error || 'System index not found'
        }
      }
    } catch (error) {
      console.warn('API load failed, trying file system fallback:', error)
      return await this.loadFromFileSystem(systemId)
    }
  }

  /**
   * Fallback: Load from file system (for development or when API unavailable)
   * This uses a proxy endpoint or returns error
   */
  private async loadFromFileSystem(systemId?: string): Promise<{ success: boolean; indexes?: SystemIndex[]; index?: SystemIndex; error?: string }> {
    try {
      // Try to use a proxy endpoint that can read files
      // This is safer than trying to use import.meta.glob which can cause issues
      const endpoint = systemId 
        ? `${this.commandServerUrl}/api/system-indexes/${encodeURIComponent(systemId)}`
        : `${this.commandServerUrl}/api/system-indexes`
      
      try {
        const response = await fetch(endpoint, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            if (systemId && data.index) {
              return { success: true, index: data.index }
            } else if (data.indexes) {
              return { success: true, indexes: data.indexes }
            }
          }
        }
      } catch (fetchError) {
        // Fall through to error message
      }

      // If we get here, the API is not available
      return {
        success: false,
              error: 'Backend API not available. Please ensure the backend server is running on port 8000'
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to load from file system'
      }
    }
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear()
    this.cacheExpiry.clear()
  }

  /**
   * Get cached data if still valid
   */
  private getCached(key: string): SystemIndex[] | null {
    const expiry = this.cacheExpiry.get(key)
    if (expiry && Date.now() < expiry) {
      return this.cache.get(key) || null
    }
    return null
  }

  /**
   * Set cached data with expiry
   */
  private setCached(key: string, data: SystemIndex[]): void {
    this.cache.set(key, data)
    this.cacheExpiry.set(key, Date.now() + this.CACHE_TTL)
  }
}

// Export singleton instance
export const systemIndexService = new SystemIndexService()

