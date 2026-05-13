/**
 * Hierarchical Navigation Service
 * Loads HIERARCHICAL_NAVIGATION_INDEX.md from the backend
 */

// Use relative path so Vite proxy can route to backend on port 8000
const API_BASE_URL = ''

export interface HierarchicalNavigationFrontmatter {
  id?: string
  type?: string
  title?: string
  description?: string
  author?: string
  version?: string
  created?: string
  updated?: string
  tags?: string[]
  [key: string]: any
}

export interface HierarchicalNavigationResponse {
  success: boolean
  frontmatter: HierarchicalNavigationFrontmatter
  content: string
  file_path: string
}

export class HierarchicalNavigationService {
  private apiBaseUrl: string
  private cache: HierarchicalNavigationResponse | null = null
  private cacheExpiry: number = 0
  private readonly CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  constructor(apiBaseUrl: string = API_BASE_URL) {
    this.apiBaseUrl = apiBaseUrl
  }

  /**
   * Load HIERARCHICAL_NAVIGATION_INDEX from backend
   */
  async loadHierarchicalNavigation(): Promise<{ success: boolean; data?: HierarchicalNavigationResponse; error?: string }> {
    const cached = this.getCached()
    if (cached) {
      return { success: true, data: cached }
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/hierarchical-navigation`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json() as HierarchicalNavigationResponse
      
      if (data.success) {
        this.setCached(data)
        return { success: true, data }
      } else {
        return {
          success: false,
          error: 'Invalid response format'
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
   * Clear cache
   */
  clearCache(): void {
    this.cache = null
    this.cacheExpiry = 0
  }

  /**
   * Get cached data if still valid
   */
  private getCached(): HierarchicalNavigationResponse | null {
    if (this.cache && Date.now() < this.cacheExpiry) {
      return this.cache
    }
    return null
  }

  /**
   * Set cached data with expiry
   */
  private setCached(data: HierarchicalNavigationResponse): void {
    this.cache = data
    this.cacheExpiry = Date.now() + this.CACHE_TTL
  }
}

// Export singleton instance
export const hierarchicalNavigationService = new HierarchicalNavigationService()

