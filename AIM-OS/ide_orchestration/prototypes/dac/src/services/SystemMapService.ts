/**
 * System Map Service
 * Loads system.map.lucid.json5 files from the backend
 */

// Use relative path so Vite proxy can route to backend on port 8000
const API_BASE_URL = ''

export interface SystemMap {
  systemId: string
  systemName: string
  version: string
  status: 'production' | 'development' | 'testing' | 'deprecated' | 'planned'
  layer?: number
  description?: string
  
  internalNodes?: Array<{
    id: string
    kind?: string
    responsibility: string
    status?: string
    must_never?: string[]
    perf_budget_ms?: number
    security_level?: string
  }>
  
  ports?: Array<{
    id: string
    name?: string
    kind?: 'input' | 'output' | 'bidirectional'
    protocol?: string
    security_level?: string
    description?: string
  }>
  
  internalEdges?: Array<{
    from: string
    to: string
    kind?: string
    description?: string
  }>
  
  externalEdges?: Array<{
    from: string
    to: string
    kind?: string
    protocol?: string
    description?: string
  }>
  
  dependencies?: string[]
  dependents?: string[]
}

export class SystemMapService {
  private apiBaseUrl: string
  private cache: Map<string, SystemMap[]> = new Map()
  private cacheExpiry: Map<string, number> = new Map()
  private readonly CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  constructor(apiBaseUrl: string = API_BASE_URL) {
    this.apiBaseUrl = apiBaseUrl
  }

  /**
   * Load all system maps from backend
   */
  async loadAllSystemMaps(): Promise<{ success: boolean; maps?: SystemMap[]; error?: string }> {
    const cacheKey = 'all'
    const cached = this.getCached(cacheKey)
    if (cached) {
      return { success: true, maps: cached }
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/system-maps`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.success && Array.isArray(data.maps)) {
        this.setCached(cacheKey, data.maps)
        return { success: true, maps: data.maps }
      } else if (Array.isArray(data)) { // Allow direct array response
        this.setCached(cacheKey, data)
        return { success: true, maps: data }
      } else {
        return {
          success: false,
          error: data.error || 'Invalid response format'
        }
      }
    } catch (error) {
      console.warn('API load failed:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Backend API not available. Please ensure the backend server is running on port 8000'
      }
    }
  }

  /**
   * Load a specific system map by ID
   */
  async loadSystemMap(systemId: string): Promise<{ success: boolean; map?: SystemMap; error?: string }> {
    const cacheKey = `system:${systemId}`
    const cached = this.getCached(cacheKey)
    if (cached && cached.length > 0) {
      return { success: true, map: cached[0] }
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/system-maps/${encodeURIComponent(systemId)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.success && data.map) {
        this.setCached(cacheKey, [data.map])
        return { success: true, map: data.map }
      } else {
        return {
          success: false,
          error: data.error || 'System map not found'
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Backend API not available. Please ensure the backend server is running on port 8000'
      }
    }
  }

  private getCached(key: string): SystemMap[] | undefined {
    const expiry = this.cacheExpiry.get(key)
    if (expiry && Date.now() < expiry) {
      return this.cache.get(key)
    }
    this.cache.delete(key)
    this.cacheExpiry.delete(key)
    return undefined
  }

  private setCached(key: string, data: SystemMap[]): void {
    this.cache.set(key, data)
    this.cacheExpiry.set(key, Date.now() + this.CACHE_TTL)
  }

  clearCache(): void {
    this.cache.clear()
    this.cacheExpiry.clear()
  }
}

export const systemMapService = new SystemMapService()

